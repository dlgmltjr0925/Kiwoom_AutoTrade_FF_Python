from KFOpenAPI import *
from ItemInfo import *

class AccountInfo(KFOpenAPI):
    def __init__(self, KFOpenAPI):
        super().__init__()
        self.loginInfo = LoginInfo()
        self.KFOpenAPI = KFOpenAPI
        # 관심 종목 설정 (종목 정보)
        self.myItemInfo = []
        self.dicMyItems = {}
        # 계좌 정보 조회 (금액 정보)
        self.myBalance = []
        self.dicBalance = {}
        self._InitBalance()

    # 보유 종목 초기화
    def _InitBalance(self):
        balanceList = ("매도수량", "매수수량", "총평가금액", "실현수익금액", "총약정금액", "총수익율")
        for i in range(len(balanceList)):
            self.dicBalance.update({balanceList[i]:i})
            self.myBalance.append([balanceList[i], ""])

    # 연결 상태
    def SetConnectState(self, bState):
        if bState:
            self.loginInfo.connectState = bState
        else:
            self.loginInfo = LoginInfo()

    # 연결 상태 반환
    def GetConnectState(self):
        return self.loginInfo.connectState

    # 로그인 정보
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

    # 관심 종목 정보
    def InitItemInfo(self):
        for i in range(len(self.dicMyItems)):
            self.myItemInfo[i].Initialize()

    def SetItemInfo(self, itemInfo):
        self.myItemInfo = []
        nIndex = 0
        for item in itemInfo:
            self.myItemInfo.append(MyItemInfo(item))
            self.dicMyItems.update({item.sCode : nIndex})
            nIndex += 1

    def GetItemInfo(self, itemCode):
        nIndex = self.dicMyItems[itemCode]
        return self.myItemInfo[nIndex].itemCode

    def SetMyBalance(self, sKey, sValue):
        if not (isinstance(sKey, str)
                and isinstance(sValue, str)):
            print("Error : ParameterTypeError by AccountInfo.SetMyBalance")
            raise ParameterTypeError()

        try:
            nIndex = self.dicBalance[sKey]
            self.myBalance[nIndex][1] = sValue
        except KeyError as error:
            print("[KeyError]", error , "is wrong value by AccountInfo.SetMyBalance")
            raise error

    def GetMyBalance(self, sKey):
         if not (isinstance(sKey, str)):
             print("Error : ParameterTypeError by AccountInfo.GetMyBalance")
             raise ParameterTypeError()

         try:
             nIndex = self.dicBalance[sKey]
             return self.myBalance[nIndex][1]
         except KeyError as error:
             print("[KeyError]", error , "is wrong value by AccountInfo.GetMyBalance")
             raise error


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

class MyItemInfo(ItemInfo):
    def __init__(self, ItemInfo):
        self.itemInfo = ItemInfo
        self.itemCode = self.itemInfo.GetCode()                     # 종목코드
        self.itemTickSize = float(self.itemInfo.GetSingleData("틱단위"))  # Tick 단위
        self.itemTickValue = float(self.itemInfo.GetSingleData("틱가치")) # Tick당 가격
        self.Initialize()

    def Initialize(self):
        self.itemPosition = 0                                       # 진입 포지션   1 : 매수, -1 : 매도, 0 : 없음
        self.itemInsertPrice = None                                 # 진입 가격
        self.itemQuantity = 0                                       # 보유 수량
        self.itemGoalPrice = None                                   # 청산 목표가
        self.itemLossPrice = None                                   # 손절가
        self.itemEvaluationPrice = None                             # 평가손익
        self.itemGoalCount = 0                                      # 수익 실현
        self.itemLossCount = 0                                      # 손절 Tick수
        self.itemCurrentPrice = 0                                   # 현재가
        self.SetCurrentPrice()                                      # 현재가 설정
        self.itemBalance = []                                       # 잔고 정보
        self.dicBalance = {}
        self._InitBalance()

    # 잔고 데이타 초기화
    def _InitBalance(self):
        balanceList = ("매도수구분", "수량", "청산가능", "평균단가", "현재가격", "평가손익",
                        "약정금액", "평가금액", "수익율", "수수료", "통화코드")
        for i in range(len(balanceList)):
            self.dicBalance.update({balanceList[i]:i})
            self.itemBalance.append([balanceList[i], ""])

    # 잔고 데이타 설정
    def SetItemBalance(self, sKey, sValue):
        if not (isinstance(sKey, str)
                and isinstance(sValue, str)):
            print("Error : ParameterTypeError by AccountInfo.SetItemBalance")
            raise ParameterTypeError()

        try:
            nIndex = self.dicBalance[sKey]
            self.itemBalance[nIndex][1] = sValue
            if sKey == "매도수구분": # 0 : 없음, 1 : 매도, 2 : 매수
                if sValue == "1": # 매도일 경우
                    self.itemPosition = -1
                elif sValue == "2": # 매수일 경우
                    self.itemPosition = 1
                else:
                    raise InputValueError()
            elif sKey == "수량":
                self.itemQuantity = int(sValue)  # 수량 값을 정수로 입력
            elif sKey == "평균단가":
                self.itemInsertPrice = float(sValue)

        except KeyError as error:
            print("[KeyError]", error , "is wrong value by AccountInfo.SetItemBalance")
            raise error

    def GetItemBalance(self, sKey):
         if not (isinstance(sKey, str)):
             print("Error : ParameterTypeError by ItemInfo.GetItemBalance")
             raise ParameterTypeError()

         try:
             nIndex = self.dicBalance[sKey]
             return self.itemBalance[nIndex][1]
         except KeyError as error:
             print("[KeyError]", error , "is wrong value by AccountInfo.GetItemBalance")
             raise error


    def SetCurrentPrice(self):
        # 현재값 입력, 종목 보유시 평가 손익 계산
        self.itemCurrentPrice = float(self.itemInfo.GetSingleData("현재가"))
        if self.HasItem():
            self._SetEvaluationPrice()

    # 청산가 설정
    def SetGoalPrice(self, GoalCount = None):
        if HasItem():
            if GoalCount:
                self.itemGoalPrice = self.itemInsertPrice + self.itemPosition * self.itemTickSize * GoalCount
            else:
                self.itemGoalPrice = self.itemInsertPrice + self.itemPosition * self.itemTickSize * self.itemGoalCount

    # 손절가 설정
    def SetLossPrice(self, lossCount = None):
        if HasItem():
            if lossCount:
                self.itemLossPrice = self.itemInsertPrice - self.itemPosition * self.itemTickSize * lossCount
            else:
                self.itemLossPrice = self.itemInsertPrice - self.itemPosition * self.itemTickSize * self.itemLossCount

    # 평가 손익 데이터 설정
    def _SetEvaluationPrice(self):
        # 평가손익 = (현재가 - 진입 가격) * 포지션(매수 : 1, 매도 : -1) / tick 단위 * tick당 가격
        if self.HasItem():
            self.itemEvaluationPrice = (self.itemCurrentPrice - self.itemInsertPrice) * self.itemQuantity * self.itemPosition / self.itemTickSize * self.itemTickValue
            self.itemEvaluationPrice = round(self.itemEvaluationPrice, 2)

    def GetGoalPrice(self):
        if self.itemGoalPrice == None:
            return ''
        else:
            return str(self.itemGoalPrice)

    def GetLossPrice(self):
        if self.itemLossPrice == None:
            return ''
        else:
            return str(self.itemLossPrice)

    # 평가 손익 데이터 출력
    def GetEvaluationPrice(self):
        if self.itemEvaluationPrice == None:
            self._SetEvaluationPrice()
        ret = '{:.2f}'.format(self.itemEvaluationPrice)
        if self.itemEvaluationPrice > 0:
            ret = '+' + ret
        return ret

    def HasItem(self):
        if (self.itemPosition == -1 or 1) and self.itemInsertPrice != None and self.itemQuantity != 0:
            return True
        else:
            return False

class ParameterCountError(Exception):
    def __init__(self, msg="인자값의 개수가 잘못 되었습니다."):
        self.msg = msg
    def __str__(self):
        return self.msg

class ReturnValueError(Exception):
    # 리턴 값이 존재하지 않을 경우 발생하는 에러
    def __init__(self, msg="리턴값이 존재하지 않습니다."):
        self.msg = msg
    def __str__(self):
        return self.msg

class InputValueError(Exception):
    # 리턴 값이 존재하지 않을 경우 발생하는 에러
    def __init__(self, msg="입력값이 잘못 되었습니다."):
        self.msg = msg
    def __str__(self):
        return self.msg
