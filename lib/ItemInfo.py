from lib.KFOpenAPI import *

class ItemInfo(KFOpenAPI):
    def __init__(self):
        super().__init__()
        self.dicSingleData = {}
        self.dicMultiData = {}
        self.singleData = []
        self.multiData = []
        self._SetData()

    def _SetData(self):
        singleList = ("현재가", "대비기호", "전일대비", "등락률", "거래량", "거래량대비", "종목명", "행사가",
                    "시가", "고가", "저가", "2차저항", "1차저항", "피봇", "1차저지", "2차저지", "호가시간",
                    "매도수량대비5", "매도건수5", "매도수량5", "매도호가5", "매도등락률5",
                    "매도수량대비4", "매도건수4", "매도수량4", "매도호가4", "매도등락률4",
                    "매도수량대비3", "매도건수3", "매도수량3", "매도호가3", "매도등락률3",
                    "매도수량대비2", "매도건수2", "매도수량2", "매도호가2", "매도등락률2",
                    "매도수량대비1", "매도건수1", "매도수량1", "매도호가1", "매도등락률1",
                    "매수호가1", "매수등략율1", "매수수량1", "매수건수1", "매수수량대비1",
                    "매수호가2", "매수등략율2", "매수수량2", "매수건수2", "매수수량대비2",
                    "매수호가3", "매수등략율3", "매수수량3", "매수건수3", "매수수량대비3",
                    "매수호가4", "매수등략율4", "매수수량4", "매수건수4", "매수수량대비4",
                    "매수호가5", "매수등략율5", "매수수량5", "매수건수5", "매수수량대비5",
                    "매도호가총건수", "매도호가총잔량", "순매수잔량", "매수호가총잔량", "매수호가총건수",
                    "매도호가총잔량직전대비", "매수호가총잔량직전대비", "상장중최고가", "상장중최고대비율",
                    "상장중최고일", "상장중최저가", "상장중최저대비율", "상장중최저일", "결제통화", "품목구분"
                    "틱단위", "틱가치", "시작시간", "종료시간", "전일종가", "정산가", "영업일자", "최종거래"
                    "잔존만기", "결제구분", "실물인수도", "레버리지", "옵션타입", "거래소")
        multiList = ("체결시간n", "현재가n", "대비기호n", "전일대비n", "등락률n", "체결량n", "누적거래량")
        for i in range(len(singleList)):
            self.dicSingleData.update({singleList[i]:i})
            self.singleData.append([singleList[i], ""])
        for i in range(len(multiList)):
            self.dicMultiData.update({multiList[i]:i})
            self.multiData.append([multiList[i], ""])

    def SetSingleData(self, sKey, sValue):
        if not (isinstance(sKey, str)
                and isinstance(sValue, str)):
            print("Error : ParameterTypeError by ItemInfo.SetData")
            raise ParameterTypeError()

        try:
            index = self.dicSingleData[sKey]
        except KeyError as e:
            print("[KeyError]", e , "is wrong value by ItemInfo.SetData")
        else:
            print("Not Error")
            self.singleData[index][1] = sValue


    def GetSingleData(self, sKey):
        if not (isinstance(sKey, str)):
            print("Error : ParameterTypeError by ItemInfo.GetData")
            raise ParameterTypeError()

        try:
            index = self.dicSingleData[sKey]
        except KeyError as e:
            print("[KeyError]", e , "is wrong value by ItemInfo.GetData")
            return e
        else:
            print("Not Error")
            return self.singleData[index][1]

if __name__ == "__main__":
    itemInfo = ItemInfo()
    itemInfo.SetSingleData("현재가", "100")
    print("출력 :", itemInfo.GetSingleData("현재가"))
