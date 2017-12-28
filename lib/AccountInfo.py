from lib.KFOpenAPI import *
from lib.ItemInfo import *

class AccountInfo(KFOpenAPI):
    def __init__(self):
        super().__init__()
        self.loginInfo = LoginInfo()
        self.CommConnect() # 로그인창 출력
        self.OnEventConnect.connect(self.EventConnect)

    def EventConnect(self, errorCode):
        if errorCode == 0:
            print("초기설정")
        else:
            print(errorCode)

    def SetLoginInfo(self):
        print("set")

class LoginInfo(object):
    def __init_(self):
        self.accountCnt = 0
        self.accNo = []
        self.userId = None
        self.userName = None
        self.keySecGb = 0      # 0 : 정상,   1 : 해지
        self.fwSecGb = 0       # 0 : 미설정, 1 : 설정, 2 : 해지
        self.setList = ["ACCOUNT_CNT", "ACCNO", "USER_ID", "USER_NAME", "KEY_BSECGB", "FIREW_SECGB"]

if __name__ == "__main__":
    accountInfo = AccountInfo()
