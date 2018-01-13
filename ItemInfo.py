from KFOpenAPI import *
import datetime

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
        self.chart = ChartData()
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
            nIndex = self.dicSingleData[sKey]
            self.singleData[nIndex][1] = sValue
        except KeyError as error:
            print("[KeyError]", error , "is wrong value by ItemInfo.SetData")
            raise error

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

    # 실시간 호가(호가 주문이 변경되었을 때 반영)
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

    # 현재 시세(거래가 발생할 때 갱신)
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



# chart형 클래스 사용하지 않음
class ChartData(object):
    def __init__(self):
        self.tickChartData = []
        self.dicTickChartData = {}
        self.dayChartData = []
        self.dicDayChartData = {}
        self.multiChartData = []
        self.timeSize = ''
        self.tickCount = 0 # 틱 카운터 초기화
        self.countUnit = 1 # 틱단위
        self.timeUnit = 1 # 분단위
        self.nVolume = 0
        self.expend = False # 차트 데이터를 축적 할 것인지 판단(최초 600개 데이터를 수신하였다면, False : 600개 유지, True : 추가)
        self.InitChartData()
        self.SetDate()

    def InitChartData(self):
        chartDataList = ("현재가", "시가", "고가", "저가", "거래량", "체결시간", "영업일자")
        for i in range(len(chartDataList)):
            self.dicTickChartData.update({chartDataList[i]:i})
            self.tickChartData.append([chartDataList[i], ""])
        chartDataList = ("현재가", "시가", "고가", "저가", "누적거래량", "일자", "영업일자")
        for i in range(len(chartDataList)):
            self.dicDayChartData.update({chartDataList[i]:i})
            self.dayChartData.append([chartDataList[i], "")

    def ResetChartData(self, sTrCode, nCount):
        '''
        sTrCode : 차트데이터 요청 틱, 분, 일, 주, 월
        nCount : 반환되는 카운터 개수(메모리 할당)
        '''
        try:
            if not (isinstance(sTrCode, str)
                    and isinstance(nCount, int)):
                print("Error : ParameterTypeError by ResetChartData")
                raise ParameterTypeError()

            self.multiChartData.clear()

            if sTrCode == TrList.OPC['TR_OPC10001'] or sTrCode == TrList.OPC['TR_OPC10002']:
                for i in range(len(self.tickChartData)):
                    self.tickChartData[i][1] = ''
                for i in range(nCount):
                    self.multiChartData.append(self.tickChartData)
            else:
                for i in range(len(self.dayChartData)):
                    self.dayChartData[i][1] = ''
                for i in range(nCount):
                    self.multiChartData.append(self.dayChartData)

        except Exception as error:
            raise error

    def SetChartData(self, sTrCode, nIndex, sKey, sValue):
        '''
        nIndex = 단위별 차트 구분 번호 0 : 가장 최신
        sKey =  (tickChartData) 현재가, 시가, 고가, 저가, 거래량, 체결시간, 영업일자
                (dayChartData) 현재가, 시가, 고가, 저가, 누적거래량, 일자, 영업일자
        sValue = 입력 데이터(String)
        '''
        try:
            if not (isinstance(sTrCode, str)
                    and isinstance(nIndex, int)
                    and isinstance(sKey, str)
                    and isinstance(sValue, str)):
                print("Error : ParameterTypeError by SetChartData")
                raise ParameterTypeError()

            self.SetDate() # 시간 설정

            if sTrCode == TrList.OPC['TR_OPC10001'] or sTrCode == TrList.OPC['TR_OPC10002']:
                seIndex = self.dicTickChartData[sKey]
                self.multiChartData[nIndex][seIndex][1] = sValue
            else:
                seIndex = self.dicDayChartData[sKey]
                self.multiChartData[nIndex][seIndex][1] = sValue
        except Exception as error:
            raise error

    def SetRealChartData(self, sPrice, sVolume):
        tNow = datetime.datetime.now()
        if self.timeSize == '틱':
            self.tickChartData = self.multiChartData[0]
            self.tickChartData[self.dicTickChartData['현재가']] = sPrice
            if self.tickCount == self.countUnit:
                self.tickCount = 0
                self.nVolume = int(sVolume)
                self.tickChartData[self.dicTickChartData['시가']] = sPrice
                self.tickChartData[self.dicTickChartData['고가']] = sPrice
                self.tickChartData[self.dicTickChartData['저가']] = sPrice
                self.tickChartData[self.dicTickChartData['거래량']] = sVolume
                self.tickChartData[self.dicTickChartData['체결시간']] = tNow.strftime('%Y%m%d%H%M%S')
                if not extend:
                    self.multiData.pop()
                self.multiData.insert(self.tickChartData)
            else:
                self.tickCount += 1
                self.nVolume += int(sVolume)
                self.tickChartData[self.dicTickChartData['거래량']] = str(nVolume)

        elif self.timeSize == '분': # 분단위 데이터도 틱차트 데이터 사용
            self.tickChartData = self.multiChartData[0]
            self.tickChartData[self.dicTickChartData['현재가']] = sPrice
            if tNow.minute % self.timeUnit == 0 and self.tDateTime.minute != tNow.minute:
                self.nVolume = int(sVolume)
                self.tickChartData[self.dicTickChartData['시가']] = sPrice
                self.tickChartData[self.dicTickChartData['고가']] = sPrice
                self.tickChartData[self.dicTickChartData['저가']] = sPrice
                self.tickChartData[self.dicTickChartData['거래량']] = sVolume
                self.tickChartData[self.dicTickChartData['체결시간']] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                if not extend:
                    self.multiData.pop()
                self.multiData.insert(self.tickChartData)
            else:
                self.nVolume += int(sVolume)
                self.tickChartData[self.dicTickChartData['거래량']] = str(nVolume)

        else: # 일, 주, 월단위 데이터
            self.dayChartData = self.multiChartData[0]
            self.dayChartData[self.dicDayChartData['현재가']] = sPrice
            if self.tDateTime.day != tNow.day:
                self.nVolume = int(sVolume)
                self.dayChartData[self.dicDayChartData['시가']] = sPrice
                self.dayChartData[self.dicDayChartData['고가']] = sPrice
                self.dayChartData[self.dicDayChartData['저가']] = sPrice
                self.dayChartData[self.dicDayChartData['누적거래량']] = sVolume
                self.dayChartData[self.dicDayChartData['일자']] = datetime.datetime.now().strftime('%Y%m%d')
                if not extend:
                    self.multiData.pop()
                self.multiData.insert(self.tickChartData)
            else:
                self.nVolume += int(sVolume)
                self.tickChartData[self.dicDayChartData['누적거래량']] = str(nVolume)

        self.SetDate()

    def SetOption(self, sTrCode, nUnit = datetime.datetime.now().strftime('%Y%m%d')):
        '''
        차트의 종류를 설정함
        sTrCode : 틱, 분, 일, 주, 월
        nUnit : 틱, 분(시간 단위), 일, 주, 월(조회 일자)
        '''
        if sTrCode == TrList.OPC['TR_OPC10001']: # 틱단위
            if not (isinstance(sTrCode, str) and isinstance(nUnit, int)):
                print("Error : ParameterTypeError by SetOption tick")
                raise ParameterTypeError()
            self.timeSize = '틱'
            self.tickCount = 0
            self.countUnit = nUnit
        elif sTrCode == TrList.OPC['TR_OPC10002']: # 분단위
            if not (isinstance(sTrCode, str) and isinstance(nUnit, int)):
                print("Error : ParameterTypeError by SetOption minute")
                raise ParameterTypeError()
            self.timeSize = '분'
            self.timeUnit = nUnit
        else:
            if not (isinstance(sTrCode, str) and isinstance(nUnit, datetime.datetime)):
                print("Error : ParameterTypeError by SetOption day, month, year")
                raise ParameterTypeError()
            if sTrCode == TrList.OPC['TR_OPC10003']: #일단위
                self.timeSize = '일'
                self.lastDate = nUnit
            elif sTrCode == TrList.OPC['TR_OPC10004']: #주단위
                self.timeSize = '주'
            elif sTrCode == TrList.OPC['TR_OPC10005']: #월단위
                self.timeSize = '월'

    def GetTickChartData(self, nIndex):
        if len(multiChartData) != 0:
            for i in range(len(self.tickChartData)):
                self.tickChartData[i][1] = self.multiChartData[nIndex][i][1]
            return self.tickChartData
        else:
            raise ReturnValueError()

    def GetDaykChartData(self, nIndex):
        if len(multiChartData) != 0:
            for i in range(len(self.dayChartData)):
                self.dayChartData[i][1] = self.multiChartData[nIndex][i][1]
            return self.tickChartData
        else:
            raise ReturnValueError()

    def SetDate(self, tDateTime = datetime.datetime.now()):
        # 시간값을 설정해주는 메소드
        if type(tDateTime) == datetime.datetime:
            self.tDateTime = tDateTime
            self.sDateTime = tDateTime.strftime('%Y%m%d%H%M%S')
            self.sDate = tDateTime.strftime('%Y%m%d')
            self.sTime = tDateTime.strftime('%H%M%S')
        elif type(tDateTime) == str:
            if len(tDateTime) == 14:
                self.tDate = datetime.datetime.strptime(tDateTime, '%Y%m%d%H%M%S')
            elif len(tDateTime) == 8: # YYYYMMDD
                self.tDate = datetime.datetime.strptime(tDateTime, '%Y%m%d')
            elif len(tDateTime) == 6: # HHMMSS
                self.sTime = datetime.datetime.strptime(tDateTime, '%H%M%S')
            else:
                raise ParameterValueError()

class ReturnValueError(Exception):
    """ 리턴값이 없을 경우 발생하는 에러 """

    def __init__(self, msg="등록된 차트 데이터가 없습니다."):
        self.msg = msg

    def __str__(self):
        return self.msg
