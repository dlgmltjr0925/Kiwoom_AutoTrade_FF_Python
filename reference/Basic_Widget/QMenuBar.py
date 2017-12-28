
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from PyQt5.QtGui import QIcon


class Example(QMainWindow):
    def __init__(self):
        super().__init__()

        exit_action = QAction(QIcon('exit.png'), "&Exit", self)
        # exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')

        exit_action.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        fielmenu = menubar.addMenu('&File')
        fielmenu.addAction(exit_action)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Menubar')
        self.show()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
