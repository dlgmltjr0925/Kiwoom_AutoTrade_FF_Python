import datetime

class VerificationTrade(object):
    def __init__(self, code = None, data = None):
        # 현재 가격
        self.currentPrice = None       # 현재가
        self.sellHoga = None          # 매도호가
        self.buyHoga = None           # 매수호가
        # 스탑 로스
        self.tickCount = 15
        self.lossPrice = None
        # 거래 상태
        self.noPosition = True         # No position(진입가 탐색)
        self.waitOpenPosition = False  # Wait open position(진입 대기)
        self.openPosition = False      # Open position(진입 / 청산가 탐색)
        self.waitClosePosition = False # Wait close position(진입 / 청산 대기)
        # 계좌 정보
        self.holdingItem = []          # 보유 종목 정보
        self.averagePrice = None       # 평균 단가
        self.totalVolume = None        # 보유 수량
        self.tradePosition = None      # 거래 포지션
        self.tradeProfit = None        # 거래 수익 = ((청산가 - 진입가) X 포지션(매도 : -1, 매수 : 1)) X 보유 수량
        self.realizedProfit = None     # 실현 손익 = (((청산가 - 진입가) X 포지션(매도 : -1, 매수 : 1)) - 수수료(7.5 * 2)) X 보유 수량
        # 종목 정보
        self.InitItemInfo(code)
        # 테스트 확인
        self.test = True
        # 미체결 주문 정보
        self.orderCount = 0
        self.orderInfo = {}             # 주문 정보{주문번호 : [포지션, 가격, 수량, 원주문번호]}
        # 체결 정보
        self.orderHistory = []
        self.tradeHistory = []          # 체결 내역
        # 전략 정보
        self.openPrice = None           # 진입 가격
        self.closePrice = None          # 청산 가격
        # 자동 거래 메소드 선언 시기
        self.realHoga = False
        self.realTrade = True
        # 참고 자료
        self.data = data


    def InitItemInfo(self, code):  # 종목 입력
        self.dicTickSize = {'CL':0.01, 'ES':0.25, 'GC':0.01}
        self.dicTickValue = {'CL':10.0, 'ES':12.5, 'GC':10.0}
        self.tickSize = None
        self.tickValue = None
        self.commission = 7.5        # 수수료
        if not code == None:
            code = code[:2]
            self.tickSize = self.dicTickSize[code]
            self.tickValue = self.dicTickValue[code]

    def AutoTrade(self, price = None, data = None):
        if self.realHoga or self.realTrade:
            if self.realHoga:
                self.realHoga = False:
            else:
                if not price == None:
                    self.currentPrice = price
            if self.noPosition:  # 진입가 탐색
                print('No position')

            if self.waitOpenPosition:   # 진입 대기
                print('Wait open position')

            if self.openPosition:   # 진입 / 청산가 탐색
                print('Open position')

            if self.waitClosePosition:
                print('waitClosePosition')

    def Analysis(self, price):  # 진입 가격 탐색
        if self.test:
            print('Analysis')

    def Order(self, orderType = 0, position = 1, price = None, volume = 0, originalOrderNo = 0):  # 주문
        # type      0 : 지정가신규, 1 : 시장가신규, 2 : 지정가정정, 3 : 시장가정정, 9 : 주문취소
        # position  1 : 매수, -1 : 매도
        # originalOrderNo  신규주문 : 0, 정정 : 기존 주문 번호
        if orderType == 0: # 지정가 신규
            if not (position == -1 or position == 1):
                raise '[Order] position is wrong value'
            if price == None or price < 0:
                raise '[Order] price is wrong value'
            if volume == 0:
                raise '[Order] volume is wrong value'
            # 주문번호
            orderNo = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '{:03}'.format(self.orderCount)
            self.orderCount += 1
            orderInfo = []
            # 포지션
            orderInfo.append(position)
            # 가격
            orderInfo.append(price)
            # 수량
            orderInfo.append(volume)
            # 원주문 번호
            orderInfo.append(originalOrderNo)

            self.orderInfo.update({orderNo : orderInfo})

        elif orderType == 1: # 시장가 신규
            if not (position == -1 or position == 1):
                raise '[Order] position is wrong value'
            if self.currentPrice == None or self.sellHoga == None or self.buyHoga:
                raise '[Order] price is wrong value'
            if volume == 0:
                raise '[Order] volume is wrong value'
            # 주문번호
            orderNo = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '{:03}'.format(self.orderCount)
            self.orderCount += 1
            orderInfo = []
            # 포지션
            orderInfo.append(position)
            # 가격
            if position = 1 # 매수일 경우 매도 호가
                orderInfo.append(self.sellHoga)
            else:           # 매도일 경우 매수 호가
                orderInfo.append(self.buyHoga)
            # 수량
            orderInfo.append(volume)
            # 원주문 번호
            orderInfo.append(originalOrderNo)

            self.orderInfo.update({orderNo : orderInfo})

        elif orderType == 2: # 지정가 정정
