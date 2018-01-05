import sys
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication, QMessageBox

class KFOpenAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl("KFOPENAPI.KFOpenAPICtrl.1")
        self.loginLoop = None
        self.requestLoop = None
        self.orderLoop = None
        self.error = None
        self.orderNo = ""
        self.inquiry = 0
        self.msg = ""
        self.screenNo = 1000
        self.dicScrNo = {}
        self.OnReceiveTrData.connect(self.ReceiveTrData)
        self.OnReceiveRealData.connect(self.ReceiveRealData)
        self.OnReceiveMsg.connect(self.ReceiveMsg)
        self.OnReceiveChejanData.connect(self.ReceiveChejanData)
        self.OnEventConnect.connect(self.EventConnect)
        print("Initialized Kiwoom OpenAPI-W")


    ###############################################################
    # Method
    ###############################################################

    def CommConnect(self):
        """
        1) CommConnect
        원형    LONG CommConnect(LONG nAutoUpgrade)
        설명    로그인 윈도우를 실행한다.
        입력값  0 – 버전 수동처리, 1 – 버전 자동처리
                *로그인창 및 OCX 파일을 버전처리 받는 경우에,
                수동처리시, 고객 프로그램(ocx포함)을 직접 수동으로 Close하고 버전처리 진행
                자동처리시, 고객 프로그램(ocx포함)을 자동으로 Close하고 버전처리 및 자동
                재실행을 함.
        반환값  0 - 성공, 음수값은 실패
        비고    로그인이 성공하거나 실패하는 경우 OnEventConnect 이벤트가 발생하고
                이벤트의 인자 값으로 로그인 성공 여부를 알 수 있다.
                구분자 자동여부는 고객 프로그램(ocx포함)이 단독으로 사용되어지는 경우에,
                구분자를 자동으로 선택하시고, 고객 프로그램(ocx포함)이 다른프로그램과
                연동되어져 실행시 데이터를 수신해야하는 경우에는 구분자를 수동으로 선택.
        """
        self.dynamicCall("CommConnect(1)")
        self.loginEventLoop = QEventLoop()
        self.loginEventLoop.exec_()

    def CommRqData(self, sRQName, sTrCode, sPrevNext, sScreenNo):
        """
        2) CommRqData
        원형    LONG CommRqData (BSTR sRQName, BSTR sTrCode, BSTR sPrevNext, BSTR sScreenNo )
        설명    Tran을 서버로 송신한다.
        입력값  BSTR sRQName  BSTR sTrCode  long nPrevNext  BSTR sScreenNo
        반환값  OP_ERR_SISE_OVERFLOW – 과도한 시세조회로 인한 통신불가
                OP_ERR_RQ_STRUCT_FAIL – 입력 구조체 생성 실패
                OP_ERR_RQ_STRING_FAIL – 요청전문 작성 실패
                OP_ERR_NONE – 정상처리
        비고    sRQName – 사용자구분 명
                sTrCode - Tran명 입력
                nPrevNext – 서버에서 내려준 Next키값 입력(샘플참조)
                sScreenNo - 4자리의 화면번호(1~9999 :숫자값으로만 가능)
                Ex) openApi.CommRqData( “RQ_1”, “OPT00001”, “”, “0101”);
        """
        if not self.GetConnectState():
            print("Error : KiwoomConnectError by CommRqData")
            raise KiwoomConnectError()

        if not (isinstance(sRQName, str)
                and isinstance(sTrCode, str)
                and isinstance(sPrevNext, str)
                and isinstance(sScreenNo, str)):
            print("Error : ParameterTypeError by CommRqData")
            raise ParameterTypeError()

        errorCode = self.dynamicCall('CommRqData(QString, QString, QString, QString)', sRQName, sTrCode, sPrevNext, sScreenNo)
        if errorCode != ErrorCode.OP_ERR_NONE:
            raise KiwoomProcessingError("CommRqData(): " + ErrorCode.CAUSE[errorCode])
        else:
            self.requestLoop = QEventLoop()
            self.requestLoop.exec_()


    def SetInputValue(self, sID, sValue):
        """
        3) SetInputValue
        원형    void SetInputValue(BSTR sID, BSTR sValue)
        설명    Tran 입력 값을 서버통신 전에 입력한다.
        입력값  sID – 아이템명  sValue – 입력 값
        반환값  없음
        비고    통신 Tran 매뉴얼 참고
                Ex) openApi.SetInputValue(“종목코드”, “6AH16”);
                openApi.SetInputValue(“계좌번호”, “5015123401”);
        """
        if not (isinstance(sID, str) and isinstance(sValue, str)):
            print("Error : ParameterTypeError by SetInputValue")
            raise ParameterTypeError()

        self.dynamicCall("SetInputValue(QString, QString)", sID, sValue)

    def GetCommData(self, strTrCode, strRecordName, nIndex, strItemName):
        """
        4) GetCommData
        원형    BSTR GetCommData(BSTR strTrCode, BSTR strRecordName, long nIndex, BSTR strItemName)
        설명    수신 데이터를 반환한다.
        입력값  strTrCode – Tran 코드
                strRecordName – 레코드명
                nIndex – 복수데이터 인덱스
                strItemName – 아이템명
        반환값  수신 데이터
        비고    Ex)현재가출력 - openApi.GetCommData(“OPT00001”, “해외선물기본정보”, 0, “현재가”);
        """
        if not (isinstance(strTrCode, str)
                and isinstance(strRecordName, str)
                and isinstance(nIndex, int)
                and isinstance(strItemName, str)):
            print("Error : ParameterTypeError by GetCommData")
            raise ParameterTypeError()

        return self.dynamicCall("GetCommData(QString, QString, int, QString)", strTrCode, strRecordName, nIndex, strItemName).strip()

    def CommTerminate(self):
        """
        5) CommTerminate
        원형    void CommTerminate()
        설명    OpenAPI의 서버 접속을 해제한다.
        입력값  없음
        반환값  없음
        비고    통신 연결 상태는 GetConnectState 메소드로 알 수 있다.
        """
        self.dynamicCall("CommTerminate()")

    def GetRepeatCnt(self, sTrCode, sRecordName):
        """
        6) GetRepeatCnt
        원형    LONG GetRepeatCnt(BSTR sTrCode, BSTR sRecordName)
        설명    레코드 반복횟수를 반환한다.
        입력값  sTrCode – Tran 명
                sRecordName – 레코드 명
        반환값  레코드의 반복횟수
        비고    Ex) openApi.GetRepeatCnt(“OPT00001”, “해외선물체결데이타”);
        """
        if not (isinstance(sTrCode, str) and isinstance(sRecordName, str)):
            print("Error : ParameterTypeError by GetRepeatCnt")
            raise ParameterTypeError()

        return self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRecordName)

    def DisconnectRealData(self, sScrNo):
        """
        7) DisconnectRealData
        원형    void DisconnectRealData(BSTR sScnNo)
        설명    화면 내 모든 리얼데이터 요청을 제거한다.
        입력값  sScrNo – 화면번호[4]
        반환값  없음
        비고    화면을 종료할 때 반드시 위 함수를 호출해야 한다.
                Ex) openApi.DisconnectRealData(“0101”);
        """
        if not (isinstance(sScrNo, str)):
            print("Error : ParameterTypeError by DisconnectRealData")
            raise ParameterTypeError()

        self.dynamicCall("DisconnectRealData(QString)", sScrNo)

    def GetCommRealData(self, strRealType, nFid):
        """
        8) GetCommRealData
        원형    BSTR GetCommRealData(BSTR strRealType, long nFid)
        설명    실시간데이터를 반환한다.
        입력값  strRealType – 실시간 구분
                nFid – 실시간 아이템
        반환값  수신 데이터
        비고    Ex) 현재가출력 - openApi.GetCommRealData(“해외선물시세”, 10);
        """
        if not (isinstance(strRealType, str) and isinstance(nFid, int)):
            print("Error : ParameterTypeError by GetCommRealData")
            raise ParameterTypeError()

        return self.dynamicCall("GetCommRealData(QString, int)", strRealType, nFid)

    def GetChejanData(self, nFid):
        """
        9) GetChejanData
        원형    BSTR GetChjanData(long nFid)
        설명    체결잔고 데이터를 반환한다.
        입력값  nFid – 체결잔고 아이템
        반환값  수신 데이터
        비고    Ex) 현재가출력 – openApi.GetChejanData(910); //체결가격
        """
        if not (isinstance(nFid, int)):
            print("Error : ParameterTypeError by GetChejanData")
            raise ParameterTypeError()

        return self.dynamicCall("GetChjanData(int)", nFid)

    def SendOrder(self, sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, sPrice, sStop, sHogaGb, sOrgOrderNo):
        """
        10) SendOrder
        원형    LONG SendOrder(BSTR sRQName, BSTR sScreenNo, BSTR sAccNo, LONG nOrderType, BSTR sCode, LONG nQty,
                BSTR sPrice, BSTR sStop, BSTR sHogaGb, BSTR sOrgOrderNo  )
        설명    주문을 서버로 전송한다.
        입력값  sRQName - 사용자 구분 요청 명
                sScreenNo - 화면번호[4] (1~9999 :숫자값으로만 가능)
                sAccNo - 계좌번호[10]
                nOrderType - 주문유형 (1:신규매도, 2:신규매수, 3:매도취소, 4:매수취소, 5:매도정정, 6:매수정정)
                sCode  - 종목코드
                nQty – 주문수량
                sPrice – 주문단가
                sStop - Stop단가
                sHogaGb - 거래구분
                sOrgOrderNo – 원주문번호
        반환값  에러코드 <7.에러코드표 참고>
        비고    sHogaGb – 1:시장가, 2:지정가, 3:STOP, 4:STOP LIMIT
                ex) 지정가 매수 - openApi.SendOrder(“RQ_1”, “0101”, “5015123410”, 2, “6AH16”, 10, “0.7900”, “2”, “”);
                    시장가 매수 - openApi.SendOrder(“RQ_1”, “0101”, “5015123410”, 2, “6AH16”, 10, “0”, “1”, “”);
                    매수 정정 - openApi.SendOrder(“RQ_1”,“0101”, “5015123410”, 6, “6AH16”, 10, “0.7800”, “0”, “200060”);
                    매수 취소 - openApi.SendOrder(“RQ_1”, “0101”, “5015123410”, 4, “6AH16”, 10, “0”, “0”, “200061”);
        """
        if not self.getConnectState():
            print("Error : KiwoomConnectError by SendOrder")
            raise KiwoomConnectError()

        if not (isinstance(sRQName, str)
                and isinstance(sScreenNo, str)
                and isinstance(sAccNo, str)
                and isinstance(nOrderType, int)
                and isinstance(sCode, str)
                and isinstance(nQty, int)
                and isinstance(sPrice, str)
                and isinstance(sStop, str)
                and isinstance(sHogaGb, str)
                and isinstance(sOrgOrderNo, str)):
            print("Error : ParameterTypeError by SendOrder")
            raise ParameterTypeError()

        ErrorCode = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, QString, QString, QString, QString)",
                                    sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, sPrice, sStop, sHogaGb, sOrgOrderNo)

        if ErrorCode != ErrorCode.OP_ERR_NONE:
            raise KiwoomProcessingError("sendOrder(): " + ErrorCode.CAUSE[ErrorCode])

        self.orderLoop = QEventLoop()
        self.orderLoop.exec_()

    def GetLoginInfo(self, sTag):
        """
        11) GetLoginInfo
        원형    BSTR GetLoginInfo(BSTR sTag)
        설명    로그인한 사용자 정보를 반환한다.
        입력값  BSTR sTag : 사용자 정보 구분 TAG값 (비고)
        반환값  TAG값에 따른 데이터 반환
        비고    BSTR sTag에 들어 갈 수 있는 값은 아래와 같음
                “ACCOUNT_CNT” – 전체 계좌 개수를 반환한다.
                "ACCNO" – 전체 계좌를 반환한다. 계좌별 구분은 ‘;’이다.
                “USER_ID” - 사용자 ID를 반환한다.
                “USER_NAME” – 사용자명을 반환한다.
                “KEY_BSECGB” – 키보드보안 해지여부. 0:정상, 1:해지
                “FIREW_SECGB” – 방화벽 설정 여부. 0:미설정, 1:설정, 2:해지
                Ex) openApi.GetLoginInfo(“ACCOUNT_CNT”);
        """
        if not self.GetConnectState():
            print("Error : KiwoomConnectError by GetLoginInfo")
            raise KiwoomConnectError()

        if not isinstance(sTag, str):
            print("Error : ParameterTypeError by GetLoginInfo")
            raise ParameterTypeError()

        if sTag not in ["ACCOUNT_CNT", "ACCNO", "USER_ID", "USER_NAME", "GetServerGubun"]:
            print("Error : ParameterValueError by GetLoginInfo")
            raise ParameterValueError()

        return self.dynamicCall("GetLoginInfo(QString)", sTag)

    def GetGlobalFutureItemlist(self):
        """
        12) GetGlobalFutureItemlist
        원형    BSTR GetGlobalFutureItemlist()
        설명    해외선물 상품리스트를 반환한다.
        입력값  없음
        반환값  해외선물 상품리스트, 상품간 구분은 ‘;’이다.
        비고    해외선물 상품리스트(6A, 6B, 6C, ES…..)
        """
        return self.dynamicCall("GetGlobalFutureItemlist()")

    def GetGlobalOptionItemlist(self):
        """
        13) GetGlobalOptionItemlist
        원형 BSTR GetGlobalOptionItemlist()
        설명 해외옵션 상품리스트를 반환한다.
        입력값 없음
        반환값 해외옵션 상품리스트, 상품간 구분은 ‘;’이다.
        비고 해외옵션 상품리스트(6A, 6B, 6C, ES…..)
        """
        return self.dynamicCall("GetGlobalOptionItemlist()")

    def GetGlobalFutureCodelist(self, sItem):
        """
        14) GetGlobalFutureCodelist
        원형    BSTR GetGlobalFutureCodelist(BSTR sItem)
        설명    해외상품별 해외선물 종목코드리스트를 반환한다.
        입력값  해외상품
        반환값  해외선물 종목코드리스트, 종목간 구분은 ‘;’이다.
        비고    해외선물 종목코드리스트
        """
        if not (isinstance(sItem, str)):
            print("Error : ParameterTypeError by GetGlobalFutureCodelist")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalFutureCodelist(QString)", sItem)

    def GetGlobalOptionCodelist(self, sItem):
        """
        15) GetGlobalOptionCodelist
        원형    BSTR GetGlobalOptionCodelist(BSTR sItem)
        설명    해외상품별 해외선물 종목코드리스트를 반환한다.
        입력값  해외상품
        반환값  해외옵션 종목코드리스트, 종목간 구분은 ‘;’이다.
        비고    해외옵션 종목코드리스트
        """
        if not (isinstance(sItem, str)):
            print("Error : ParameterTypeError by GetGlobalOptionCodelist")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalOptionCodelist(QString)", sItem)

    def GetConnectState(self):
        """
        16) GetConnectState
        원형    LONG GetConnectState()
        설명    현재접속상태를 반환한다.
        입력값  없음
        반환값  접속상태
        비고    0:미연결, 1:연결완료
        """
        return self.dynamicCall("GetConnectState()")

    def GetAPIModulePath(self):
        """
        17) GetAPIModulePath
        원형    BSTR GetAPIModulePath()
        설명    OpenAPI모듈의 경로를 반환한다.
        입력값  없음
        반환값  경로
        비고
        """
        return self.dynamicCall("GetAPIModulePath()")

    def GetCommonFunc(self, sFuncName, sParam):
        """
        18) GetCommonFunc
        원형    BSTR GetCommonFunc(BSTR sFuncName, BSTR sParam)
        설명    공통함수로 추후 추가함수가 필요시 사용할 함수이다.
        입력값  함수명, 인자값
        반환값  문자값으로 반환한다.
        비고
        """
        if not (isinstance(sFuncName, str)
                and isinstance(sParam, str)):
            print("Error : ParameterTypeError by GetCommonFunc")
            raise ParameterTypeError()

        return self.dynamicCall("GetCommonFunc(QString, QString)", sFuncName, sParam)

    def GetConvertPrice(self, sCode, sPrice, nType):
        """
        19) GetConvertPrice
        원형    BSTR GetConvertPrice(BSTR sCode, BSTR sPrice, LONG nType)
        설명    가격 진법에 따라 변환된 가격을 반환한다.
        입력값  종목코드, 가격, 타입(0 : 진법->10진수, 1 : 10진수->진법)
        반환값  문자값으로 반환한다.
        비고
        """
        if not (isinstance(sCode, str)
                and isinstance(sPrice, str)
                and isinstance(nType, str)):
            print("Error : ParameterTypeError by GetConvertPrice")
            raise ParameterTypeError()

        return self.dynamicCall("GetConvertPrice(QString, QString, int)", sCode, sPrice, nType)

    def GetGlobalFutOpCodeInfoByType(self, nGubun, sType):
        """
        20) GetGlobalFutOpCodeInfoByType
        원형    BSTR GetGlobalFutCodeInfoByType(LONG nGubun, BSTR sType)
        설명    해외선물옵션종목코드정보를 타입별로 반환한다.
        입력값  nGubun : 0(해외선물), 1(해외옵션)
                sType : IDX(지수), CUR(통화), INT(금리), MLT(금속), ENG(에너지), CMD(농산물)
        반환값  종목코드정보리스트들을 문자값으로 반환한다.(아래 종목마스터파일 참조)
        비고    전체는 “”으로 보내면 된다.
        """
        if not (isinstance(nGubun, int)
                and isinstance(sType, str)):
            print("Error : ParameterTypeError by GetGlobalFutOpCodeInfoByType")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalFutOpCodeInfoByType(int, QString)", nGubun, sType)

    def GetGlobalFutOpCodeInfoByCode(self, sCode):
        """
        21) GetGlobalFutOpCodeInfoByCode
        원형    BSTR GetGlobalFutCodeInfoByCode(BSTR sCode)
        설명    해외선물옵션종목코드정보를 종목코드별로 반환한다.
        입력값  sCode : 해외선물옵션 종목코드 입력
        반환값  종목코드정보를 문자값으로 반환한다.(아래 종목마스터파일 참조)
        비고
        """
        if not (isinstance(sCode, str)):
            print("Error : ParameterTypeError by GetGlobalFutOpCodeInfoByCode")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalFutOpCodeInfoByCode(QString)", sCode)

    def GetGlobalFutureItemlistByType(self, sType):
        """
        22) GetGlobalFutureItemlistByType
        원형    BSTR GetGlobalFutureItemlistByType (BSTR sType)
        설명    해외선물상품리스트를 타입별로 반환한다.
        입력값  sType : IDX(지수), CUR(통화), INT(금리), MLT(금속), ENG(에너지), CMD(농산물)
        반환값  상품리스트를 문자값으로 반환한다.
        비고
        """
        if not (isinstance(sType, str)):
            print("Error : ParameterTypeError by GetGlobalFutureItemlistByType")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalFutureItemlistByType(QString)", sType)

    def GetGlobalFutureCodeByItemMonth(self, sItem, sMonth):
        """
        23) GetGlobalFutureCodeByItemMonth
        원형    BSTR GetGlobalFutureCodeByItemMonth(BSTR sItem, BSTR sMonth)
        설명    해외선물종목코드를 상품/월물별로 반환한다.
        입력값  sItem: 상품코드(6A, ES..),
                sMonth: “201606”
        반환값  종목코드를 문자값으로 반환한다.
        비고
        """
        if not (isinstance(sItem, str)
                and isinstance(sMonth, str)):
            print("Error : ParameterTypeError by GetGlobalFutureCodeByItemMonth")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalFutureCodeByItemMonth(QString, QString)", sItem, sMonth)

    def GetGlobalOptionCodeByMonth(self, sItem, sCPGubun, sActPrice, sMonth):
        """
        24) GetGlobalOptionCodeByMonth
        원형    BSTR GetGlobalOptionCodeByMonth(BSTR sItem, BSTR sCPGubun, BSTR sActPrice, BSTR sMonth)
        설명    해외옵션종목코드를 상품/콜풋/행사가/월물별로 반환한다.
        입력값  sItem: 상품코드(6A, ES..),
                sCPGubun: C(콜)/P(풋), sActPrice: 0.760,
                sMonth: “201606”
        반환값  종목코드를 문자값으로 반환한다.
        비고
        """
        if not (isinstance(sItem, str)
                and isinstance(sCPGubun, str)
                and isinstance(sActPrice, str)
                and isinstance(sMonth, str)):
            print("Error : ParameterTypeError by GetGlobalOptionCodeByMonth")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalOptionCodeByMonth(QString, QString, QString, QString)", sItem, sCPGubun, sActPrice, sMonth)

    def GetGlobalOptionMonthByItem(self, sItem):
        """
        25) GetGlobalOptionMonthByItem
        원형    BSTR GetGlobalOptionMonthByItem(BSTR sItem)
        설명    해외옵션월물리스트를 상품별로 반환한다.
        입력값  sItem: 상품코드(6A, ES..)
        반환값  월물리스트를 문자값으로 반환한다.
        비고
        """
        if not (isinstance(sItem, str)):
            print("Error : ParameterTypeError by GetGlobalOptionMonthByItem")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalOptionMonthByItem(QString", sItem)

    def GetGlobalOptionActPriceByItem(self, sItem):
        """
        26) GetGlobalOptionActPriceByItem
        원형    BSTR GetGlobalOptionActPriceByItem(BSTR sItem)
        설명    해외옵션행사가리스트를 상품별로 반환한다.
        입력값  sItem: 상품코드(6A, ES..)
        반환값  행사가리스트를 문자값으로 반환한다.
        비고
        """
        if not (isinstance(sItem, str)):
            print("Error : ParameterTypeError by GetGlobalOptionActPriceByItem")
            raise ParameterTypeError()

        return self.dynamicCall("GetGlobalOptionActPriceByItem(QString", sItem)

    def GetGlobalFutureItemTypelist(self):
        """
        27) GetGlobalFutureItemTypelist
        원형    BSTR GetGlobalFutureItemTypelist()
        설명    해외선물상품타입리스트를 반환한다.
        입력값  없음
        반환값  상품타입리스트를 문자값으로 반환한다.
        비고    IDX;CUR;INT;MLT;ENG;CMD;  반환
        """
        return self.dynamicCall("GetGlobalFutureItemTypelist()")

    def GetCommFullData(self, strTrCode, strRecordName):
        """
        28) GetCommFullData
        원형    BSTR GetCommFullData(BSTR strTrCode, BSTR strRecordName, LONG nGubun )
        설명    수신된 전체데이터를 반환한다.
        입력값  strTrCode – Tran 코드
                strRecordName – 레코드명
                nGubun–  0 : 전체(싱글+멀티),  1 : 싱글데이타, 2 : 멀티데이타
        반환값  수신 전체데이터를 문자값으로 반환한다.
        비고    WKOAStudio의 TR목록탭에서 필드 사이즈 참조.(필드명 옆 가로안의 값들)
                모든 시세/원장 조회에 사용 가능하며, 특히 차트데이타 같은 대용량 데이터를
                한번에 받아서 처리가능.
        """
        if not (isinstance(strTrCode, str)
                and isinstance(strRecordName, str)):
            print("Error : ParameterTypeError by GetCommFullData")
            raise ParameterTypeError()

        return self.dynamicCall("GetCommFullData(QString, QString", strTrCode, strRecordName)

    def GetScreenNumber(self):
        ret = "{0:04d}".format(self.screenNo)
        if self.screenNo == 9999:
            raise MaxScreenNumber()
        self.dicScrNo.update({ret:self.screenNo})
        self.screenNo += 1
        return ret

    ###############################################################
    # Event
    # 각종 수신 Event를 처리
    ###############################################################

    # OnReceiveTrData
    def ReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        """
        1) OnReceiveTrData
        원형    void OnReceiveTrData(BSTR sScrNo, BSTR sRQName, BSTR sTrCode, BSTR sRecordName, BSTR sPreNext)
        설명    서버통신 후 데이터를 받은 시점을 알려준다.
        입력값  sScrNo – 화면번호
                sRQName – 사용자구분 명
                sTrCode – Tran 명
                sRecordName – Record 명
                sPreNext – 연속조회 유무
        반환값  없음
        비고    sRQName – CommRqData의 sRQName과 매핑되는 이름이다.
                sTrCode – CommRqData의 sTrCode과 매핑되는 이름이다.
        """
        print("OnReceiveTrData")
        self.requestLoop.exit()

    # OnReceiveRealData
    def ReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        """
        2) OnReceiveRealData
        원형    void OnReceiveRealData(BSTR sJongmokCode, BSTR sRealType, BSTR sRealData)
        설명    실시간데이터를 받은 시점을 알려준다.
        입력값  sJongmokCode – 종목코드
                sRealType – 리얼타입
                sRealData – 실시간 데이터전문
        반환값  없음
        비고
        """
        print("OnReceiveRealData")

    # OnReceiveMsg
    def ReceiveMsg(self, sScrNo, sRQName, sTrCode, sMsg):
        """
        3) OnReceiveMsg
        원형    void OnReceiveMsg(BSTR sScrNo BSTR sRQName, BSTR sTrCode, BSTR sMsg)
        설명    서버통신 후 메시지를 받은 시점을 알려준다.
        입력값  sScrNo – 화면번호
                sRQName – 사용자구분 명
                sTrCode – Tran 명
                sMsg – 서버메시지
        반환값  없음
        비고    sScrNo – CommRqData의 sScrNo와 매핑된다.
                sRQName – CommRqData의 sRQName 와 매핑된다.
                sTrCode – CommRqData의 sTrCode 와 매핑된다
        """
        print("OnReceiveMsg")
        self.msg += sRQName + ": " + sMsg + "\r\n\r\n"

    # OnReceiveChejanData
    def ReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        """
        4) OnReceiveChejanData
        원형    void OnReceiveChejanData(BSTR sGubun, LONG nItemCnt, BSTR sFidList)
        설명    체결데이터를 받은 시점을 알려준다.
        입력값  sGubun – 체결구분
                nItemCnt - 아이템갯수
                sFidList – 데이터리스트
                sSplmMsg - 1.0.0.1 버전 이후 사용하지 않음.
        반환값  없음
        비고    sGubun – 0:주문체결통보, 1:잔고통보, 3:특이신호
                sFidList – 데이터 구분은 ‘;’ 이다
        """
        print("OnReceiveChejanData")

    # 로그인 이벤트 응답
    def EventConnect(self, nErrCode):
        """
        5) OnEventConnect
        원형    void OnEventConnect(LONG nErrCode)
        설명    서버 접속 관련 이벤트
        입력값  LONG nErrCode : 에러 코드
        반환값  없음
        비고    nErrCode가 0이면 로그인 성공, 음수면 실패
                음수인 경우는 에러 코드 참조
        """
        print("OnEventConnect")
        self.loginEventLoop.exit()

    # def PreventRequestOver(self): # 초당 5회 이상 방지

class MaxScreenNumber(Exception):
    """ 스크린 넘거 개수가 9999개를 초과할 경우 발생하는 예외"""

    def __init__(self, msg="Screen Number를 생성할 수 없습니다."):
        self.msg = msg

    def __str__(self):
        return self.msg

class ParameterTypeError(Exception):
    """ 파라미터 타입이 일치하지 않을 경우 발생하는 예외 """

    def __init__(self, msg="파라미터 타입이 일치하지 않습니다."):
        self.msg = msg

    def __str__(self):
        return self.msg

class ParameterValueError(Exception):
    """ 파라미터로 사용할 수 없는 값을 사용할 경우 발생하는 예외 """

    def __init__(self, msg="파라미터로 사용할 수 없는 값 입니다."):
        self.msg = msg

    def __str__(self):
        return self.msg

class KiwoomProcessingError(Exception):
    """ 키움에서 처리실패에 관련된 리턴코드를 받았을 경우 발생하는 예외 """

    def __init__(self, msg="처리 실패"):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return self.msg

class KiwoomConnectError(Exception):
    """ 키움서버에 로그인 상태가 아닐 경우 발생하는 예외 """

    def __init__(self, msg="로그인 여부를 확인하십시오"):
        self.msg = msg

    def __str__(self):
        return self.msg

# KiwoomAPI에서 반환하는 값
class ErrorCode(object):
    OP_ERR_NONE = 0                # 정상처리
    OP_ERR_NO_LOGIN = -1           # 미접속상태
    OP_ERR_LOGIN = -100            # 로그인시 접속 실패(아이피 오류 또는 접속정보 오류)
    OP_ERR_CONNECT = -101          # 서버 접속 실패
    OP_ERR_VERSION = -102          # 버전처리가 실패하였습니다.
    OP_ERR_TRCODE = -103           # TrCode가 존재하지 않습니다
    OP_ERR_NO_REGOPENAPI = -104    # 해외OpenAPI 미신청
    OP_ERR_SISE_OVERFLOW = -200    # 조회과부하
    OP_ERR_ORDER_OVERFLOW = -201   # 주문과부하
    OP_ERR_RQ_WRONG_INPUT = -202   # 조회입력값(명칭/누락) 오류
    OP_ERR_ORD_WRONG_INPUT = -300  # 주문입력값 오류
    OP_ERR_ORD_WRONG_ACCPWD = -301 # 계좌비밀번호를 입력하십시오
    OP_ERR_ORD_WRONG_ACCNO = -302  # 타인 계좌를 사용할 수 없습니다
    OP_ERR_ORD_WRONG_QTY200 = -303 # 경고-주문수량 200개 초과
    OP_ERR_ORD_WRONG_QTY400 = -304 # 제한-주문수량 400개 초과

    CAUSE = {
        0 : "정상처리",
        -1 : "미접속상태",
        -100 : "로그인시 접속 실패(아이피오류 또는 접속정보 오류)",
        -101 : "서버 접속 실패",
        -102 : "버전처리가 실패하였습니다.",
        -103 : "TrCode가 존재하지 않습니다.",
        -104 : "해외OpenAPI 미신청",
        -200 : "조회과부하",
        -201 : "주문과부하",
        -202 : "조회입력값(명칭/누락) 오류",
        -300 : "주문입력값 오류",
        -301 : "계좌비밀번호를 입력하십시오.",
        -302 : "타인 계좌를 사용할 수 없습니다.",
        -303 : "경고-주문수량 200개 초과",
        -304 : "제한-주문수량 400개 초과"
    }

# 실시간 FID
class RealFidList(object):
    FIDLIST = {
        "해외선물옵션시세" : {
            20 : "체결시간",
            10 : "현재가(진법)",
            140 : "현재가",
            11 : "전일대비",
            12 : "등락율",
            27 : "매도호가",
            28 : "매수호가",
            15 : "체결량",
            13 : "거래량",
            16 : "시가",
            17 : "고가",
            18 : "저가",
            25 : "전일대비기호",
            26 : "전일대비",
            30 : "전일거래량등락율",
            22 : "체결일자",
            761 : "영업일자"
        },
        "해외선물옵션호가" : {
            21 : "호가시간",
            27 : "매도호가",
            28 : "매수호가",
            41 : "매도호가1",
            61 : "매도수량1",
            81 : "매도수량대비1",
            101 : "매도건수1",
            51 : "매수호가1",
            71 : "매수수량1",
            91 : "매수수량대비1",
            111 : "매수건수1",
            42 : "매도호가2",
            62 : "매도수량2",
            82 : "매도수량대비2",
            102 : "매도건수2",
            52 : "매수호가2",
            72 : "매수수량2",
            92 : "매수수량대비2",
            112 : "매수건수2",
            43 : "매도호가3",
            63 : "매도수량3",
            83 : "매도수량대비3",
            103 : "매도건수3",
            53 : "매수호가3",
            73 : "매수수량3",
            93 : "매수수량대비3",
            113 : "매수건수3",
            44 : "매도호가4",
            64 : "매도수량4",
            84 : "매도수량대비4",
            104 : "매도건수4",
            54 : "매수호가4",
            74 : "매수수량4",
            94 : "매수수량대비4",
            114 : "매수건수4",
            45 : "매도호가5",
            65 : "매도수량5",
            85 : "매도수량대비5",
            105 : "매도건수5",
            55 : "매수호가5",
            75 : "매수수량5",
            95 : "매수수량대비5",
            115 : "매수건수5",
            121 : "매도호가총잔량",
            122 : "매도호가총잔량직전대비",
            123 : "매도호가총건수",
            125 : "매수호가총잔량",
            126 : "매수호가총잔량직전대비",
            127 : "매수호가총건수",
            137 : "호가순잔량",
            128 : "순매수잔량",
            600 : "매도등락율1",
            601 : "매도등락율2",
            602 : "매도등락율3",
            603 : "매도등락율4",
            604 : "매도등락율5",
            610 : "매수등락율1",
            611 : "매수등락율2",
            612 : "매수등락율3",
            613 : "매수등락율4",
            614 : "매수등락율5"
        },
        "해외선물옵션주문" : {
            9201 : "계좌번호",
            9203 : "주문번호",
            9001 : "종목코드",
            907 : "매도수구분",
            905 : "주문구분",
            904 : "원주문번호",
            302 : "종목명",
            906 : "주문유형",
            900 : "주문수량",
            901 : "주문가격",
            13333 : "조건가격",
            13330 : "주문표시가격",
            13332 : "조건표시가격",
            902 : "미체결수량",
            913 : "주문상태",
            919 : "반대매매여부",
            8046 : "거래소코드",
            947 : "FCM코드",
            8043 : "통화코드",
            908 : "주문시"
        },
        "해외선물옵션 체결" : {
            9201 : "계좌번호",
            9203 : "주문번호",
            9001 : "종목코드",
            907 : "매도수구분",
            905 : "주문체결구분",
            8046 : "거래소코드",
            947 : "FCM코드",
            904 : "원주문번호",
            302 : "종목명",
            906 : "주문유형",
            900 : "주문수량",
            901 : "주문가격",
            13330 : "주문표시가격",
            13333 : "조건가격",
            13332 : "조건표시가격",
            909 : "체결번호",
            911 : "체결수량",
            910 : "체결가격",
            13331 : "체결표시가격",
            13329 : "체결금액",
            13326 : "거부수량",
            913 : "주문상태",
            902 : "주문잔량",
            935 : "체결수수료",
            13327 : "신규수량",
            13328 : "청산수량",
            8018 : "실현손익",
            8043 : "통화코드",
            8009 : "약정금액",
            930 : "미결제약정합계",
            13334 : "미결제약정단가표시(평균)",
            908 : "체결수신시간"
        },
        "해외선물옵션마진콜" : {
            9201 : "계좌번호",
            8054 : "경고구분", #  (1:1차 경고, 2:2차경고)
            8055 : "발생일시", # YYYYMMDDHHMMSSMS
            8053 : "마진콜율",
            8043 : "통화코드"
        }
    }

# TR 목록
class TrList(object):
    OPT = {
        "TR_OPT10001" : "opt10001", # 종목정보조회
        "TR_OPT10002" : "opt10002", # 해외옵션전체월물조회
        "TR_OPT10003" : "opt10003", # 해외옵션콜월물조회
        "TR_OPT10004" : "opt10004", # 회외옵션풋월물조회
        "TR_OPT10005" : "opt10005", # 관심종목조회
        "TR_OPT10006" : "opt10006", # 상품별현재가조회
        "TR_OPT10007" : "opt10007", # 거래소별현재가조회
        "TR_OPT10008" : "opt10008", # 해외선물전체시세조회
        "TR_OPT10009" : "opt10009", # 전일대비등락율상위조회
        "TR_OPT10010" : "opt10010", # 당일거래량상위조회
        "TR_OPT10011" : "opt10011", # 체결데이타조회
        "TR_OPT10012" : "opt10012", # 분데이타조회
        "TR_OPT10013" : "opt10013", # 일별데이타조회
        "TR_OPT10014" : "opt10014", # 종목시작시간
    }
    OPW = {
        "TR_OPW20001" : "opw20001", # 주문수량제한조회
        "TR_OPW20002" : "opw20002", # 주순수량제한등록
        "TR_OPW20003" : "opw20003", # 주문수량제한삭제
        "TR_OPW20004" : "opw20004", # 상품별증거금조회
        "TR_OPW20005" : "opw20005", # 위탁증거금비율조회
        "TR_OPW20006" : "opw20006", # 원화대용지정해지조회
        "TR_OPW20007" : "opw20007", # 원화대용지정해지처리
        "TR_OPW20008" : "opw20008", # 원화대용지정해지금액계산조회
        "TR_OPW30001" : "opw30001", # 미체결내역조회
        "TR_OPW30002" : "opw30002", # 미체결내역(TCP)조회
        "TR_OPW30003" : "opw30003", # 미체결잔고내역조회
        "TR_OPW30004" : "opw30004", # 미체결잔고내역(TCP)조회
        "TR_OPW30005" : "opw30005", # 주문체결내역조회
        "TR_OPW30006" : "opw30006", # 주문거부내역조회
        "TR_OPW30007" : "opw30007", # 청산내역조회
        "TR_OPW30008" : "opw30008", # 위탁증거금조회
        "TR_OPW30009" : "opw30009", # 예수금및증거금현황조회
        "TR_OPW30010" : "opw30010", # 증거금상세조회
        "TR_OPW30011" : "opw30011", # 주문가능수량조회
        "TR_OPW30012" : "opw30012", # 미결제내역상세조회
        "TR_OPW30013" : "opw30013", # 일자별종목별손익상세조회
        "TR_OPW30014" : "opw30014", # 일자별미결제및평가조회
        "TR_OPW30015" : "opw30015", # 통화별예수금현황조회
        "TR_OPW30016" : "opw30016", # 해외옵션인수도대상조회
        "TR_OPW30017" : "opw30017", # 해외옵션인수도신청내역조회
        "TR_OPW30018" : "opw30018", # 주문증거금조회
        "TR_OPW30019" : "opw30019", # 해외옵션인수도신청
        "TR_OPW30020" : "opw30020", # 해외옵션인수도신청취소
        "TR_OPW40001" : "opw40001", # 기간손익내역조회
        "TR_OPW40002" : "opw40002", # 계좌별최종결제내역조회
        "TR_OPW40003" : "opw40003", # 기간별결제내역조회
        "TR_OPW40004" : "opw40004", # 해외옵션최종결제내역조회
        "TR_OPW50001" : "opw50001", # 장운영정보조회
        "TR_OPW50002" : "opw50002", # 일자별정산가조회
        "TR_OPW50003" : "opw50003", # 최근월물만기도래현황조회
        "TR_OPW50004" : "opw50004", # 상품별명세및요약조회
        "TR_OPW50005" : "opw50005", # 품목별FND일자조회
        "TR_OPW60001" : "opw60001", # 원화대용환전처리외화예수금조회
        "TR_OPW60002" : "opw60002", # 해외증권원화외화대용환전처리
        "TR_OPW60003" : "opw60003" # 원화외화예수금잔액조회
    }
    OPC = {
        "TR_OPC10001" : "opc10001", # 해외선물옵션틱차트조회
        "TR_OPC10002" : "opc10002", # 해외선물옵션분차트조회
        "TR_OPC10003" : "opc10003", # 해외선물옵션일차트조회
        "TR_OPC10004" : "opc10004", # 해외선물옵션주차트조회
        "TR_OPC10005" : "opc10005" # 해외선물옵션월차트조회
    }


if __name__ == "__main__":
    kfo = KFOpenAPI()
