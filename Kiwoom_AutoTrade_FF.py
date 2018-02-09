import sys, os.path, configparser, time
import threading as tr
from ItemInfo import *
from AccountInfo import *
from KFOpenAPI import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

rootDir = os.getcwd() # 작업 최상위 디렉토리
AutoTradeMainForm = uic.loadUiType(rootDir + '\kiwoom_autotrade_ff.ui')[0]
configDir = rootDir + '\Kiwoom_AutoTrade_FF.ini'

class AutoTradeMain(QMainWindow, AutoTradeMainForm):
    def __init__(self):
        super().__init__()
        self.logCounter = 0 # 로그 카운터 초기화
        self._SetupUi() # User Interface 초기화
        self._SetConfig()
        self.kiwoom = KFOpenAPI() # 키움증권 OPEN_API-W
        self.accountInfo = AccountInfo(self.kiwoom) # 계좌정보
        self.sScrNo = self.kiwoom.GetScreenNumber() # 화면번호
        self.sAccNo = ''  # 데이터 송수신 중인 계좌번호
        self.chejanReceive = [0, 0] # 체결 잔고 (index 0 : 주문, 1 : 체결)
        self.kiwoom.OnReceiveTrData.connect(self.ReceiveTrData)
        self.kiwoom.OnReceiveRealData.connect(self.ReceiveRealData)
        self.kiwoom.OnReceiveMsg.connect(self.ReceiveMsg)
        self.kiwoom.OnReceiveChejanData.connect(self.ReceiveChejanData)
        self.kiwoom.OnEventConnect.connect(self.EventConnect)

    def _SetConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read('Kiwoom_AutoTrade_FF.ini')

    # User Interface 초기화
    def _SetupUi(self):
        # QTableWidget Setting
        self.setupUi(self) # QT Creater로 생성된 기본 프레임
        self._InitButton()
        self._InitTableWidget()
        self.show()

    # 종목 정보 초기화
    def _InitItemInfo(self, status): # 종목 정보 초기화
        try:
            # 로그인 상태이면 초기화 진행, 아닐 경우 메모리 정리
            if status:
                self.sAccNo = self.cbAccountNum.currentText()
                self.itemInfo = []
                self.dicItemInfo = {}
                self.orderIndex = []
                for i in range(int(self.config['DEFAULT']['ItemsCount'])):
                    sections = 'ItemProperty' + str(i)
                    self.itemInfo.append(ItemInfo())
                    self.itemInfo[i].SetCode(self.config[sections]['Code'], i)
                    self.dicItemInfo.update({self.config[sections]['Code']:i})
                    self.orderIndex.append([])
                    # self.Logging('Create {0} information, Index = {1}'.format(self.config[sections]['Code'], i))
                    # Check : 코드 정보를 정확히 불러오는지 확인
                self._SetItemInfo() # 종목별 실시간 조회(관심종목)
                time.sleep(1)
                self._SetOrderInfo()
                self._SetAccountInfo()
            else:
                self.accountInfo.clear()
                self.itemInfo.clear()
        except Exception as error:
            self.Logging("[Exception] {} in _InitItemInfo".format(error))

    # 버튼 기능을 초기화
    def _InitButton(self):
        # 메뉴(기능 - 로그인)
        self.actionLogin.setShortcut('Ctrl+L')
        self.actionLogin.setStatusTip('Open Login pannel')
        self.actionLogin.triggered.connect(self._OpenLoginPannel)
        # 메뉴(기능 - 로그아웃) 기능을 지원하지 않음
        self.actionLogout.setShortcut('Ctrl+O')
        self.actionLogout.setStatusTip('Disconnect')
        self.actionLogout.triggered.connect(self._Disconnect)
        # 메뉴(기능 - 종료)
        self.actionClose.setShortcut('Ctrl+X')
        self.actionClose.setStatusTip('Close')
        self.actionClose.triggered.connect(self._Close)
        # 계좌정보 - 조회 버튼
        self.btnSearchMyAccount.clicked.connect(self._ClickedSearchMyAccount)
        # test 버튼
        self.btnTest.clicked.connect(self.ClickedTest)

    # QTableWidget 초기화
    def _InitTableWidget(self):
        # tbAcountItem
        rowCount = 4
        columnCount = 14
        self.tbAcountItemData = []
        for i in range(rowCount):
            self.tbAcountItemData.append([])
            for j in range(columnCount):
                self.tbAcountItemData[i].append('')
        self.tbAcountItem.setRowCount(rowCount) # 4행
        self.tbAcountItem.setColumnCount(columnCount) # 10열
        # 행 높이, 열 너비 설정
        for i in range(rowCount):
            self.tbAcountItem.setRowHeight(i, 21)
        for i in range(columnCount):
            if i == 0 or i == 1 or i == 2:
                self.tbAcountItem.setColumnWidth(i, 75)
            elif i == 3:
                self.tbAcountItem.setColumnWidth(i, 110)
            elif i == 4 or i == 5 or i == 7 or i == 8 or i == 13:
                self.tbAcountItem.setColumnWidth(i, 60)
            else:
                self.tbAcountItem.setColumnWidth(i, 80)
            self.tbAcountItem.setHorizontalHeaderItem(i, QTableWidgetItem().setBackground(Qt.red))
        # Header 설정
        columnLables = ['구 분', '종목코드', '현재가', '주문번호', '주 문', '주문수량', '주문가', '보 유',
                        '보유수량', '진입가', '목표가', '손절가', '평가손익', '통화코드']
        self.tbAcountItem.setHorizontalHeaderLabels(columnLables) # QTableWidget.setHorizontalHeaderLabels(self, QStringList lables)

    def _OpenLoginPannel(self):
        # 로그인
        # 로그인 상태 'Already Connected!!'
        # 비로그인 상태 '로그인 패널'
        if not self.kiwoom.GetConnectState():
            self.Logging('Opened Login Pannel')
            self.kiwoom.CommConnect()
        else:
            self.accountInfo.SetConnectState(True)
            self.Logging('Already Connected!!')

    def _Disconnect(self):
        # 로그아웃
        # 로그인 상태 'Disconnected'
        # 비로그인 상태 'Already Disconnected!!'
        if self.kiwoom.GetConnectState():
            self.kiwoom.CommTerminate()
            self.accountInfo.SetConnectState(False)
            self.Logging('Disconnected')
        else:
            self.accountInfo.SetConnectState(False)
            self.Logging('Already Disconnected!!')

    def _Close(self):
        # 화면종료
        self.close()

    def _ClickedSearchMyAccount(self):
        self.Logging('Clicked btnSearchMyAccount')
        if not self.accountInfo.GetConnectState():
            self._OpenLoginPannel()
        else:
            self._InitItemInfo(True)

    def _SetItemInfo(self): # 종목별 초기 데이터 조회
        sRQName = '종목정보조회'
        sTrCode = TrList.OPT['TR_OPT10001']
        items = ''
        nScrNo = int(self.sScrNo)
        for item in self.itemInfo:
            items += item.GetCode() + ';'
            try:
                nScrNo -= 1
                sScrNo = str(nScrNo)
                self.Logging('Requesting [{}] information'.format(item.GetCode()))
                self.kiwoom.SetInputValue('종목코드', item.GetCode())
                self.Logging('[Input Value] sRQName = {0}, sTrCode = {1}, sScrNo = {2}'.format(sRQName, sTrCode, sScrNo))
                errorCode = self.kiwoom.CommRqData(sRQName, sTrCode, '', sScrNo)
                if errorCode:
                    self.Logging('[Error] Code = {} in_SetItemInfo'.format(errorCode))
                self.Logging('Finished getting information about [{}]'.format(item.GetCode()))
            except Exception as error:
                self.Logging('[Exception] {} in _SetItemInfo'.format(error))
        self.accountInfo.SetItemInfo(self.itemInfo)
        self.SetTbAcountItem()
        try:
            sRQName = '관심종목조회'
            sTrCode = TrList.OPT['TR_OPT10005']
            sScrNo = self.sScrNo
            self.kiwoom.SetInputValue('종목코드', items)
            errorCode = self.kiwoom.CommRqData(sRQName, sTrCode, '', sScrNo)
            if errorCode:
                self.Logging('[Error] Code = {} in _SetItemInfo'.format(errorCode))
        except Exception as error:
            self.Logging('[Exception] {} in _SetItemInfo'.format(error))

    # 주문한(미체결된) 종목 정보
    def _SetOrderInfo(self):
        sRQName = '계좌정보조회'
        sTrCode = TrList.OPW['TR_OPW30001']
        sScrNo = self.sScrNo
        try:
            self.Logging('Requesting [{}] information'.format(self.sAccNo))
            self.kiwoom.SetInputValue('계좌번호', self.sAccNo)
            self.kiwoom.SetInputValue('비밀번호', '')
            self.kiwoom.SetInputValue('비밀번호입력매체', '00')
            self.kiwoom.SetInputValue('종목코드', '')
            self.kiwoom.SetInputValue('통화코드', '')
            self.kiwoom.SetInputValue('매도수구분', '')
            errorCode = self.kiwoom.CommRqData(sRQName, sTrCode, '', sScrNo)
            if errorCode:
                self.Logging('[Error] Code = {} in _SetOrderInfo'.format(errorCode))
            self.Logging('Finished getting information {}'.format(self.sAccNo))
        except Exception as error:
            self.Logging('[Exception] {} in _SetOrderInfo'.format(error))
            error = '{}'.format(error)
            if error == 'CommRqData(): 조회과부하':
                self.Logging('[재요청중...] in _SetOrderInfo')
                tr.Timer(0.25, self._SetOrderInfo).start()
        self.SetTbAcountItem()

    # 보유하고 있는 종목 정보
    def _SetAccountInfo(self):
        sRQName = '계좌정보조회'
        sTrCode = TrList.OPW['TR_OPW30003']
        sScrNo = self.sScrNo
        try:
            self.Logging('Requesting [{}] information'.format(self.sAccNo))
            self.kiwoom.SetInputValue('계좌번호', self.sAccNo)
            self.kiwoom.SetInputValue('비밀번호', '')
            self.kiwoom.SetInputValue('비밀번호입력매체', '00')
            self.kiwoom.SetInputValue('통화코드', 'USD')
            errorCode = self.kiwoom.CommRqData(sRQName, sTrCode, '', sScrNo)
            if errorCode:
                self.Logging('[Error] Code = {} in _SetAccountInfo'.format(errorCode))
            self.Logging('Finished getting information {}'.format(self.sAccNo))
        except Exception as error:
            self.Logging('[Exception] {} in _SetAccountInfo'.format(error))
            error = '{}'.format(error)
            if error == 'CommRqData(): 조회과부하':
                self.Logging('[재요청중...] in _SetAccountInfo')
                tr.Timer(0.25, self._SetAccountInfo).start()
        self.SetTbAcountItem()

    def _TrRequest(self):
        if self.chejanReceive[0] > 0:
            self._SetOrderInfo()
        if self.chejanReceive[1] > 0:
            self._SetAccountInfo()
        self.chejanReceive = [0, 0]

    ###########################################################################
    # 이벤트 수신부
    # 이벤트 발생시 데이터 처리
    # #########################################################################

    # 요청 이벤트 수신부
    def ReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        # self.Logging("[Event] OnReceiveTrData")
        # self.Logging("sScrNo : {}".format(sScrNo))
        # self.Logging("sRQName : {}".format(sRQName))
        # self.Logging("sTrCode : {}".format(sTrCode))
        # self.Logging("sRecordName : {}".format(sRecordName))
        # self.Logging("sPrevNext : {}".format(sPrevNext))

        if sRQName == '종목정보조회':
            if sTrCode == TrList.OPT['TR_OPT10001']:
                try:
                    sCode = sPrevNext.split(' ')[0][2:8]
                    nIndex = self.dicItemInfo[sCode]
                    for singleData in self.itemInfo[nIndex].singleData:
                        sValue = self.kiwoom.GetCommData(sTrCode, sRQName, 0, singleData[0]).strip()
                        self.itemInfo[nIndex].SetSingleData(singleData[0], sValue) # 종목별 SingleData 입력
                        # self.Logging("{} : {}".format(singleData[0], self.itemInfo[nIndex].GetSingleData(singleData[0])))
                except Exception as error:
                    self.Logging("[Exception][종목정보조회] {} in ReceiveTrData ".format(error))

        elif sRQName == '계좌정보조회':
            if  sTrCode == TrList.OPW['TR_OPW30001']:
                try:
                    self.accountInfo.InitOrderInfo()
                    nCount = self.kiwoom.GetRepeatCnt(sTrCode, sRQName) # 반복 회수 조회
                    for i in range(nCount):
                        # 종목 정보 추가
                        sOrderNo = self.kiwoom.GetCommData(sTrCode, sRQName, i, '주문번호')
                        sOriginalOrderNo = self.kiwoom.GetCommData(sTrCode, sRQName, i, '원주문번호')
                        self.accountInfo.AddOrderInfo(sOrderNo, sOriginalOrderNo)
                        for data in self.accountInfo.GetOrderInfo(sOrderNo).orderData:
                            sValue = self.kiwoom.GetCommData(sTrCode, sRQName, i, data[0])
                            self.accountInfo.SetOrderInfo(sOrderNo, data[0], sValue)
                    self.SetOrderIndex()

                except Exception as error:
                    self.Logging("[Exception][계좌정보조회] {} in ReceiveTrData ".format(error))

            if sTrCode == TrList.OPW['TR_OPW30003']:
                try:
                    for data in self.accountInfo.myBalance:
                        sValue = self.kiwoom.GetCommData(sTrCode, sRQName, 0, data[0]).strip()
                        self.accountInfo.SetMyBalance(data[0], sValue) # 보유 정목 입력
                        # self.Logging('{0} : {1}'.format(data[0], self.accountInfo.GetMyBalance(data[0])))
                    self.accountInfo.InitItemInfo()
                    nCount = self.kiwoom.GetRepeatCnt(sTrCode, sRQName)
                    for i in range(nCount):
                        sCode = self.kiwoom.GetCommData(sTrCode, sRQName, i, '종목코드')
                        nIndex = self.accountInfo.dicMyItems[sCode]
                        for data in self.accountInfo.myItemInfo[nIndex].itemBalance:
                            sValue = self.kiwoom.GetCommData(sTrCode, sRQName, i, data[0]).strip()
                            self.accountInfo.myItemInfo[nIndex].SetItemBalance(data[0], sValue)
                            # self.Logging('{0} : {1}'.format(data[0], self.accountInfo.myItemInfo[nIndex].GetItemBalance(data[0])))
                except Exception as error:
                    self.Logging("[Exception][계좌정보조회] {} in ReceiveTrData ".format(error))

    # 실시간 이벤트 수신부
    def ReceiveRealData(self, sCode, sRealType, sRealData):
        # self.Logging("[Event] ReceiveRealData")
        # self.Logging("sCode : {}".format(sCode))
        # self.Logging("sRealType : {}".format(sRealType))
        # self.Logging("sRealData : {}".format(sRealData))
        if sRealType == "해외옵션호가" or sRealType == "해외선물호가":
            try:
                nIndex = self.dicItemInfo[sCode]
                for realFid in self.itemInfo[nIndex].dicRealHoga.keys():
                    sValue = self.kiwoom.GetCommRealData(sRealType, realFid).strip()
                    self.itemInfo[nIndex].SetRealHoga(realFid, sValue)
                    # self.Logging("[{0}] : {1}".format(realFid, self.itemInfo[nIndex].GetRealHoga(realFid))) # 입력 확인
                # self.SetTbAcountItem(nIndex)
            except Exception as error:
                self.Logging("[해외옵션선물호가][Exception] {} in ReceiveRealData".format(error))
        elif sRealType == "해외옵션시세" or sRealType == "해외선물시세":
            try:
                nIndex = self.dicItemInfo[sCode]
                for realFid in self.itemInfo[nIndex].dicRealMarketPrice.keys():
                    sValue = self.kiwoom.GetCommRealData(sRealType, realFid).strip()
                    self.itemInfo[nIndex].SetRealMarketPrice(realFid, sValue)
                    # self.Logging("[{0}] : {1}".format(realFid, self.itemInfo[nIndex].GetRealMarketPrice(realFid))) # 입력 확인
                nIndex = self.accountInfo.dicMyItems[sCode]
                self.accountInfo.myItemInfo[nIndex].SetCurrentPrice()
                nIndex = self.dicItemInfo[sCode]
                self.SetTbAcountItem(nIndex)
            except Exception as error:
                self.Logging("[해외옵션선물시세][Exception] {} in ReceiveRealData".format(error))
        elif sRealType == "마진콜" or sRealType == "잔고" or sRealType == "주문체결":
            self.Logging('[RealData] {} '.format(sRealType))


    def ReceiveMsg(self, sScrNo, sRQname, sTrCode, sMsg):
        self.Logging('[ReceiveMsg]sScrNo : {}'.format(sScrNo))
        self.Logging('[ReceiveMsg]sRQname : {}'.format(sRQname))
        self.Logging('[ReceiveMsg]sTrCode : {}'.format(sTrCode))
        self.Logging('[ReceiveMsg]sMsg : {}'.format(sMsg))

    def ReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        # self.Logging('[ReceiveChejanData]sGubun : {}'.format(sGubun))
        # self.Logging('[ReceiveChejanData]nItemCnt : {}'.format(nItemCnt))
        # self.Logging('[ReceiveChejanData]sFidList : {}'.format(sFidList))
        try:
            # fids = sFidList.split(';')
            self.Logging('sGubun : {}'.format(sGubun))
            if sGubun == '0': # 해외선물옵션주문
                self.chejanReceive[0] += 1
                # tr.Timer(0.3, self._SetOrderInfo).start()
            elif sGubun == '1': # 해외선물옵션체결
                self.chejanReceive[1] += 1
                # tr.Timer(0.3, self._SetAccountInfo).start()
            if tr.active_count() == 1:
                tr.Timer(0.24, self._TrRequest).start()
        except Exception as error:
            self.Logging("[Exception] {} in ReceiveChejanData ".format(error))

    def EventConnect(self, nErrCode):
        # 서버와 연결되거나 해제되었을 경우 발생되는 이벤트 처리 메소드
        try:
            # nErrCode(0 : 접속, 음수값 : 오류)
            if nErrCode == ErrorCode.OP_ERR_NONE:
                self.Logging('Successed login')
                self.Logging('Loading login information')
                self.accountInfo.SetConnectState(True)
                self.accountInfo.SetLoginInfo()
                for i in range(len(self.accountInfo.loginInfo.accNo)-1):
                    self.cbAccountNum.addItem(self.accountInfo.loginInfo.accNo[i])
                # self._InitItemInfo(True)
                self.Logging('Completed Login!')
            else:
                try:
                    self.accountInfo.SetConnectState(False)
                    self._InitItemInfo(False)
                    msg = ErrorCdoe.CAUSE[nErrCode]
                except KeyError as error:
                    self.Logging('[Error]'+str(error)+' in EventConnect')
                finally:
                    print(msg)

        except Exception as error:
            self.Logging('[Error]'+str(error)+' in EventConnect')

        finally:
            try:
                self.loginEventLoop.exit()
            except AttributeError:
                pass

    # 관심종목 및 실시간 거래 내역을 확인하는 테이블 설정
    def SetTbAcountItem(self, nIndex = -1):
        # self.Logging("setting tbAcountItem")
        # 프로그램 실행 및 설정이 변경 되었을 경우 초기화과정
        try:
            if nIndex < 0 or nIndex > 3:
                self.Logging("[{}]Seting All item in table".format(nIndex))
                for i in range(14):
                    for key in self.dicItemInfo.keys():
                        if (i == 0 or i == 1 or i == 13):
                            row = self.dicItemInfo[key]
                            self.tbAcountItemData[row][0] = '시세감시'
                            self.tbAcountItemData[row][1] = key
                            self.tbAcountItemData[row][13] = 'USD'
                            self.tbAcountItem.setItem(row, 0, QTableWidgetItem(self.tbAcountItemData[row][0]))
                            self.tbAcountItem.setItem(row, 1, QTableWidgetItem(self.tbAcountItemData[row][1]))
                            self.tbAcountItem.setItem(row, 13, QTableWidgetItem(self.tbAcountItemData[row][13]))
                        elif i == 2: # 현재가
                            for key in self.dicItemInfo.keys():
                                row = self.dicItemInfo[key]
                                currentPrice = self.itemInfo[row].GetSingleData('현재가(진법)')
                                if currentPrice == '':
                                    currentPrice = self.itemInfo[row].GetSingleData('현재가')
                                color, currentPrice = self.GetPriceForm(currentPrice)
                                self.tbAcountItemData[row][i] = currentPrice
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(currentPrice)) # 데이터 입력
                                self.tbAcountItem.item(row, i).setForeground(QBrush(color)) # 글자색 변경
                        elif i == 3:
                            for key in self.dicItemInfo.keys():
                                row = self.dicItemInfo[key]
                                if len(self.orderIndex[row]) > 0:
                                    col = 0
                                    self.tbAcountItemData[row][i] = self.orderIndex[row][col]
                                    orderNo = '{:010}({}/{})'.format(int(self.tbAcountItemData[row][i]), col+1, len(self.orderIndex[row]))
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                    orderNo = self.tbAcountItemData[row][i]
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(orderNo))
                        elif i == 4: # 주문 포지션
                            for key in self.dicItemInfo.keys():
                                row = self.dicItemInfo[key]
                                color = Qt.black
                                orderNo = self.tbAcountItemData[row][i-1]
                                if orderNo != '':
                                    nPosition = self.accountInfo.GetOrderInfo(orderNo, '매도수구분')
                                    if nPosition == '1': # 매도일 경우
                                        self.tbAcountItemData[row][i] = '매도'
                                        color = Qt.blue
                                    elif nPosition == '2': # 매수일 경우
                                        self.tbAcountItemData[row][i] = '매수'
                                        color = Qt.red
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                                self.tbAcountItem.item(row, i).setForeground(QBrush(color)) # 글자색 변경
                        elif i == 5: # 주문가
                            for key in self.dicItemInfo.keys():
                                row = self.dicItemInfo[key]
                                orderNo = self.tbAcountItemData[row][i-2]
                                if orderNo != '':
                                    self.tbAcountItemData[row][i] = str(int(self.accountInfo.GetOrderInfo(orderNo, '주문수량')))
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                        elif i == 6: # 주문 수량
                            for key in self.dicItemInfo.keys():
                                row = self.dicItemInfo[key]
                                orderNo = self.tbAcountItemData[row][i-3]
                                if orderNo != '':
                                    self.tbAcountItemData[row][i] = self.accountInfo.GetOrderInfo(orderNo, '주문표시가격')
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                        elif i == 7: # 보유 포지션
                            for key in self.accountInfo.dicMyItems.keys():
                                self.tbAcountItemData[row][i] = ''
                                color = Qt.black
                                row = self.accountInfo.dicMyItems[key]
                                if self.accountInfo.myItemInfo[row].HasItem():
                                    nPosition = self.accountInfo.myItemInfo[row].GetItemBalance('매도수구분')
                                    if nPosition == '1': # 매도일 경우
                                        self.tbAcountItemData[row][i] = '매도'
                                        color = Qt.blue
                                    elif nPosition == '2': # 매수일 경우
                                        self.tbAcountItemData[row][i] = '매수'
                                        color = Qt.red
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                                self.tbAcountItem.item(row, i).setForeground(QBrush(color)) # 글자색 변경
                        elif i == 8: # 보유수량
                            for key in self.accountInfo.dicMyItems.keys():
                                row = self.accountInfo.dicMyItems[key]
                                if self.accountInfo.myItemInfo[row].HasItem():
                                    self.tbAcountItemData[row][i] = str(int(self.accountInfo.myItemInfo[row].GetItemBalance('수량')))
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                        elif i == 9: # 진입가
                            for key in self.accountInfo.dicMyItems.keys():
                                row = self.accountInfo.dicMyItems[key]
                                if self.accountInfo.myItemInfo[row].HasItem():
                                    self.tbAcountItemData[row][i] = self.accountInfo.myItemInfo[row].GetItemBalance('평균단가')
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                        elif i == 10: # 청산가
                            for key in self.accountInfo.dicMyItems.keys():
                                row = self.accountInfo.dicMyItems[key]
                                if self.accountInfo.myItemInfo[row].HasItem():
                                    self.tbAcountItemData[row][i] = self.accountInfo.myItemInfo[row].GetGoalPrice()
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                        elif i == 11: # 손절가
                            for key in self.accountInfo.dicMyItems.keys():
                                row = self.accountInfo.dicMyItems[key]
                                if self.accountInfo.myItemInfo[row].HasItem():
                                    self.tbAcountItemData[row][i] = self.accountInfo.myItemInfo[row].GetLossPrice()
                                else:
                                    self.tbAcountItemData[row][i] = ''
                                    self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                        elif i == 12 : # 평가손익
                            for key in self.accountInfo.dicMyItems.keys():
                                row = self.accountInfo.dicMyItems[key]
                                if self.accountInfo.myItemInfo[row].HasItem():
                                    self.tbAcountItemData[row][i] = self.accountInfo.myItemInfo[row].GetEvaluationPrice()
                                    color, _ = self.GetPriceForm(sEvaluationPrice)
                                else:
                                    sEvaluationPrice = ''
                                self.tbAcountItem.setItem(row, i, QTableWidgetItem(self.tbAcountItemData[row][i]))  # 데이터 입력
                                self.tbAcountItem.item(row, i).setForeground(QBrush(color)) # 글자색 변경

            else:
                for i in range(14):
                    if i == 2:
                        currentPrice = self.itemInfo[nIndex].GetSingleData("현재가(진법)")
                        color, currentPrice = self.GetPriceForm(currentPrice)
                        self.tbAcountItemData[nIndex][i] = currentPrice
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(currentPrice))
                        self.tbAcountItem.item(nIndex, i).setForeground(QBrush(color))
                    elif i == 3:
                        if len(self.orderIndex[nIndex]) > 0:
                            col = 0
                            self.tbAcountItemData[nIndex][i] = self.orderIndex[nIndex][col]
                            orderNo = '{:010}({}/{})'.format(int(self.tbAcountItemData[nIndex][i]), col+1, len(self.orderIndex[nIndex]))
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                            orderNo = self.tbAcountItemData[nIndex][i]
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(orderNo))
                    elif i == 4: # 주문 포지션
                        color = Qt.black
                        orderNo = self.tbAcountItemData[nIndex][i-1]
                        if orderNo != '':
                            nPosition = self.accountInfo.GetOrderInfo(orderNo, '매도수구분')
                            if nPosition == '1': # 매도일 경우
                                self.tbAcountItemData[nIndex][i] = '매도'
                                color = Qt.blue
                            elif nPosition == '2': # 매수일 경우
                                self.tbAcountItemData[nIndex][i] = '매수'
                                color = Qt.red
                            else:
                                self.tbAcountItemData[nIndex][i] = ''
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                        self.tbAcountItem.item(nIndex, i).setForeground(QBrush(color)) # 글자색 변경
                    elif i == 5: # 주문가
                        orderNo = self.tbAcountItemData[nIndex][i-2]
                        if orderNo != '':
                            self.tbAcountItemData[nIndex][i] = str(int(self.accountInfo.GetOrderInfo(orderNo, '주문수량')))
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                    elif i == 6: # 주문 수량key]
                        orderNo = self.tbAcountItemData[nIndex][i-3]
                        if orderNo != '':
                            self.tbAcountItemData[nIndex][i] = self.accountInfo.GetOrderInfo(orderNo, '주문표시가격')
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                    elif i == 7: # 보유 포지션
                        if self.accountInfo.myItemInfo[nIndex].HasItem():
                            nPosition = self.accountInfo.myItemInfo[nIndex].GetItemBalance('매도수구분')
                            if nPosition == '1': # 매도일 경우
                                self.tbAcountItemData[nIndex][i] = '매도'
                                color = Qt.blue
                            elif nPosition == '2': # 매수일 경우
                                self.tbAcountItemData[nIndex][i] = '매수'
                                color = Qt.red
                            else:
                                self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                        self.tbAcountItem.item(nIndex, i).setForeground(QBrush(color)) # 글자색 변경
                    elif i == 8: # 보유수량
                        if self.accountInfo.myItemInfo[nIndex].HasItem():
                            self.tbAcountItemData[nIndex][i] = str(int(self.accountInfo.myItemInfo[nIndex].GetItemBalance('수량')))
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                    elif i == 9: # 진입가
                        if self.accountInfo.myItemInfo[nIndex].HasItem():
                            self.tbAcountItemData[nIndex][i] = self.accountInfo.myItemInfo[nIndex].GetItemBalance('평균단가')
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                    elif i == 10: # 청산가
                        if self.accountInfo.myItemInfo[nIndex].HasItem():
                            self.tbAcountItemData[nIndex][i] = self.accountInfo.myItemInfo[nIndex].GetGoalPrice()
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                    elif i == 11: # 손절가
                        if self.accountInfo.myItemInfo[nIndex].HasItem():
                            self.tbAcountItemData[nIndex][i] = self.accountInfo.myItemInfo[nIndex].GetLossPrice()
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                    elif i == 12 : # 평가손익
                        if self.accountInfo.myItemInfo[nIndex].HasItem():
                            self.tbAcountItemData[nIndex][i] = self.accountInfo.myItemInfo[nIndex].GetEvaluationPrice()
                            color, _ = self.GetPriceForm(self.tbAcountItemData[nIndex][i])
                        else:
                            self.tbAcountItemData[nIndex][i] = ''
                        self.tbAcountItem.setItem(nIndex, i, QTableWidgetItem(self.tbAcountItemData[nIndex][i]))  # 데이터 입력
                        self.tbAcountItem.item(nIndex, i).setForeground(QBrush(color)) # 글자색 변경

        except Exception as error:
            self.Logging("[Exception] {} in SetTbAcountItem".format(error))

    def GetPriceForm(self, sValue):
        if sValue[0:1] == '-':
            return Qt.blue, sValue[1:]
        elif sValue[0:1] == '+':
            return Qt.red, sValue[1:]
        else:
            return Qt.black, sValue

    def SetOrderIndex(self):
        for i in range(len(self.orderIndex)):
            self.orderIndex[i].clear()
        for key in self.accountInfo.orderInfo.keys():
            code = self.accountInfo.GetOrderInfo(key, '종목코드')
            nIndex = self.dicItemInfo[code]
            self.orderIndex[nIndex].append(key)

    def Logging(self, strData):
        # 각종 데이터 처리 과정을 메론 로그에 남김
        if self.logCounter == 0:
            logFile = open('log.txt', 'a')
            logFile.write('\n\n[{0}] Started Program'.format(time.ctime()))
            logFile.close()
        try:
            if not (isinstance(strData, str)):
                strData = str(strData)
            self.lstLog.addItem('[{0:05d}] {1}'.format(self.logCounter, strData))
            self.lstLog.scrollToBottom()
            logFile = open('log.txt', 'a')
            logFile.write('\n[{0:05d}] {1}'.format(self.logCounter, strData))
            logFile.close()
            self.logCounter += 1
        except:
            self.Logging('error')

    def logging(self,strData):
        self.Logging("[Debug] This isn't Logging, you will fixed from self.logging to self.Logging")
        self.Logging(strData)

    def ClickedTest(self):
        self.Logging(self.cbAccountNum.currentText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('fusion'))  # 어플리케이션 기본 디자인 설정 "Fusion"

    autoTradeMain = AutoTradeMain()
    sys.exit(app.exec_())
