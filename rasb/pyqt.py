import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QWidget,QLabel, QVBoxLayout
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

#background #F3F9F0
class TPRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.ind = 0
        self.setWindowTitle('My First Application')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.center()
        self.showFullScreen()
        # self.resize(1024,768)
        # self.setFixedSize(self.width, self.height)
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor("#F3F9F0"))
        self.setPalette(pal)
        #self.rgb_value = "r{0},g{1},b{0}".format(r, g, b)
        label1 = QLabel("화면을 터치하여 주세요.")
        label1.setAlignment(Qt.AlignCenter)

        font1 = label1.font()
        font1.setPointSize(40)
        font1.setBold(True)
        
        label1.setFont(font1)

        layout = QVBoxLayout()
        layout.addWidget(label1)
        self.setLayout(layout)
        
        self.show()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            #esc
            self.close()
    
    def mouseReleaseEvent(self, e):
        if self.ind == 0:
            self.close()
            self.ind += 1
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    w = TPRApp()

    sys.exit(app.exec_())
    