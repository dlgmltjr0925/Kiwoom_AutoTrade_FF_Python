import sys, io, os.path
from KFOpenAPI import *
from AccountInfo import *
from ItemInfo import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

root_dir = os.getcwd() # 작업 최상위 디렉토리
AutoTradeMainForm = uic.loadUiType(root_dir + "\kiwoom_autotrade_ff.ui")[0]

class AutoTradeMain(QMainWindow, AutoTradeMainForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._SetupUi()
        self.logNumber = 0
        self.accountInfo = AccountInfo()
        self.kiwoom = Kiwoom()

    def _SetupUi(self):
        # QTableWidget Setting
        self._InitButton()
        self.show()

    # 버튼 기능을 초기화
    def _InitButton(self):
        # actionLogin 버튼
        self.actionLogin.setShortcut("Ctrl+L")
        self.actionLogin.setStatusTip("Open Login pannel")
        self.actionLogin.triggered.connect(self._TriActionLogin)
        # actionLogout 버튼
        self.actionLogout.setShortcut("Ctrl+O")
        self.actionLogout.setStatusTip("Disconnect")
        self.actionLogout.triggered.connect(self._TriActionLogout)
        # test 버튼
        self.btnTest.clicked.connect(self.ClickedTest)

    def _TriActionLogin(self):
        self.accountInfo.CommConnect(1)
        self.kiwoom.CommConnect()

    def _TriActionLogout(self):
        self.accountInfo.CommTerminate()

    def _EventConnect(self, nErrCode):
        self.Logging(accountInfo.loginInfo.accNo)
        QMessageBox.about(self, "OnEventConnect", str(nErrCode))

    def Logging(self, strData):
        try:
            if not (isinstance(strData, str)):
                strData = str(strData)
            self.lstLog.addItem("[{0:05d}] {1}".format(self.logNumber, strData))
            self.logNumber += 1
        except:
            self.Logging("error")

    def ClickedTest(self):
        self.Logging("This is test")

class Kiwoom(KFOpenAPI):
    def __init__(self):
        super().__init__()

    def EventConnect(self):
        self.loginEventLoop.exit()

    def CommConnect(self, nAutoUpgrade):
        self.dynamicCall("CommConnect(int)", nAutoUpgrade)
        self.loginEventLoop = QEventLoop()
        self.loginEventLoop.exec_()

    def _EventConnect(self, nErrCode):
        try:
            if nErrCode == ErrorCode.OP_ERR_NONE:
                self._SetLoginInfo()
            else:
                try:
                    msg = ErrorCdoe.CAUSE[nErrCode]
                except KeyError as error:
                    QMessageBox.about(self,"EventConnect", str(error))
                finally:
                    print(msg)

        except Exception as error:
            QMessageBox.about(self,"EventConnect", str(error))

        finally:
            try:
                self.loginEventLoop.exit()
            except AttributeError:
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    autoTradeMain = AutoTradeMain()
    sys.exit(app.exec_())
