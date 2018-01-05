from KFOpenAPI import *

class ItemInfo(object):
    def __init__(self):
        self.sCode = None
        self.dicCode = None
        self.dicSingleData = {}
        self.dicMultiData = {}
        self.dicRealHoga = {}
        self.dicRealMarketPrice = {}
        self.singleData = []
        self.multiData = []
        self._SetData()

    def SetCode(self, sCode, nIndex):
        self.sCode = sCode
        self.dicCode = nIndex

    def GetCode(self):
        return self.sCode

    def _SetData(self):
        # 종목 정보 조회시
        singleList = ("현재가", "대비기호", "전일대비", "등락율", "거래량", "거래량대비", "종목명", "행사가",
                    "시가", "고가", "저가", "2차저항", "1차저항", "피봇", "1차저지", "2차저지", "호가시간",
                    "매도수량대비5", "매도건수5", "매도수량5", "매도호가5", "매도등락율5",
                    "매도수량대비4", "매도건수4", "매도수량4", "매도호가4", "매도등락율4",
                    "매도수량대비3", "매도건수3", "매도수량3", "매도호가3", "매도등락율3",
                    "매도수량대비2", "매도건수2", "매도수량2", "매도호가2", "매도등락율2",
                    "매도수량대비1", "매도건수1", "매도수량1", "매도호가1", "매도등락율1",
                    "매수호가1", "매수등락율1", "매수수량1", "매수건수1", "매수수량대비1",
                    "매수호가2", "매수등락율2", "매수수량2", "매수건수2", "매수수량대비2",
                    "매수호가3", "매수등락율3", "매수수량3", "매수건수3", "매수수량대비3",
                    "매수호가4", "매수등락율4", "매수수량4", "매수건수4", "매수수량대비4",
                    "매수호가5", "매수등락율5", "매수수량5", "매수건수5", "매수수량대비5",
                    "매도호가총건수", "매도호가총잔량", "순매수잔량", "매수호가총잔량", "매수호가총건수",
                    "매도호가총잔량직전대비", "매수호가총잔량직전대비", "상장중최고가", "상장중최고대비율",
                    "상장중최고일", "상장중최저가", "상장중최저대비율", "상장중최저일", "결제통화", "품목구분",
                    "틱단위", "틱가치", "시작시간", "종료시간", "전일종가", "정산가", "영업일자", "최종거래",
                    "잔존만기", "결제구분", "레버리지", "옵션타입", "거래소", # 조회 데이터
                    "매도호가", "매수호가", "매도호가총잔량대비", "매수호가총잔량대비", "호가순잔량", # 실시간 호가
                    "체결시간", "현재가(진법)", "체결량", "전일대비기호", "전일거래량등락율", "체결일자")
        multiList = ("체결시간n", "현재가n", "대비기호n", "전일대비n", "등락율n", "체결량n", "누적거래량")
        for i in range(len(singleList)):
            self.dicSingleData.update({singleList[i]:i})
            self.singleData.append([singleList[i], ""])
        for i in range(len(multiList)):
            self.dicMultiData.update({multiList[i]:i})
            self.multiData.append([multiList[i], ""])

        # 실시간 조회시
        realHogaList = (21, 27, 28, 41, 61, 81, 101, 51, 71, 91, 111, 42, 62, 82, 102, 52, 72, 92, 112,
                        43, 63, 83, 103, 53, 73, 93, 113, 44, 64, 84, 104, 54, 74, 94, 114, 45, 65, 85, 105,
                        55, 75, 95, 115, 121, 122, 123, 125, 126, 127, 137, 128, 600, 601, 602, 603, 604,
                        610, 611, 612, 613, 614)
        realMarketPrice = (20, 10, 140, 11, 12, 27, 28, 15, 13, 16, 17, 18, 25, 26, 30, 22, 761)
        try:
            for fid in realHogaList:
                self.dicRealHoga.update({fid:RealFidList.FIDLIST["해외선물옵션호가"][fid]})
            for fid in realMarketPrice:
                self.dicRealMarketPrice.update({fid:RealFidList.FIDLIST["해외선물옵션시세"][fid]})
        except Exception as error:
            print("[KeyError]", error , "is wrong value by ItemInfo._SetData")
            raise error

    def SetSingleData(self, sKey, sValue):
        if not (isinstance(sKey, str)
                and isinstance(sValue, str)):
            print("Error : ParameterTypeError by ItemInfo.SetData")
            raise ParameterTypeError()

        try:
            index = self.dicSingleData[sKey]
            self.singleData[index][1] = sValue
        except KeyError as e:
            print("[KeyError]", e , "is wrong value by ItemInfo.SetData")
            raise e

    def GetSingleData(self, sKey):
        if not (isinstance(sKey, str)):
            print("Error : ParameterTypeError by ItemInfo.GetData")
            raise ParameterTypeError()

        try:
            index = self.dicSingleData[sKey]
            return self.singleData[index][1]
        except KeyError as e:
            print("[KeyError]", e , "is wrong value by ItemInfo.GetData")
            raise e

    def SetRealHoga(self, nKey, sValue):
        try:
            sKey = self.dicRealHoga[nKey]
            self.SetSingleData(sKey, sValue)
        except Exception as error:
            raise error

    def GetRealHoga(self, nKey):
        try:
            sKey = self.dicRealHoga[nKey]
            return self.GetSingleData(sKey)
        except Exception as error:
            raise error

    def SetRealMarketPrice(self, nKey, sValue):
        try:
            sKey = self.dicRealMarketPrice[nKey]
            self.SetSingleData(sKey, sValue)
        except Exception as error:
            raise error

    def GetRealMarketPrice(self, nKey):
        try:
            sKey = self.dicRealMarketPrice[nKey]
            return self.GetSingleData(sKey)
        except Exception as error:
            raise error
