import sys, os.path, configparser, time
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
        self.kiwoom.OnReceiveTrData.connect(self.ReceiveTrData)
        self.kiwoom.OnReceiveRealData.connect(self.ReceiveRealData)
        # self.kiwoom.OnReceiveMsg.connect(self.ReceiveMsg)
        # self.kiwoom.OnReceiveChejanData.connect(self.ReceiveChejanData)
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

    # 변수 값 설정
    def _InitItemInfo(self, loginStatus): # 종목 정보 초기화
        try:
            if loginStatus:
                self.itemInfo = []
                self.dicItemInfo = {}
                for i in range(int(self.config['DEFAULT']['ItemsCount'])):
                    sections = 'ItemProperty' + str(i)
                    self.itemInfo.append(ItemInfo())
                    self.itemInfo[i].SetCode(self.config[sections]['Code'], i)
                    self.dicItemInfo.update({self.config[sections]['Code']:i})
                    self.Logging('Create {0} infomation, Index = {1}'.format(self.config[sections]['Code'], i))
                    # Check : 코드 정보를 정확히 불러오는지 확인
                self._SetItemInfo() # 종목별 상세 조건
            else:
                self.ItemInfo.clear()
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
        # twRealState
        rowCount = 4
        columnCount = 10
        self.twRealState.setRowCount(rowCount) # 4행
        self.twRealState.setColumnCount(columnCount) # 10열
        # 행 높이, 열 너비 설정
        for i in range(rowCount):
            self.twRealState.setRowHeight(i, 21)
        for i in range(columnCount):
            if not i == 1:
                self.twRealState.setColumnWidth(i, 103)
            else:
                self.twRealState.setColumnWidth(i, 108)
            self.twRealState.setHorizontalHeaderItem(i, QTableWidgetItem().setBackground(Qt.red))
        # Header 설정
        columnLables = ['구 분', '종목코드', '현재가', '포지션', '보유수량', '진입가', '청산가',
                    '손절가', '평가손익', '통화코드']
        self.twRealState.setHorizontalHeaderLabels(columnLables) # QTableWidget.setHorizontalHeaderLabels(self, QStringList lables)

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
        sScrNo = self.sScrNo
        items = ''
        for item in self.itemInfo:
            items += item.GetCode() + ';'
            try:
                self.Logging('Requesting [{}] infomation'.format(item.GetCode()))
                self.kiwoom.SetInputValue('종목코드', item.GetCode())
                self.Logging('[Input Value] sRQName = {0}, sTrCode = {1}, sScrNo = {2}'.format(sRQName, sTrCode, sScrNo))
                errorCode = self.kiwoom.CommRqData(sRQName, sTrCode, '', sScrNo)
                if errorCode:
                    self.Logging('[Error] Code = {} in_SetItemInfo'.format(errorCode))
                self.Logging('Requested [{}] infomation'.format(item.GetCode()))
            except Exception as error:
                self.Logging('[Exception] {} in _SetItemInfo'.format(error))
        self.SettwRealState()
        try:
            sRQName = '관심종목조회'
            sTrCode = TrList.OPT['TR_OPT10005']
            self.kiwoom.SetInputValue('종목코드', items)
            errorCode = self.kiwoom.CommRqData(sRQName, sTrCode, '', sScrNo)
            if errorCode:
                self.Logging('[Error] Code = {} in_SetItemInfo'.format(errorCode))
        except Exception as error:
            self.Logging('[Exception] {} in _SetItemInfo'.format(error))

    def ReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        self.Logging("[Event] OnReceiveTrData")
        self.Logging("sScrNo : {}".format(sScrNo))
        self.Logging("sRQName : {}".format(sRQName))
        self.Logging("sTrCode : {}".format(sTrCode))
        self.Logging("sRecordName : {}".format(sRecordName))
        self.Logging("sPrevNext : {}".format(sPrevNext))
        self.Logging("MainWindow")
        if sRQName == '종목정보조회':
            if sTrCode == TrList.OPT["TR_OPT10001"]:
                try:
                    nIndex = self.dicItemInfo[sPrevNext.split(' ')[0][2:8]]
                    for singleData in self.itemInfo[nIndex].singleData:
                        sValue = self.kiwoom.GetCommData(sTrCode, sRQName, 0, singleData[0]).strip()
                        self.itemInfo[nIndex].SetSingleData(singleData[0], sValue) # 종목별 SingleData 입력
                        # self.Logging("{} : {}".format(singleData[0], self.itemInfo[nIndex].GetSingleData(singleData[0])))
                except Exception as error:
                    self.Logging("[Exception][종목정보조회] {} in ReceiveTrData ".format(error))


    def ReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        self.Logging("[Event] ReceiveRealData")
        self.Logging("sJongmokCode : {}".format(sJongmokCode))
        self.Logging("sRealType : {}".format(sRealType))
        self.Logging("sRealData : {}".format(sRealData))
        if sRealType == "해외옵션호가" or sRealType == "해외선물호가":
            try:
                nIndex = self.dicItemInfo[sJongmokCode]
                for realFid in self.itemInfo[nIndex].dicRealHoga.keys():
                    sValue = self.kiwoom.GetCommRealData(sRealType, realFid).strip()
                    self.itemInfo[nIndex].SetRealHoga(realFid, sValue)
                    # self.Logging("[{0}] : {1}".format(realFid, self.itemInfo[nIndex].GetRealHoga(realFid))) # 입력 확인
            except Exception as error:
                self.Logging("[해외옵션선물호가][Exception] {} in ReceiveRealData".format(error))
        elif sRealType == "해외옵션시세" or sRealType == "해외선물시세":
            try:
                nIndex = self.dicItemInfo[sJongmokCode]
                for realFid in self.itemInfo[nIndex].dicRealMarketPrice.keys():
                    sValue = self.kiwoom.GetCommRealData(sRealType, realFid).strip()
                    self.itemInfo[nIndex].SetRealMarketPrice(realFid, sValue)
                    # self.Logging("[{0}] : {1}".format(realFid, self.itemInfo[nIndex].GetRealMarketPrice(realFid))) # 입력 확인
                self.SettwRealState(nIndex)
            except Exception as error:
                self.Logging("[해외옵션선물시세][Exception] {} in ReceiveRealData".format(error))


    def EventConnect(self, nErrCode):
        # 서버와 연결되거나 해제되었을 경우 발생되는 이벤트 처리 메소드
        try:
            # nErrCode(0 : 접속, 음수값 : 오류)
            if nErrCode == ErrorCode.OP_ERR_NONE:
                self.Logging('Successed login')
                self.Logging('Loading login infomation')
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
                    self.Logging('[Error1]'+str(error)+' in EventConnect')
                finally:
                    print(msg)

        except Exception as error:
            self.Logging('[Error2]'+str(error)+' in EventConnect')

        finally:
            try:
                self.loginEventLoop.exit()
            except AttributeError:
                pass

    # 관심종목 및 실시간 거래 내역을 확인하는 테이블 설정
    def SettwRealState(self, nIndex = -1):
        self.Logging("setting twRealState")
        # 프로그램 실행 및 설정이 변경 되었을 경우 초기화과정
        try:
            if nIndex < 0 or nIndex > 3:
                for i in range(10):
                    for key in self.dicItemInfo.keys():
                        if not (i == 0 or i == 1 or i == 9):
                            self.twRealState.setItem(nIndex, i, QTableWidgetItem(''))
                        else:
                            row = self.dicItemInfo[key]
                            self.twRealState.setItem(row, 0, QTableWidgetItem('시세감시'))
                            self.twRealState.setItem(row, 1, QTableWidgetItem(key))
                            self.twRealState.setItem(row, 9, QTableWidgetItem('USD'))
                for i in range(10):
                    if i == 0 or i == 1 or i == 9:
                        continue
                    else:
                        if i == 2:
                            for key in self.dicItemInfo.keys():
                                row = self.dicItemInfo[key]
                                currentPrice = self.itemInfo[row].GetSingleData("현재가")
                                color, price = self.GetPriceForm(currentPrice)
                                self.twRealState.setItem(row, 2, QTableWidgetItem(price))
                                self.twRealState.item(row, 2).setForeground(QBrush(color))
            else:
                for i in range(10):
                    if i == 2:
                        currentPrice = self.itemInfo[nIndex].GetSingleData("현재가(진법)")
                        color, price = self.GetPriceForm(currentPrice)
                        if self.twRealState.item(nIndex, 2) != currentPrice:
                            self.twRealState.setItem(nIndex, 2, QTableWidgetItem(price))
                            self.twRealState.item(nIndex, 2).setForeground(QBrush(color))
        except Exception as error:
            self.Logging("[Exception] {} in SettwRealState".format(error))

    def GetPriceForm(self, sValue):
        if sValue[0:1] == '-':
            return Qt.blue, sValue[1:]
        elif sValue[0:1] == '+':
            return Qt.red, sValue[1:]
        else:
            return Qt.black, sValue

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
        # 테스트 버튼
        self.Logging('This is test')
        sRQName = "종목정보조회"
        sTrCode = TrList.OPT["TR_OPT10001"]
        sScrNo = self.sScrNo
        try:
            self.kiwoom.SetInputValue("종목코드", "CLG18")
            errorCode = self.kiwoom.CommRqData(sRQName, sTrCode, '', sScrNo)
            if errorCode:
                self.Logging('[ErrorCode] {} in _SetItemInfo'.format(errorCode))
        except Exception as error:
            self.Logging("[Exception] {} in ClickedTest".format(error))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('fusion'))  # 어플리케이션 기본 디자인 설정 "Fusion"

    autoTradeMain = AutoTradeMain()
    sys.exit(app.exec_())
