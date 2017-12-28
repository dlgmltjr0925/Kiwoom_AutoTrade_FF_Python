from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *

import sys


if __name__ == '__main__':

    app = QApplication(sys.argv)

    listWidget = QListWidget()
    listWidget.show()

    ls = ['test', 'test2', 'test3']

    listWidget.addItem('test')
    listWidget.addItem('test2')

    listWidget.addItems(ls)

    sys.exit(app.exec_())
