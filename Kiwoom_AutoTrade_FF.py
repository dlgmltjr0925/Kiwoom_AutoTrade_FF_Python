import sys, os.path
from KFOpenAPI import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

root_dir = os.getcwd() # 작업 최상위 디렉토리
AutoTradeMainForm = uic.loadUiType(root_dir + "\kiwoom_autotrade_ff.ui")[0]

class AutoTradeMain(QMainWindow, AutoTradeMainForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.kfo = KFOpenAPI()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    autoTradeMain = AutoTradeMain()
    sys.exit(app.exec_())
