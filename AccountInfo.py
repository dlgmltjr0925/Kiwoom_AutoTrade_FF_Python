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
        # 주문 정보 조회
        self.orderInfo = {} # 주문 번호에 맞는 주문 정보

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

    def InitOrderInfo(self):
        self.orderInfo.clear()

    def AddOrderInfo(self, sOrderNo, sOriginalOrderNo = '000000000000000'):
        try:
            if not sOrderNo in self.orderInfo.keys():
                # 원주문 번호가 0이면 신규
                if sOriginalOrderNo == '000000000000000':
                    self.orderInfo.update({sOrderNo:OrderInfo()})
                else: # 원주문 번호에 번호가 있다면..
                    if sOriginalOrderNo in self.orderInfo.keys(): # 등록된 정보가 있다면
                        self.orderInfo.pop(sOriginalOrderNo)
                    self.orderInfo.update({sOrderNo:OrderInfo()})
        except KeyError as error:
            print("[KeyError]", error , "is wrong value by AccountInfo.SetOrderInfo")
            raise error

    def SetOrderInfo(self, sOrderNo, sKey, sValue):  # 주문 정보를 입력
        try:
            self.orderInfo[sOrderNo].SetOrderData(sKey, sValue)
        except KeyError as error:
            print("[KeyError]", error , "is wrong value by AccountInfo.SetOrderData")
            raise error

    def GetOrderInfo(self, sOrderNo, sKey = None):   # 주문 정보(세부정보)를 반환
        try:
            if sKey == None:
                return self.orderInfo[sOrderNo]
            else:
                return self.orderInfo[sOrderNo].GetOrderData(sKey)
        except Exception as error:
            print("[KeyError]", error , "is wrong value by AccountInfo.GetOrderInfo")
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

# 보유 정보 \
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
        if (self.itemPosition == -1 or self.itemPosition == 1) and self.itemInsertPrice != None and self.itemQuantity != 0:
            return True
        else:
            return False

class OrderInfo(object):
    def __init__(self):                          # 주석 매수 신규 주문 기준
        self.orderNo = ''                        # 주문번호 = 000000002011364
        self.code = ''                           # 종목코드 = 6EH18
        self.orderType = ''                      # 주문유형 = 2 (2: 지정가)
        self.position = ''                       # 매도수구분 = 2 (1 : 매도, 2: 매수)
        self.orderCount = 0                      # 주문수량 = 000000001
        self.conclusionOrder = 0                 # 체결수량 = 000000000
        self.outstandingOrder = 0                # 미체결수량 = 000000001
        self.orderPrice = 0.0                    # 주문표시가격 = 1.22550
        self.orderPriceInt = 0                   # 주문가격 = 00000000122550
        self.conditionPrice = 0                  # 조건표시가격 =
        self.conditionType = 0                   # 상태구분 = 1(1: 신규, 2: 정정)
        self.currencyCode = 'USD'                # 통화코드 = USD
        self.orderTime = datetime.datetime.now() # 주문시각 = 01/15 16:57:10
        self.originalOrderNo = ''                # 원주문번호 = 000000000000000
        self.orderData = []
        self.dicOrderData = {}
        self.InitOrderData()

    def InitOrderData(self):
        orderList = ('주문번호', '종목코드', '주문유형', '매도수구분', '주문수량',
                        '체결수량', '미체결수량', '주문표시가격', '주문가격', '조건표시가격',
                        '상태구분', '통화코드', '주문시각', '원주문번호')
        for i in range(len(orderList)):
            self.orderData.append([orderList[i], ''])
            self.dicOrderData.update({orderList[i]: i})

    def SetOrderData(self, sKey, sValue):
        if not (isinstance(sKey, str) and isinstance(sValue, str)):
            print("Error : ParameterTypeError by OrderInfo.SetOrderData")
            raise ParameterTypeError()

        try:
            print('sKey : {}, sValue : {}'.format(sKey, sValue))
            nIndex = self.dicOrderData[sKey]
            self.orderData[nIndex][1] = sValue
            if sKey == '주문번호':
                self.orderNo = sValue
            elif sKey == '종목코드':
                self.code = sValue
            elif sKey == '주문유형':
                self.orderType = int(sValue)
            elif sKey == '매도수구분':
                if sValue == '1': # 매도
                    self.position = -1
                elif sValue == '2': # 매수
                    self.position = 1
            elif sKey == '주문수량':
                self.orderCount = int(sValue)
            elif sKey == '체결수량':
                self.conclusionOrder = int(sValue)
            elif sKey == '미체결수량':
                self.outstandingOrder = int(sValue)
            elif sKey == '주문표시가격':
                self.orderPrice = float(sValue)
            elif sKey == '주문가격':
                self.orderPriceInt = int(sValue)
            elif sKey == '조건표시가격':
                if sValue != '' and sValue != None:
                    self.conditionPrice = float(sValue)
            elif sKey == '상태구분':
                self.conditionType = int(sValue)
            elif sKey == '통화코드':
                self.currencyCode = sValue
            elif sKey == '주문시각':
                sValue = str(self.orderTime.year) + '/' + sValue
                self.orderTime = datetime.datetime.strptime(sValue, '%Y/%m/%d %H:%M:%S')
            elif sKey == '원주문번호':
                self.originalOrderNo = sValue

        except KeyError as error:
            print("[KeyError]", error , "is wrong value by OrderInfo.SetOrderData")
            raise error

    def GetOrderData(self, sKey):
        if not (isinstance(sKey, str)):
            print("Error : ParameterTypeError by OrderInfo.GetOrderData")
            raise ParameterTypeError()

        try:
            nIndex = self.dicOrderData[sKey]
            return self.orderData[nIndex][1]
        except KeyError as error:
            print("[KeyError]", error , "is wrong value by OrderInfo.GetOrderData")
            raise error

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
