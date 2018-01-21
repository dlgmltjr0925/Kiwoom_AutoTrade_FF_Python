#-*- coding: utf-8 -*-
import sys, os.path, configparser, time, pymysql, datetime, threading as tr, platform
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

rootDir = os.getcwd() # 작업 최상위 디렉토리
if platform.platform()[:7] == 'Windows':
    VerificationDir = rootDir + '\Verification'
    VerificationUi = VerificationDir + '\VerificationVolume.ui'
else:
    VerificationDir = rootDir + '/Verification'
    VerificationUi = VerificationDir + '/VerificationVolume.ui'
VerificationMainForm = uic.loadUiType(VerificationUi)[0]

class VerificationMain(QMainWindow, VerificationMainForm):
    def __init__(self):
        super().__init__()
        self.logCounter = 0      # 로그 리스트 카운터
        self.db = DataBase()     # 데이터 베이스 접속 설정값
        self.dicTickSize = {'CL':0.01, 'ES':0.25, 'GC':0.1}
        self.dicTickValue = {'CL':10.0, 'ES':12.5, 'GC':10}
        self.dicTickUnit = {'CL':2, 'ES':2, 'GC':1}
        self.sCode = None
        self.hogaDB = []
        self.tradeDB = []
        self._SetTimer()
        self._SetupUi()
        self.tradeTable = TradeTable()
        self.hogaTable = HogaTable()
        self.volumeTable = VolumeTable()
        self.btnSearch.clicked.connect(self._SearchData) # 검색 버튼을 누르면 데이터 처리가 이루어진다
        self.btnStart.clicked.connect(self._PlayVerification) # 시작(>) 버튼을 누르면 데이터 처리 진행
        self.btnPause.clicked.connect(self._PauseVerification) # 일시정지(||) 버튼을 누르면 데이터 처리 중지
        self.btnStop.clicked.connect(self._StopVerification) # 정지(ㅁ) 버튼을 누르면 데이터 처리 정지(시간 초기화)
        self.chRealTime.clicked.connect(self._SetRealTime)
        self.cbCode.currentIndexChanged.connect(self._SetSearchDate)
        self.timer.timeout.connect(self._TimerProcessData)
        self.realTimer.timeout.connect(self._SetRealTime)
        # 데이터 처리를 위한 값


    def _SetTimer(self):
        self.timer = QTimer() # 타이머(데이터 동작)
        self.bTimer = False # 타이머가 작동 중이면 True, 작동중이지 않으면 False
        self.realTimer = QTimer() # 종료 시간 실시간 처리
        self.bRealTimer = False
        self.timeDelta = 1 #
        self.timeDeltaCount = 60
        self.startTime = None
        self.finishTime = None
        self.processTime = None
        self.bMajor = False # 16시를 기준으로 구분(False : 이전(분단위로 수집), True : 이후(초단위로 수집))
        self.bRealVerification = False # 실시간 검증

    # User Interface 초기화
    def _SetupUi(self):
        # QTableWidget Setting
        self.setupUi(self) # QT Creater로 생성된 기본 프레임
        self.show() # 화면 출력
        self._InitTableWidget()
        self._SetCodeList()
        self._SetSearchDate()

    def _InitTableWidget(self):
        # Setting Hoga Table Widget
        rowCount = 12
        columnCount = 7
        self.twHoga.setRowCount(rowCount)
        self.twHoga.setColumnCount(columnCount)
        for i in range(rowCount):
            self.twHoga.setRowHeight(i, 26)
        for i in range(columnCount):
            if i == 3:
                self.twHoga.setColumnWidth(i, 100)
            else:
                self.twHoga.setColumnWidth(i, 40)
        head = ('대비', '건수', '잔량', '가격(등락률)', '잔량', '건수', '대비')
        for i in range(len(head)):
            self.twHoga.setItem(0, i, QTableWidgetItem(head[i]))
        self.hogaTableIndex = (6, 7, 5, 4, 56, 10, 11, 9, 8, 55, 14, 15, 13, 12, 54, 18, 19,
                            17, 16, 53, 22, 23, 21, 20, 52, 24, 57, 25, 27, 26, 28, 58, 29, 31,
                            30, 32, 59, 33, 35, 34, 36, 60, 37, 39, 38, 40, 61, 41, 43, 42,
                            45, 46, 44, 0, 47, 49, 48)
        # Setting Trade Table Widget
        rowCount = 4
        columnCount = 8
        self.twTrade.setRowCount(rowCount)
        self.twTrade.setColumnCount(columnCount)
        for i in range(rowCount):
            self.twTrade.setRowHeight(i, 26)
        for i in range(columnCount):
            self.twTrade.setColumnWidth(i, 68)
        head = ('체결시간', '현재가(진법)', '현재가', '전일대비', '등락율', '매도호가', '매수호가',
                '체결량', '누적거래량', '시가', '고가', '저가', '기호', '거래등락율', '체결일자', '영업일')
        for i in range(len(head)):
            if i < 8:
                self.twTrade.setItem(0, i, QTableWidgetItem(head[i]))
            else:
                self.twTrade.setItem(2, i - 8, QTableWidgetItem(head[i]))

        # Setting Volume Table Widget
        if self.sCode == None:
            rowCount = 30
            columnCount = 3
            self.twVolume.setRowCount(rowCount)
            self.twVolume.setColumnCount(columnCount)
            for i in range(rowCount):
                self.twVolume.setRowHeight(i, 19)
            for i in range(columnCount):
                if i == 1:
                    self.twVolume.setColumnWidth(i, 79)
                else:
                    self.twVolume.setColumnWidth(i, 50)
            columnLables = ['매도', '가격', '매수']
            self.twVolume.setHorizontalHeaderLabels(columnLables)
        else:
            if not self.sCode == self.volumeTable.sCode:
                self.volumeTable = VolumeTable(self.sCode)
            self.twVolume.clear()
            self.twVolume.setRowCount(self.volumeTable.rowCount)
            self.twVolume.setColumnCount(self.volumeTable.columnCount)
            for i in range(self.volumeTable.rowCount):
                self.twVolume.setRowHeight(i, 19)
            for i in range(self.volumeTable.columnCount):
                if i == 1:
                    self.twVolume.setColumnWidth(i, 79)
                else:
                    self.twVolume.setColumnWidth(i, 50)
            columnLables = ['매도', '가격', '매수']
            self.twVolume.setHorizontalHeaderLabels(columnLables)
            for i in range(self.volumeTable.rowCount):
                self.twVolume.setItem(i, 0, QTableWidgetItem('{}'.format(self.volumeTable.volumeData[i][1])))
                self.twVolume.setItem(i, 2, QTableWidgetItem('{}'.format(self.volumeTable.volumeData[i][2])))
            if self.volumeTable.tickUnit == 1:
                for i in range(self.volumeTable.rowCount):
                    self.twVolume.setItem(i, 1, QTableWidgetItem('{:.01f}'.format(self.volumeTable.volumeData[i][0])))
            elif self.volumeTable.tickUnit == 2:
                for i in range(self.volumeTable.rowCount):
                    self.twVolume.setItem(i, 1, QTableWidgetItem('{:.02f}'.format(self.volumeTable.volumeData[i][0])))
            else:
                for i in range(self.volumeTable.rowCount):
                    self.twVolume.setItem(i, 1, QTableWidgetItem('{}'.format(self.volumeTable.volumeData[i][0])))

    # 종목 코드 및 시작 & 종료 시간
    def _SetCodeList(self):
        self.cbCode.addItem('CLF18')
        self.cbCode.addItem('ESZ17')
        self.cbCode.addItem('GCZ17')

    # 시간 설정
    def _SetSearchDate(self):
        try:
            if self.bTimer: # 타이머 종료
                self.timer.stop()
                self.bTimer = False
            self.sCode = self.cbCode.currentText()
            query = 'select time from {}_hoga order by time asc limit 1;'.format(self.sCode)
            self.db.ExecuteQuery(query)
            startTime1 = datetime.datetime.strptime(self.db.GetData()[0][0][:-2], '%Y%m%d%H%M%S')
            query = 'select time from {}_hoga order by time asc limit 1'.format(self.sCode)
            self.db.ExecuteQuery(query)
            startTime2 = datetime.datetime.strptime(self.db.GetData()[0][0][:-2], '%Y%m%d%H%M%S')
            query = 'select time from {}_trade order by time desc limit 1'.format(self.sCode)
            self.db.ExecuteQuery(query)
            finishTime1 = datetime.datetime.strptime(self.db.GetData()[0][0][:-2], '%Y%m%d%H%M%S')
            query = 'select time from {}_hoga order by time desc limit 1'.format(self.sCode)
            self.db.ExecuteQuery(query)
            finishTime2 = datetime.datetime.strptime(self.db.GetData()[0][0][:-2], '%Y%m%d%H%M%S')
            # 가장 빠른 시간 데이터 ~ 가장 마지막 시간 데이터
            if startTime1 < startTime2:
                self.dteStart.setDateTime(startTime1)
                self.dteProcess.setDateTime(startTime1)
                self.startTime = startTime1
                self.processTime = startTime1
            else:
                self.dteStart.setDateTime(startTime2)
                self.dteProcess.setDateTime(startTime2)
                self.startTime = startTime2
                self.processTime = startTime2
            if finishTime1 > finishTime2:
                self.dteFinish.setDateTime(finishTime1)
                self.finishTime = finishTime1
            else:
                self.dteFinish.setDateTime(finishTime2)
                self.finishTime = finishTime2
        except Exception as error:
            self.Log('[Exception]{} in SetupComboBox'.format(error))

    def _SearchData(self):
        try:
            self.processTime = self.dteStart.dateTime().toPyDateTime()
            self.dteProcess.setDateTime(self.processTime)
            self._InitTableWidget()
        except Exception as error:
            self.Log('[Exception]{} in searchData'.format(error))

    def _PlayVerification(self):
        # 타이머 시작
        try:
            if not self.sCode == self.volumeTable.sCode:
                self._SearchData()

            if not self.bTimer:
                self.bTimer = True
                self.timer.start(self.sbTimeUnit.value())
            else:
                self.Log('Already running')
        except Exception as error:
            self.Log('[Exception]{} in PlayVerification'.format(error))

    def _PauseVerification(self):
        # 타이머 동장을 일시 정지
        try:
            if self.bTimer:
                self.timer.stop()
                self.bTimer = False
            else:
                self.Log('Not running')
        except Exception as error:
            self.Log('[Exception]{} in PauseVerification'.format(error))

    def _StopVerification(self):
        # 타이머 동작을 멈추고 processTime을 시작값으로 복귀
        try:
            if self.bTimer:
                self.timer.stop()
                self.bTimer = False
            self.processTime = self.dteStart.dateTime().toPyDateTime()
            self.dteProcess.setDateTime(self.processTime)
        except Exception as error:
            self.Log('[Exception]{} in StopVerification'.format(error))

    def _TimerProcessData(self):
        try:
            if self.bTimer:
                if self.TimeCompare(self.processTime, self.dteFinish.dateTime().toPyDateTime()):
                    self._PauseVerification()
                    self.processTime = self.dteFinish.dateTime().toPyDateTime()
                    self.dteProcess.setDateTime(self.processTime)
                    self.bRealVerification = False
                    if self.bRealTimer:
                        self.bRealVerification = True
                        self.sbTimeUnit.setValue(1000)
                        self._PlayVerification()

                else:
                    self._GetDataFromDB()
                    if self.processTime.hour == 7:
                        self.processTime += datetime.timedelta(hours = 1)
                        self.volumeTable.InitVolumeData()
                        for i in range(self.volumeTable.rowCount):
                            self.twVolume.setItem(i, 0, QTableWidgetItem('{}'.format(self.volumeTable.volumeData[i][1])))
                            self.twVolume.setItem(i, 2, QTableWidgetItem('{}'.format(self.volumeTable.volumeData[i][2])))
                    elif 8 <= self.processTime.hour < 16:
                        if self.bMajor:
                            self.bMajor = False
                            self.timeDelta = 60
                    else:
                        if not self.bMajor:
                            self.bMajor = True
                            self.timeDelta = 1

                    self.processTime += datetime.timedelta(seconds = self.timeDelta)
                    self.dteProcess.setDateTime(self.processTime)
            else:
                self.timer.stop()
        except Exception as error:
            self.Log('[Exception]{} in TimerProcessData'.format(error))


    def _GetDataFromDB(self):
        '''
        processTime 기준 초단위 데이터를 불러온다
        '''
        try:
            self.processTime = self.dteProcess.dateTime().toPyDateTime()
            # DB 데이터 가져오기'%Y%m%d%H%M%S'
            self.hogaDB = []
            self.tradeDB = []
            if self.timeDelta == 60:
                query = 'select * from {}_trade where time like \'{}\' order by time asc'.format(self.sCode, self.processTime.strftime('%Y%m%d%H%M') + '%')
            else:
                query = 'select * from {}_trade where time like \'{}\' order by time asc'.format(self.sCode, self.processTime.strftime('%Y%m%d%H%M%S') + '%')
            self.db.ExecuteQuery(query)
            # self.Log(self.db.GetData())
            if not len(self.db.GetData()) == 0:
                self.tradeDB = self.db.GetData()
            # self.Log(self.tradeDB)
            if self.timeDelta == 60:
                query = 'select * from {}_hoga where time like \'{}\' order by time asc'.format(self.sCode, self.processTime.strftime('%Y%m%d%H%M') + '%')
            else:
                query = 'select * from {}_hoga where time like \'{}\' order by time asc'.format(self.sCode, self.processTime.strftime('%Y%m%d%H%M%S') + '%')
            self.db.ExecuteQuery(query)
            # self.Log(self.db.GetData())
            if not len(self.db.GetData()) == 0:
                self.hogaDB = self.db.GetData()
            self._SeparateData()

        except Exception as error:
            self.Log('[Exception]{} in GetDataFromDB'.format(error))

    def _SeparateData(self):
        try:
            processTime = self.processTime.strftime('%Y%m%d%H%M%S') + '00'
            processTime = int(processTime)
            nCount = len(self.tradeDB) + len(self.hogaDB)
            if nCount == 0: # 단위 시간별 데이터가 없을 경우
                self.timeDeltaCount -= 1
            else:           # 단위 시간별 데이터가 있을 경우
                self.timeDeltaCount = 60
            if self.timeDeltaCount <= 0: # 단위 시간당 반응이 없을 경우 탐색 시간 증가
                if self.processTime.second == 0:
                    self.timeDelta = 60
            else:
                if self.bMajor:
                    self.timeDelta = 1
                else:
                    self.timeDelta = 60
                    if self.bRealVerification:
                        self.timeDelta = 1
            totalData = self.tradeDB + self.hogaDB
            nCount = len(totalData)
            if nCount == 0: # 단위 시간별 데이터가 없을 경우
                self.timeDeltaCount -= 1
            else:           # 단위 시간별 데이터가 있을 경우
                self.timeDeltaCount = 60
            if self.timeDeltaCount <= 0: # 단위 시간당 반응이 없을 경우 탐색 시간 증가
                if self.processTime.second == 0:
                    self.timeDelta = 60
            else:
                if self.bMajor:
                    self.timeDelta = 1
                else:
                    if not self.bRealVerification:
                        self.timeDelta = 60
                    else:
                        self.timeDelta = 1
            if self.tradeDB and self.hogaDB:
                totalData.sort()
            disTrade = None
            disHoga = None
            price = []
            if not totalData == []:
                for data in totalData:
                    if len(data) == 17:
                        disTrade = data
                        self.volumeTable.SetVolumeData(data[3], data[8])
                        if not data[3] in price:
                            price.append(data[3])
                    else:
                        disHoga = data
            if not disTrade == None:
                self._DisplayTradeDB(disTrade)
                self._DisplayVolumeData(price)
            if not disHoga == None:
                self._DisplayHogaDB(disHoga)

        except Exception as error:
            self.Log('[Exception]{} in SeparateData'.format(error))

    def _DisplayTradeDB(self, tradeDB):
        try:
            for nIndex in range(len(tradeDB)):
                row = self.tradeTable.indexToTable[nIndex][0]
                col = self.tradeTable.indexToTable[nIndex][1]
                # self.Log('row : [{}], col : [{}], data = [{}]'.format(row, col, tradeDB[nIndex]))
                if row != None and col != None:
                    self.twTrade.setItem(row, col, QTableWidgetItem(str(tradeDB[nIndex])))
            self.twTrade.setItem(1, 0, QTableWidgetItem(self.TimeFormat(str(tradeDB[0]))))
        except Exception as error:
            self.Log('[Exception]{} in DisplayTradeDB'.format(error))

    def _DisplayHogaDB(self, hogaDB):
        try:
            hogaIndex = 0
            for nIndex in range(len(hogaDB)):
                row = self.hogaTable.indexToTable[nIndex][0]
                col = self.hogaTable.indexToTable[nIndex][1]
                # self.Log('row : [{}], col : [{}], data = [{}]'.format(row, col, hogaDB[nIndex]))
                if not (row == None or col == None):
                    if 51 < nIndex <= 61:
                        hogaIndex += 1
                        hoga = hogaDB[4 * hogaIndex]
                        if hoga < 0:
                            hoga *= -1
                        self.twHoga.setItem(row, col, QTableWidgetItem('{}({})'.format(hoga, hogaDB[nIndex])))
                    else:
                        self.twHoga.setItem(row, col, QTableWidgetItem(str(hogaDB[nIndex])))
                self.twHoga.setItem(11, 3, QTableWidgetItem(self.TimeFormat(str(hogaDB[0]))))
        except Exception as error:
            self.Log('[Exception]{} in DisplayHogaDB'.format(error))

    def _DisplayVolumeData(self, prices): #
        try:
            for price in prices:
                row = self.volumeTable.dicVolumeData[price]
                self.twVolume.setItem(row, 0, QTableWidgetItem(str(self.volumeTable.volumeData[row][1])))
                self.twVolume.setItem(row, 2, QTableWidgetItem(str(self.volumeTable.volumeData[row][2])))
        except Exception as error:
            self.Log('[Exception]{} in DisplayVolumeData'.format(error))

    def TimeFormat(self, sTime):
        return sTime[8:10] + ':' + sTime[10:12] + ':' +sTime[12:14]

    def TimeCompare(self, datetime1, datetime2):
        try:
            if (isinstance(datetime1, datetime.datetime) and isinstance(datetime2, datetime.datetime)):
                result = datetime2 - datetime1
                if result.days < 0:
                    return True
                else:
                    return False
        except Exception as error:
            self.Log('[Exception]{} in TimeCompare'.format(error))


    def _SetRealTime(self):
        try:
            if self.chRealTime.isChecked():
                if not self.bRealTimer:
                    self.realTimer.start(1000) # 1초 단위 이벤트 발생
                    self.bRealTimer = True
                self.dteFinish.setDateTime(datetime.datetime.now())
            else:
                if self.bRealTimer:
                    self.realTimer.stop()
                    self.bRealTimer = False
                self.dteFinish.setDateTime(self.finishTime)
        except Exception as error:
            self.Log('[Exception]{} in SetRealTime'.format(error))

    def Log(self, strData):
        # 각종 데이터 처리 과정을 메론 로그에 남김
        if self.logCounter == 0:
            if platform.platform()[:7] == 'Windows':
                logFile = open(VerificationDir+'\VerificationLog.txt', 'a')
            else:
                logFile = open(VerificationDir+'/VerificationLog.txt', 'a')
            logFile.write('\n\n[{0}] Started Program'.format(time.ctime()))
            logFile.close()
        try:
            if not (isinstance(strData, str)):
                strData = str(strData)
            self.lstLog.addItem('[{0:05d}] {1}'.format(self.logCounter, strData))
            if platform.platform()[:7] == 'Windows':
                logFile = open(VerificationDir+'\VerificationLog.txt', 'a')
            else:
                logFile = open(VerificationDir+'/VerificationLog.txt', 'a')
            logFile.write('\n[{0:05d}] {1}'.format(self.logCounter, strData))
            logFile.close()
            self.logCounter += 1
        except Exception as error:
            self.Log('[Exception]{} in Log'.format(error))

class DataBase(object):
    def __init__(self):
        self.host = 'localhost'
        self.user = 'dbreader'
        self.password = 'dbreader'
        self.db = 'ff_data'
        self.charset = 'utf8'
        self.SetConnectOption()

    def SetConnectOption(self):
        self.settingDB = [self.host, self.user, self.password, self.db, self.charset]
        self.connect = None  # 연결 상태
        self.cursor = None   # 연결시 데이터 추출
        self.query = None    # 쿼리문
        self.dbData = []  # 데이터 수신
        for i in range(10):
            self.dbData.append(None)

    # mysql 접속
    def Connect(self):
        if self.connect == None:
            if platform.platform()[:7] == 'Windows':
                self.connect = pymysql.connect(host = self.host, user = self.user, password = self.password,
                                                db = self.db, charset = self.charset)

            elif platform.platform()[:6] == 'Darwin':
                self.connect = pymysql.connect(host = '192.168.0.9', user = self.user, password = self.password,
                                                db = self.db, charset = self.charset)
            self.cursor = self.connect.cursor()
        else:
            raise 'Database is already Connected'

    def DisConnect(self):
        if self.connect != None:
            self.cursor = None
            self.connect.close()
            self.connect = None
        else:
            raise 'Database is not Connected'

    def SetQuery(self, query):
        self.query = query

    def ExecuteQuery(self, query = None, select = 0):
        try:
            self.Connect()
            if query != None:
                self.cursor.execute(query)
            elif query == None and self.query != None:
                self.cursor.execute(self.query)
            else:
                raise 'Please, writing query'

            if 0 <= select < 10:
                dbData = self.cursor.fetchall()
                self.dbData[select] = []
                for data in dbData:
                    self.dbData[select].append(list(data))
            else:
                raise 'list index out of range'

        except Exception as error:
            raise error

        finally:
            self.DisConnect()

    def GetData(self, nIndex = 0):
        return self.dbData[nIndex]

class HogaTable(object):
    def __init__(self):
        self.indexToTable = (
        # 행(row), 열(column)
        (11, 3),        #  0 호가시간
        (None, None),   #  1 종목명
        (None, None),   #  2 최우선매도호가
        (None, None),   #  3 최우선매수호가
        (1, 3),          #  4 매도호가 5
        (1, 2),          #  5 매도호가잔량 5
        (1, 0),          #  6 매도호가대비 5
        (1, 1),          #  7 매도호가건수 5
        (2, 3),          #  8 매도호가 4
        (2, 2),          #  9 매도호가잔량 4
        (2, 0),          # 10 매도호가대비 4
        (2, 1),          # 11 매도호가건수 4
        (3, 3),          # 12 매도호가 3
        (3, 2),          # 13 매도호가잔량 3
        (3, 0),          # 14 매도호가대비 3
        (3, 1),          # 15 매도호가건수 3
        (4, 3),          # 16 매도호가 2
        (4, 2),          # 17 매도호가잔량 2
        (4, 0),          # 18 매도호가대비 2
        (4, 1),          # 19 매도호가건수 2
        (5, 3),          # 20 매도호가 1
        (5, 2),          # 21 매도호가잔량 1
        (5, 0),          # 22 매도호가대비 1
        (5, 1),          # 23 매도호가건수 1
        (6, 3),          # 24 매수호가 1
        (6, 4),          # 25 매수호가잔량 1
        (6, 6),          # 26 매수호가대비 1
        (6, 5),          # 27 매수호가건수 1
        (7, 3),          # 28 매수호가 2
        (7, 4),          # 29 매수호가잔량 2
        (7, 6),          # 30 매수호가대비 2
        (7, 5),          # 31 매수호가건수 2
        (8, 3),          # 32 매수호가 3
        (8, 4),          # 33 매수호가잔량 3
        (8, 6),          # 34 매수호가대비 3
        (8, 5),          # 35 매수호가건수 3
        (9, 3),          # 36 매수호가 4
        (9, 4),          # 37 매수호가잔량 4
        (9, 6),          # 38 매수호가대비 4
        (9, 5),          # 39 매수호가건수 4
        (10, 3),         # 40 매수호가 5
        (10, 4),         # 41 매수호가잔량 5
        (10, 6),         # 42 매수호가대비 5
        (10, 5),         # 43 매수호가건수 5
        (11, 2),         # 44 매도호가총잔량
        (11, 0),         # 45 매도호가총잔량대비
        (11, 1),         # 46 매도호가총건수
        (11, 4),         # 47 매수호가총잔량
        (11, 6),         # 48 매수호가총잔량대비
        (11, 5),         # 49 매수호가총건수
        (None, None),    # 50 호가순잔량
        (None, None),    # 51 순매수잔량
        (1, 3),          # 52 매도1호가등락율
        (2, 3),          # 53 매도2호가등락율
        (3, 3),          # 54 매도3호가등락율
        (4, 3),          # 55 매도4호가등락율
        (5, 3),          # 56 매도5호가등락율
        (6, 3),          # 57 매수1호가등락율
        (7, 3),          # 58 매수2호가등락율
        (8, 3),          # 59 매수3호가등락율
        (9, 3),          # 60 매수4호가등락율
        (10, 3))         # 61 매수5호가등락율
        self.tableToIndex = (6, 7, 5, 4, 56, 10, 11, 9, 8, 55, 14, 15, 13, 12, 54, 18, 19,
                            17, 16, 53, 22, 23, 21, 20, 52, 24, 57, 25, 27, 26, 28, 58, 29, 31,
                            30, 32, 59, 33, 35, 34, 36, 60, 37, 39, 38, 40, 61, 41, 43, 42,
                            45, 46, 44, 0, 47, 49, 48)

        def GetTableIndex(self, nIndex):
            return self.indexToTable[nIndex][0], self.indexToTable[nIndex][1]

class TradeTable(object):
    def __init__(self):
        self.indexToTable = (
        # 행(row), 열(column)
        (1, 0),        #  0 체결시간
        (None, None),  #  1 코드명
        (1, 1),        #  2 현재가(진법)
        (1, 2),        #  3 현재가
        (1, 3),        #  4 전일대비
        (1, 4),        #  5 등락율
        (1, 5),        #  6 매도호가
        (1, 6),        #  7 매수호가
        (1, 7),        #  8 체결량
        (3, 0),        #  9 누적거래량
        (3, 1),        #  10 시가
        (3, 2),        #  11 고가
        (3, 3),        #  12 저가
        (3, 4),        #  13 전일대비기호
        (3, 5),        #  14 대비
        (3, 6),        #  15 체결일자
        (3, 7))        #  16 영업일
        self.tableToIndex = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

        def GetTableIndex(self, nIndex):
            return self.indexToTable[nIndex][0], self.indexToTable[nIndex][1]

class VolumeTable(object):
    def __init__(self, sCode = None):
        self.db = DataBase()     # 데이터 베이스 접속 설정값
        self.dicTickSize = {'CL':0.01, 'ES':0.25, 'GC':0.1}
        self.dicTickValue = {'CL':10.0, 'ES':12.5, 'GC':10}
        self.dicTickUnit = {'CL':2, 'ES':2, 'GC':1}
        self.sCode = None
        self.tickSize = None
        self.tickValue = None
        self.tickUnit = None
        self.highestPrice = None
        self.lowestPrice = None
        self.rowCount = 30
        self.columnCount = 3
        self.dicVolumeData = {} # twVolume table widget에 입력될 데이터의 인덱스를 반환
        self.VolumeList = [] # twVolume table widget에 입력될 데이터의 인덱스를 반환
        if not sCode == None:
            self.InitTableData(sCode)

    def InitTableData(self, sCode = None): # table Widget에 들어갈 데이터를 입력
        if sCode == None:
            raise 'Invalid code.[Empty]'
        elif not sCode[:2] in self.dicTickSize.keys():
            raise 'Invalid code.[Wrong]'
        else:
            volumeRange = 200
            self.sCode = sCode
            self.tickSize = self.dicTickSize[self.sCode[:2]]
            self.tickValue = self.dicTickValue[self.sCode[:2]]
            self.tickUnit = self.dicTickUnit[self.sCode[:2]]
            query = 'select max(abs(sell_hoga_5)) from {}_hoga'.format(self.sCode)
            self.db.ExecuteQuery(query)
            self.highestPrice = round((self.db.GetData()[0][0] + volumeRange * self.tickSize)/ self.tickSize) * self.tickSize
            query = 'select min(abs(buy_hoga_5)) from {}_hoga'.format(self.sCode)
            self.db.ExecuteQuery(query)
            self.lowestPrice = round((self.db.GetData()[0][0] - volumeRange * self.tickSize) / self.tickSize) * self.tickSize
            self.rowCount = round((self.highestPrice - self.lowestPrice) / self.tickSize)
            self.dicVolumeData = {}
            self.volumeData = []
            for i in range(self.rowCount):
                price = round(self.highestPrice - self.tickSize * i, self.tickUnit)
                self.dicVolumeData.update({price:i})
                self.volumeData.append([price, 0, 0]) # 가격, 매도 거래량, 매수 거래량

    def InitVolumeData(self):
        for i in range(len(self.volumeData)):
            self.volumeData[i][1] = 0
            self.volumeData[i][2] = 0

    def SetVolumeData(self, nPrice, nVolume):
        try:
            if self.sCode == None:
                raise 'Volume Table is not defined'
            else:
                if nVolume < 0:
                    self.volumeData[self.dicVolumeData[nPrice]][1] += nVolume * -1
                else:
                    self.volumeData[self.dicVolumeData[nPrice]][2] += nVolume
        except Exception as error:
            raise '[Exception]{} in SetVolumeData'.format(error)

    def GetVolumeData(self, nPrice):
        try:
            return self.volumeData[self.dicVolumeData[nPrice]]
        except Exception as error:
            raise '[Exception]{} in GetVolumeData'.format(error)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('fusion'))  # 어플리케이션 기본 디자인 설정 "Fusion"
    verificationMain = VerificationMain()
    sys.exit(app.exec_())
