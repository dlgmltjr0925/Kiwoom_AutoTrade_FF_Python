import sys, os.path, configparser, time, pymysql, datetime, threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

rootDir = os.getcwd() # 작업 최상위 디렉토리
VerificationMainForm = uic.loadUiType(rootDir + '\Verification.ui')[0]

class VerificationMain(QMainWindow, VerificationMainForm):
    def __init__(self):
        super().__init__()
        self.startTime = None    # 시작 시간
        self.finishTime = None   # 종료 시간
        self.timeUnit = 0.01     # 타이머 이벤트 처리 간격
        self.logCounter = 0      # 로그 리스트 카운터
        self.db = DataBase()        # 데이터 베이스 접속 설정값
        self.dicItem = {}
        self.sCode = None
        self.hogaDB = []
        self.tradeDB = []
        self._SetupUi()
        self.timer = None
        self.btnSearch.clicked.connect(self._SearchData)
        self.chRealTime.clicked.connect(self._SetRealTime)

    # User Interface 초기화
    def _SetupUi(self):
        # QTableWidget Setting
        self.setupUi(self) # QT Creater로 생성된 기본 프레임
        self.show() # 화면 출력
        self._InitTableWidget()
        self._SetCodeList()
        self._SetBasicOption()

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
                self.twHoga.setColumnWidth(i, 120)
            elif i == 0 or i == 6:
                self.twHoga.setColumnWidth(i, 70)
            else:
                self.twHoga.setColumnWidth(i, 71)
        head = ('대비', '건수', '매도잔량', '가격(등락률)', '매수잔량', '건수', '대비')
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

    # 종목 코드 및 시작 & 종료 시간
    def _SetCodeList(self):
        codeList = ('cl', 'es', 'gc')
        self.Log('====================')
        dicItemDetail = {'시작시간':'', '종료시간':''}
        for i in range(len(codeList)):
            self.Log('{} 종목코드 추출 중'.format(codeList[i]))
            # 종목명만 추출하는 쿼리문
            query = 'select distinct name from tb_ff_{}_real_trade'.format(codeList[i])
            self.db.ExecuteQuery(query)
            for code in self.db.GetData():
                self.dicItem.update({code[0]:dicItemDetail})
                self.Log(code[0])
        for key in self.dicItem.keys():
            self.Log('{} 시작시간 추출 중'.format(key))
            query = 'select distinct time from tb_ff_{}_real_trade where name = "{}" order by time asc limit 1'.format(key[0:2].lower(), key)
            self.db.ExecuteQuery(query)
            self.dicItem[key].update({'시작시간':self.db.GetData()[0][0][0:14]})
            self.Log('{} : 시작시간[{}]'.format(key, self.dicItem[key]['시작시간']))
            self.Log('{} 종료시간 추출 중'.format(key))
            query = 'select distinct time from tb_ff_{}_real_trade where name = "{}" order by time desc limit 1'.format(key[0:2].lower(), key)
            self.db.ExecuteQuery(query)
            self.dicItem[key].update({'종료시간':self.db.GetData()[0][0][0:14]})
            self.Log('{} : 종료시간[{}]'.format(key, self.dicItem[key]['종료시간']))
        self.Log('====================')

    # 코드
    def _SetBasicOption(self):
        try:
            for key in self.dicItem.keys():
                self.cbCode.addItem(key)
            self.dteStart.setDateTime(datetime.datetime.now())
            self.dteFinish.setDateTime(datetime.datetime.now())
            self.dteProcess.setDateTime(datetime.datetime.now())
        except Exception as error:
            self.Log('[Exception]{} in SetupComboBox'.format(error))

    def _SearchData(self):
        try:
            if self.sCode == self.cbCode.currentText():
                return 0
            self.Log(self.dicItem)
            self.sCode = self.cbCode.currentText()
            startTime = self.dicItem[self.sCode]['시작시간']
            self.Log(startTime)
            self.dteStart.setDateTime(datetime.datetime.strptime(startTime, '%Y%m%d%H%M%S'))
            finishTime = self.dicItem[self.sCode]['종료시간']
            self.Log(finishTime)
            self.dteFinish.setDateTime(datetime.datetime.strptime(finishTime, '%Y%m%d%H%M%S'))
        except Exception as error:
            self.Log('[Exception]{} in SearchData'.format(error))

    def _SetHogaTableWidget(self, hogaData = None):
        if hogaData == None:
            data = self.hogaDB
        else:
            data = hogaData
        nIndex = 0
        for row in range(1, 12):
            if row < 6:
                for col in range(4):
                    if not col == 3:
                        self.twHoga.setItem(row, col, QTableWidgetItem(data[self.hogaTableIndex[nIndex]]))
                        nIndex += 1
                    else:
                        strData = '{}({})'.format(data[self.hogaTableIndex[nIndex]], data[self.hogaTableIndex[nIndex+1]])
                        self.twHoga.setItem(row, col, QTableWidgetItem(strData))
                        nIndex += 2

            elif 5 < row < 11:
                for col in range(3, 7):
                    if not col == 3:
                        self.twHoga.setItem(row, col, QTableWidgetItem(data[self.hogaTableIndex[nIndex]]))
                        nIndex += 1
                    else:
                        strData = '{}({})'.format(data[self.hogaTableIndex[nIndex]], data[self.hogaTableIndex[nIndex+1]])
                        self.twHoga.setItem(row, col, QTableWidgetItem(strData))
                        nIndex += 2
            else:
                for col in range(7):
                    self.twHoga.setItem(row, col, QTableWidgetItem(data[self.hogaTableIndex[nIndex+1]]))
                    nIndex += 1

    def _SetTradeTableWidget(self, tradeData = None):
        if tradeData == None:
            data = self.hogaDB
        else:
            data = tradeData
        nIndex = 0
        for row in range(1, 4):
            if row == 2:
                continue
            else:
                for col in range(8):
                    self.twHoga.setItem(row, col, QTableWidgetItem(data[self.tradeTableIndex[nIndex]]))
                    nIndex += 1


    def _SetRealTime(self):
        try:
            if self.chRealTime.isChecked():
                self.dteFinish.setDateTime(datetime.datetime.now())
                self.timer = threading.Timer(1, self._SetRealTime)
                self.timer.start()
            else:
                self.timer.cancel()
        except Exception as error:
            self.Log('[Exception]{} in SetRealTime'.format(error))


    def Log(self, strData):
        # 각종 데이터 처리 과정을 메론 로그에 남김
        if self.logCounter == 0:
            logFile = open('VerificationLog.txt', 'a')
            logFile.write('\n\n[{0}] Started Program'.format(time.ctime()))
            logFile.close()
        try:
            if not (isinstance(strData, str)):
                strData = str(strData)
            self.lstLog.addItem('[{0:05d}] {1}'.format(self.logCounter, strData))
            logFile = open('VerificationLog.txt', 'a')
            logFile.write('\n[{0:05d}] {1}'.format(self.logCounter, strData))
            logFile.close()
            self.logCounter += 1
        except Exception as error:
            self.Log('[Exception]{} in Log'.format(error))

class DataBase(object):
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = '1'
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
            self.connect = pymysql.connect(host = self.host, user = self.user, password = self.password,
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
                self.dbData[select] = self.cursor.fetchall()
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
        (5, 3),          # 52 매도1호가등락율
        (4, 3),          # 53 매도2호가등락율
        (3, 3),          # 54 매도3호가등락율
        (2, 3),          # 55 매도4호가등락율
        (1, 3),          # 56 매도5호가등락율
        (6, 3),          # 57 매수1호가등락율
        (7, 3),          # 58 매수2호가등락율
        (8, 3),          # 59 매수3호가등락율
        (9, 3),          # 60 매수4호가등락율
        (10, 3))          # 61 매수5호가등락율
        self.tableToIndex = (6, 7, 5, 4, 56, 10, 11, 9, 8, 55, 14, 15, 13, 12, 54, 18, 19,
                            17, 16, 53, 22, 23, 21, 20, 52, 24, 57, 25, 27, 26, 28, 58, 29, 31,
                            30, 32, 59, 33, 35, 34, 36, 60, 37, 39, 38, 40, 61, 41, 43, 42,
                            45, 46, 44, 0, 47, 49, 48)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('fusion'))  # 어플리케이션 기본 디자인 설정 "Fusion"
    verificationMain = VerificationMain()
    sys.exit(app.exec_())
