from KFOpenAPI import *

class AccountInfo(KFOpenAPI):
    def __init__(self, KFOpenAPI):
        super().__init__()
        self.loginInfo = LoginInfo()
        self.KFOpenAPI = KFOpenAPI

    def SetConnectState(self, bState):
        if bState:
            self.loginInfo.connectState = bState
        else:
            self.loginInfo = LoginInfo()
    def GetConnectState(self):
        return self.loginInfo.connectState

    def SetLoginInfo(self):
        # EventConnect 함수 내에서 동작
        self.loginInfo.accountCnt = self.GetLoginInfo(self.loginInfo.setList[0])
        self.loginInfo.accNo = self.GetLoginInfo(self.loginInfo.setList[1]).split(';')
        self.loginInfo.userId = self.GetLoginInfo(self.loginInfo.setList[2])
        self.loginInfo.userName = self.GetLoginInfo(self.loginInfo.setList[3])
        self.loginInfo.keySecGb = self.GetLoginInfo(self.loginInfo.setList[4])
        self.loginInfo.fwSecGb = self.GetLoginInfo(self.loginInfo.setList[5])

    def GetLoginInfo(self, sTag):
        return self.KFOpenAPI.dynamicCall("GetLoginInfo(QString)", sTag)

class LoginInfo(object):
    def __init__(self):
        self.connectState = False
        self.accountCnt = 0
        self.accNo = []
        self.userId = None
        self.userName = None
        self.keySecGb = 0      # 0 : 정상,   1 : 해지
        self.fwSecGb = 0       # 0 : 미설정, 1 : 설정, 2 : 해지
        self.setList = ["ACCOUNT_CNT", "ACCNO", "USER_ID", "USER_NAME", "KEY_BSECGB", "FIREW_SECGB"]
