from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random


class MyTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(parent)
        self._mainwin = parent

        self.__make_layout()
        self.__make_table()

    def __make_table(self):
        # self.table.setSelectionBehavior(QTableView.SelectRows)  # multiple row 선택 가능
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        # row, column 갯수 설정해야만 tablewidget 사용할수있다.
        self.table.setColumnCount(5)
        self.table.setRowCount(3)

        # column header 명 설정.
        self.table.setHorizontalHeaderLabels(["코드", "종목명"])
        self.table.horizontalHeaderItem(0).setToolTip("코드...")  # header tooltip
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignRight)  # header 정렬 방식

        header_item = QTableWidgetItem("추가")
        header_item.setBackground(Qt.red)  # 헤더 배경색 설정 --> app.setStyle() 설정해야만 작동한다.
        self.table.setHorizontalHeaderItem(2, header_item)



        # cell 에 data 입력하기
        self.table.setItem(0, 0, QTableWidgetItem("000020"))
        self.table.setItem(0, 1, QTableWidgetItem("삼성전자"))
        self.table.setItem(1, 0, QTableWidgetItem("000030"))
        self.table.setItem(1, 1, QTableWidgetItem("현대차"))
        self.table.setItem(2, 0, QTableWidgetItem("000080"))
        item = QTableWidgetItem("기아차")
        self.table.setItem(2, 1, item)
        # self.table.resizeColumnsToContents()
        # self.table.resizeRowsToContents()

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # edit 금지 모드

        # self.table.setCurrentCell(1, 1)  # current cell 위치 지정하기

        self.table.setColumnWidth(2, 50)
        ckbox = QCheckBox()
        self.table.setCellWidget(0, 2, ckbox)
        ckbox2 = QCheckBox('me')
        self.table.setCellWidget(1, 2, ckbox2)

        mycom = QComboBox()
        mycom.addItems(["aa", "dd", "kk"])
        mycom.addItem("cc")
        mycom.addItem("bb")
        self.table.setCellWidget(2, 2, mycom)

        item_widget = QPushButton("test")
        self.table.setCellWidget(1, 3, item_widget)

        self.table.cellClicked.connect(self.__mycell_clicked)
        mycom.currentTextChanged.connect(self.__mycom_text_changed)

    @pyqtSlot(int, int)
    def __mycell_clicked(self, row, col):
        cell = self.table.item(row, col)
        # print(cell)

        if cell is not None:
            txt = "clicked cell = ({0},{1}) ==>{2}<==".format(row, col, cell.text())
        else:
            txt = "clicked cell = ({0},{1}) ==>None type<==".format(row, col)

        # msg = QMessageBox.information(self, 'clicked cell...', txt)
        # print(txt)
        self._mainwin.statusbar.showMessage(txt)
        return

    @pyqtSlot(str)
    def __mycom_text_changed(self, txt):
        msg = QMessageBox.information(self, 'combobox changed...', txt)
        return

    def __make_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)

        grid = QGridLayout()
        vbox.addLayout(grid)
        # grid.setSpacing(20)

        btn1 = QPushButton("전체내용 삭제")
        grid.addWidget(btn1, 0, 0)
        btn2 = QPushButton("table삭제")
        grid.addWidget(btn2, 0, 1)
        btn3 = QPushButton("selection mode")
        grid.addWidget(btn3, 0, 2)
        btn4 = QPushButton("column 추가")
        grid.addWidget(btn4, 0, 3)

        btn5 = QPushButton("column 삽입")
        grid.addWidget(btn5, 1, 0)
        btn6 = QPushButton("column 삭제")
        grid.addWidget(btn6, 1, 1)
        btn7 = QPushButton("row 추가")
        grid.addWidget(btn7, 1, 2)
        btn8 = QPushButton("row 삽입")
        grid.addWidget(btn8, 1, 3)

        btn9 = QPushButton("row 삭제")
        grid.addWidget(btn9, 2, 0)
        btn10 = QPushButton("row 단위선택")
        grid.addWidget(btn10, 2, 1)
        btn11 = QPushButton("grid line 숨기기")
        grid.addWidget(btn11, 2, 2)
        btn12 = QPushButton("alternate color")
        grid.addWidget(btn12, 2, 3)

        btn13 = QPushButton("randorm row 선택")
        grid.addWidget(btn13, 3, 0)
        btn14 = QPushButton("edit")
        grid.addWidget(btn14, 3, 1)
        btn15 = QPushButton("hide row헤더")
        grid.addWidget(btn15, 3, 2)
        btn16 = QPushButton("hide column헤더")
        grid.addWidget(btn16, 3, 3)

        btn17 = QPushButton("selected cells")
        grid.addWidget(btn17, 4, 0)
        btn18 = QPushButton("selected ranges")
        grid.addWidget(btn18, 4, 1)
        btn19 = QPushButton("current cell 내용")
        grid.addWidget(btn19, 4, 2)
        btn20 = QPushButton("(0,0) cell 내용")
        grid.addWidget(btn20, 4, 3)

        btn21 = QPushButton("span")
        grid.addWidget(btn21, 5, 0)
        btn22 = QPushButton("바탕화면 바꾸기")
        grid.addWidget(btn22, 5, 1)
        btn23 = QPushButton("cell 배경 바꾸기")
        grid.addWidget(btn23, 5, 2)
        btn24 = QPushButton("선택시 색 변경 ")
        grid.addWidget(btn24, 5, 3)

        btn25 = QPushButton("헤더배경색 변경")
        grid.addWidget(btn25, 6, 0)
        btn26 = QPushButton("(1,2) checkbox 값")
        grid.addWidget(btn26, 6, 1)
        btn27 = QPushButton("정렬 설정하기")
        grid.addWidget(btn27, 6, 2)
        btn28 = QPushButton("column, row 숨기기")
        grid.addWidget(btn28, 6, 3)

        self.setLayout(vbox)

        self.setGeometry(200, 200, 400, 500)
        self.setWindowTitle("tablewidget example")

        btn1.clicked.connect(self.__btn1_clicked)
        btn2.clicked.connect(self.__btn2_clicked)
        btn3.clicked.connect(self.__btn3_clicked)
        btn4.clicked.connect(self.__btn4_clicked)
        btn5.clicked.connect(self.__btn5_clicked)
        btn6.clicked.connect(self.__btn6_clicked)
        btn7.clicked.connect(self.__btn7_clicked)
        btn8.clicked.connect(self.__btn8_clicked)
        btn9.clicked.connect(self.__btn9_clicked)
        btn10.clicked.connect(self.__btn10_clicked)
        btn11.clicked.connect(self.__btn11_clicked)
        btn12.clicked.connect(self.__btn12_clicked)
        btn13.clicked.connect(self.__btn13_clicked)
        btn14.clicked.connect(self.__btn14_clicked)
        btn15.clicked.connect(self.__btn15_clicked)
        btn16.clicked.connect(self.__btn16_clicked)
        btn17.clicked.connect(self.__btn17_clicked)
        btn18.clicked.connect(self.__btn18_clicked)
        btn19.clicked.connect(self.__btn19_clicked)
        btn20.clicked.connect(self.__btn20_clicked)
        btn21.clicked.connect(self.__btn21_clicked)
        btn22.clicked.connect(self.__btn22_clicked)
        btn23.clicked.connect(self.__btn23_clicked)
        btn24.clicked.connect(self.__btn24_clicked)
        btn25.clicked.connect(self.__btn25_clicked)
        btn26.clicked.connect(self.__btn26_clicked)
        btn27.clicked.connect(self.__btn27_clicked)
        btn28.clicked.connect(self.__btn28_clicked)

    @pyqtSlot()
    def __btn1_clicked(self):
        self.table.clearContents()  # 헤더는 제거 안함.

    @pyqtSlot()
    def __btn2_clicked(self):
        self.table.clear()   # 헤더도 제거함.

    @pyqtSlot()
    def __btn3_clicked(self):
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)  # drag, Ctrl, Shift 키로 다중 선택 가능.
        # self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        # self.table.setSelectionMode(QAbstractItemView.NoSelection)   # 선택 불능.
        # self.table.setSelectionMode(QAbstractItemView.SingleSelection)  # 다중 선택 불가능.
        # self.table.setSelectionMode(QAbstractItemView.ContiguousSelection)

    @pyqtSlot()
    def __btn4_clicked(self):
        # self.table.setColumnCount(3)  # column 추가.
        col_count = self.table.columnCount()
        # print("col_count = {0}".format(col_count))
        self.table.setColumnCount(col_count+1)

    @pyqtSlot()
    def __btn5_clicked(self):
        self.table.insertColumn(1)  # 1 번재 자리에 column 삽입

    @pyqtSlot()
    def __btn6_clicked(self):
        self.table.removeColumn(2)  # column 삭제

    @pyqtSlot()
    def __btn7_clicked(self):
        row_count = self.table.rowCount()
        self.table.setRowCount(row_count+1)   # row 추가

    @pyqtSlot()
    def __btn8_clicked(self):
        self.table.insertRow(0)   # 0번재 자리에 row 삽입

    @pyqtSlot()
    def __btn9_clicked(self):
        self.table.removeRow(1)   # 1번째 row 삭제

    @pyqtSlot()
    def __btn10_clicked(self):
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  # row 단위로 선택 가능
        # self.table.setSelectionBehavior(QAbstractItemView.SelectColumns)  # column 단위로 선택
        # self.table.setSelectionBehavior(QAbstractItemView.SelectItems)  # cell 단위로 선택 가능
        return

    @pyqtSlot()
    def __btn11_clicked(self):
        sender_obj = self.sender()
        if sender_obj.text() == "grid line 숨기기":
            self.table.setShowGrid(False)  # grid line 숨기기
            sender_obj.setText("grid line 보이기")
        else:
            self.table.setShowGrid(True)  # grid line 숨기기
            sender_obj.setText("grid line 숨기기")
        return

    @pyqtSlot()
    def __btn12_clicked(self):
        sender_obj = self.sender()
        if sender_obj.text() == "alternate color":
            self.table.setAlternatingRowColors(True)
            sender_obj.setText("no alternate")
        else:
            self.table.setAlternatingRowColors(False)
            sender_obj.setText("alternate color")
        return

    @pyqtSlot()
    def __btn13_clicked(self):
        row_cnt = self.table.rowCount()
        row_idx = random.randint(0, row_cnt-1)

        # current SelectionMode 와 SelectionBehavior 모두 row 선택가능하게 되어야만 작동한다.
        self.table.selectRow(row_idx)  # 해당 index 의 row 선택하기
        return

    @pyqtSlot()
    def __btn14_clicked(self):
        sender_obj = self.sender()
        if sender_obj.text() == "edit":
            self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
            sender_obj.setText("no edit")
        else:
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # edit 금지 모드
            sender_obj.setText("edit")
        return

    @pyqtSlot()
    def __btn15_clicked(self):
        sender_obj = self.sender()
        if sender_obj.text() == "hide row헤더":
            self.table.verticalHeader().setVisible(False)  # row header 숨기기
            sender_obj.setText("show row헤더")
        else:
            self.table.verticalHeader().setVisible(True)  # row header 보이기
            sender_obj.setText("hide row헤더")
        return

    @pyqtSlot()
    def __btn16_clicked(self):
        sender_obj = self.sender()
        if sender_obj.text() == "hide column헤더":
            self.table.horizontalHeader().setVisible(False)  # column header 숨기기
            sender_obj.setText("show column헤더")
        else:
            self.table.horizontalHeader().setVisible(True)  # column header 보이기
            sender_obj.setText("hide column헤더")
        return

    @pyqtSlot()
    def __btn17_clicked(self):
        aa = self.table.selectedIndexes()
        cell = set( (idx.row(), idx.column()) for idx in aa )
        # print(cell)
        txt1 = "selected cells ; {0}".format(cell)
        msg = QMessageBox.information(self, 'selectedIndexes()...',  txt1)
        return

    @pyqtSlot()
    def __btn18_clicked(self):
        aa = self.table.selectedRanges()
        txt = []
        for idx, sel in enumerate(aa):
            # print(sel.rowCount(), sel.columnCount(), sel.topRow(), sel.leftColumn(), sel.bottomRow(), sel.rightColumn())
            tmp = "ranage {0} ; row/col Count={1}/{2} ".format(idx,sel.rowCount(), sel.columnCount() ) + \
                  "({0},{1}) ~ ({2},{3})".format(sel.topRow(), sel.leftColumn(), sel.bottomRow(), sel.rightColumn())
            txt.append(tmp)
        msg = QMessageBox.information(self, 'selectedRanges()...', '\n'.join(txt))
        return

    @pyqtSlot()
    def __btn19_clicked(self):
        aa = self.table.currentItem()
        # print(aa)

        if aa is not None:
            txt = "row={0}, column={1}, content={2}".format(aa.row(), aa.column(), aa.text())
        else:
            txt = "clicked cell = ({0},{1}) ==>None type<==".format(self.table.currentRow(), self.table.currentColumn())

        msg = QMessageBox.information(self, 'cell 내용', txt)
        return

    @pyqtSlot()
    def __btn20_clicked(self):
        item = self.table.item(0, 0)   # (0,0) cell 의 item 가져오기.
        if item is not None:
            txt = item.text()
        else:
            txt = "no data"
        msg = QMessageBox.information(self, "(0,0) 내용", txt)
        return

    @pyqtSlot()
    def __btn21_clicked(self):
        col_count = self.table.columnCount()
        self.table.setColumnCount(col_count+1)
        self.table.setSpan(1, col_count, 2, 1)  # 2 x 1 크기의 span 생성

        self.table.setCellWidget(1, col_count, QPushButton("span"))
        # self.table.resize(500,600)
        return

    @pyqtSlot()
    def __btn22_clicked(self):
        """
        버튼 누를때 마다 임의의 배경화면...

        ** QPalette.Base  ==> text 사용 widget 의 background 로 사용하겠다는 의미.
        :return:
        """
        palette = QPalette()

        x = random.randint(1, 4)   # 1 <=  x <= 4  사이의 임의의 수
        if x == 1:
            palette.setBrush(QPalette.Base, QBrush(QPixmap("img77.jpg")))
        elif x == 2:
            palette.setColor(QPalette.Base, Qt.yellow)
        elif x == 3:
            palette.setColor(QPalette.Base, QColor(255, 255, 255))   # white
        else:
            palette.setColor(QPalette.Base, QColor(0, 255, 0))

        self.table.setPalette(palette)  # table 배경 설정
        return

    @pyqtSlot()
    def __btn23_clicked(self):
        x = random.randint(1, 3)  # 1 <=  x <= 3  사이의 임의의 수
        myitem = self.table.item(0, 0)
        if x == 1:
            myitem.setBackground(QBrush(QPixmap("exit.png")))  # cell 배경
            myitem.setForeground(QBrush(Qt.red))  # 글자색
            myitem.setFont(QFont("Times", 17, QFont.Bold, italic=True))  # 글자 폰트 설정.
        elif x == 2:
            myitem.setBackground(QBrush(Qt.red))
            myitem.setForeground(QBrush(Qt.yellow))
            myitem.setFont(QFont("Helvetica", 8, QFont.Normal, italic=False))
        else:
            myitem.setBackground(QBrush(QColor(0, 255, 0)))
            myitem.setForeground(QBrush(Qt.blue))
            myitem.setFont(QFont('SansSerif', 25))
        return

    @pyqtSlot()
    def __btn24_clicked(self):
        """
        ** QPalette.Highlight  ==> item 선택시 배경화면 설정.
                                    default ; Qt.darkBlue

        ** QPalette.HighlightedText  ==> item 선택시 글자색 설정.
                                          default ; Qt.white
        :return:
        """
        palette = QPalette()
        palette.setColor(QPalette.Highlight, Qt.yellow)  # default ==> Qt.darkBlue
        palette.setColor(QPalette.HighlightedText, Qt.red)  # default ==> Qt.white
        self.table.setPalette(palette)
        return

    @pyqtSlot()
    def __btn25_clicked(self):
        """
        ** 헤더 배경색 설정 --> app.setStyle() 설정해야만 작동한다.

        ** 헤더명 설정안하고, Qt 가 자동으로 만든 헤더(숫자)는 인식못한다...
        :return:
        """
        hitem = self.table.horizontalHeaderItem(1)
        if hitem is not None:
            hitem.setBackground(QBrush(Qt.cyan))
        # print(hitem)
        # print(hitem.text())
        return

    @pyqtSlot()
    def __btn26_clicked(self):
        ckbox = self.table.cellWidget(1, 2)
        # print(ckbox)
        if isinstance(ckbox, QCheckBox):
            if ckbox.isChecked():
                print("checked")
                _ = QMessageBox.information(self, 'checkbox', "checked")
            else:
                _ = QMessageBox.information(self, 'checkbox', "no checked")
        else:
            _ = QMessageBox.information(self, 'checkbox', "checkbox 아닙니다.")
        return

    @pyqtSlot()
    def __btn27_clicked(self):
        """
        헤더 click 시에 정렬 가능하게 함.
        :return:
        """
        sender_obj = self.sender()
        if sender_obj.text() == "정렬 설정하기":
            self.table.setSortingEnabled(True)  # default ; False
            sender_obj.setText("정렬 안함")
        else:
            self.table.setSortingEnabled(False)
            sender_obj.setText("정렬 설정하기")
        return

    @pyqtSlot()
    def __btn28_clicked(self):
        """
        column, row 숨기기
        :return:
        """
        sender_obj = self.sender()
        if sender_obj.text() == "column, row 숨기기":
            self.table.setColumnHidden(2, True)
            self.table.setRowHidden(0, True)
            sender_obj.setText("column, row 보이기")
        else:
            self.table.setColumnHidden(2, False)
            self.table.setRowHidden(0, False)
            sender_obj.setText("column, row 숨기기")
        return


class MyMain(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        table = MyTable(self)
        # table.setStyle(QStyleFactory.create('Fusion'))
        self.setCentralWidget(table)

        self.statusbar = self.statusBar()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))  # --> 없으면, 헤더색 변경 안됨.

    # w = MyTable()
    w = MyMain()
    w.show()
    sys.exit(app.exec())
