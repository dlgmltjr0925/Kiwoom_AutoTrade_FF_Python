class VerificationTrade(object):
    def __init__(self, code = None):
        # 현재 가격
        self.currentPrice = None
        # 진입 가격, 포지션,
        self.openPrice = None
        self.openPosition = None
        # 청산 가격
        self.closePrice = None
        # 스탑 로스
        self.tickCount = 15 
        self.lossPrice = None
        # 거래 상태
        self.noPosition = True         # No position(진입가 탐색)
        self.waitOpenPosition = False  # Wait open position(진입 대기)
        self.openPosition = False      # Open position(진입 / 청산가 탐색)
        self.waitClosePosition = False # Wait close position(진입 / 청산 대기)
        # 계좌 정보
        self.tradingProfit = None   # 거래 수익
        self.realizedProfit = None  # 실현 손익
        # 종목 정보
        self.SetCodeInfo(code)

    def SetCodeInfo(self, code):
        self.dicTickSize = {'CL':0.01, 'ES':0.25, 'GC':0.01}
        self.dicTickValue = {'CL':10.0, 'ES':12.5, 'GC':10.0}
        self.tickSize = None
        self.tickValue = None
        self.commission = 7.5        # 수수료
        if not code == None:
            code = code[:2]
            self.tickSize = self.dicTickSize[code]
            self.tickValue = self.dicTickValue[code]

    def Trading(self, price, position = None, order = None):
        if self.noPosition:
            print('No position')

        elif self.waitOpenPosition:
            print('Wait open position')

        elif self.waitPosition:
            print('Wait position')

        else:
            print('waitClosePosition')
