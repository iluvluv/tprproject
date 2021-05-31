import sys
import cv2
import pyzbar.pyzbar as pyzbar
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QDialog, QGridLayout, QHBoxLayout, QPushButton, QStackedWidget, QWidget,QLabel, QVBoxLayout
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

class ShowVideo(QtCore.QObject):
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("can't video")
        sys.exit(0)

    ret, image = camera.read()

    height, width = image.shape[:2]

    VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, widget,parent=None):
        self.widget = widget
        super(ShowVideo, self).__init__(parent)

    @QtCore.pyqtSlot()
    def startVideo(self):
        global image
        run_video = True
        print("video start")
        while run_video and self.widget.currentIndex()== 1:
            ret, image = self.camera.read()
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray_qr = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # QR decode
            decoded = pyzbar.decode(gray_qr)

            if len(decoded) == 0:
                print('qr not found')
            elif len(decoded) == 1:
                for d in decoded:
                    x, y, w, h = d.rect
                    barcode_data = d.data.decode("utf-8")
                    barcode_type = d.type
                    print("="*30)
                    print("\n\n\n\n\n")
                    print('qr find!!')
                    print("\n\n\n\n\n")
                    print("="*30)
                    userid, userpoint = barcode_data.split(" ")

                    print(userid, " _ ", userpoint)
                    # Camera module Thread Run
                run_video = False
                self.widget.setCurrentIndex(self.widget.currentIndex()+2)
                self.widget.s.thread.quit()
                break
            print('webcam module thread')
            k = cv2.waitKey(0) & 0xff
            if k == 27:
                break
            qt_image1 = QtGui.QImage(color_swapped_image.data,
                                    self.width,
                                    self.height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
            self.VideoSignal1.emit(qt_image1)

            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(25, loop.quit) #25 ms
            # singleshot은 다른 스레드?로 돌아감
            loop.exec_()
    def buffer_clear(self):
        buffer_size = cv2.CAP_PROP_BUFFERSIZE
        print("buffer size", buffer_size)
        while buffer_size > 0:
            buffer_size -= 1
            self.camera.read()

class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

    def initUI(self):
        self.setWindowTitle('Test')

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            print("image size",image.size())
            self.setFixedSize(image.size())
        self.update()

#background #F3F9F0
class TPRFirstWindow(QWidget):
    def __init__(self, wid):
        super().__init__()
        self.setWidget(wid)
        self.initUI()
    
    def setWidget(self, wid):
        self.widget = wid

    def initUI(self):
        self.ind = 0
        # self.setWindowTitle('My First Application')
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # self.center()
        # self.showFullScreen()
        # self.resize(1024,768)
        # self.setFixedSize(self.width, self.height)
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor("#F3F9F0"))
        self.widget.setPalette(pal)
        
        label1 = QLabel("화면을 터치하여 주세요.")
        label1.setAlignment(Qt.AlignCenter)

        font1 = label1.font()
        font1.setPointSize(40)
        font1.setBold(True)
        
        label1.setFont(font1)

        layout = QVBoxLayout()
        layout.addWidget(label1)
        self.setLayout(layout)
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    
    def start_second(self):
        self.widget.s.thread = QtCore.QThread()
        self.widget.s.thread.start()
        self.widget.s.vid.moveToThread(self.widget.s.thread)
        self.widget.s.vid.VideoSignal1.connect(self.widget.s.image_viewer.setImage)
        self.widget.s.vid.startVideo()

    def mouseReleaseEvent(self, e):
        print("click!!")
        if self.widget.currentIndex() == 0:
            self.widget.setCurrentIndex(self.widget.currentIndex()+1)
            self.widget.update()
            QtCore.QTimer.singleShot(10, self.start_second) #25 ms
            # singleshot은 다른 스레드?로 돌아감
            print("0->1swap!!")


class TPRSecondWindow(QWidget):
    def __init__(self, widget,parent=None):
        self.widget = widget
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.image_viewer = ImageViewer()
        self.vid = self.widget.vid

        grid_layout = QtWidgets.QGridLayout()
        
        grid_layout.addWidget(self.image_viewer,0,0,2,-1,Qt.AlignCenter)

        btn = QPushButton("선택")
        btn.clicked.connect(self.btn_click)
        print(btn.sizeHint())

        #dummy_label
        for i in range(3):
            lab = QLabel("")
            lab.setAlignment(Qt.AlignCenter)
            grid_layout.addWidget(lab, 2, i)

        label1 = QLabel("포인트를 적립하지 않겠습니다.")
        label1.setAlignment(Qt.AlignCenter)

        font1 = label1.font()
        font1.setPointSize(20)
        font1.setBold(True)
        
        label1.setFont(font1)
        btn.resize(50,50)
        
        grid_layout.addWidget(label1, 2, 3)
        grid_layout.addWidget(btn, 2, 4)

        self.thread = QtCore.QThread()
        self.setLayout(grid_layout)

    def btn_click(self):
        print("btn_click")
        if self.widget.currentIndex() == 1:
            self.widget.setCurrentIndex(self.widget.currentIndex()+1)
            QtCore.QTimer.singleShot(5000, self.widget.s.moveFirstWindow)
            print("1->2 swap!!")

# 800 400
# https://pixabay.com/ko/vectors/%EC%9E%AC%ED%99%9C%EC%9A%A9-%EA%B8%B0%ED%98%B8-%EB%A1%9C%EA%B3%A0-%EB%85%B9%EC%83%89-304974/

class TPRThirdWindow(QWidget):
    def __init__(self, widget):
        self.widget = widget
        super().__init__()
        self.initUI()
    
    def initUI(self):
        print("TPR Third Window initUI")
        grid_layout = QGridLayout()
        recycle = QPixmap()
        recycle.load("C:/Users/nav96/Desktop/recycling-304974_1280.png")
        recycle = recycle.scaledToHeight(120)

        label1 = QLabel()
        label1.setPixmap(recycle)

        label1.setAlignment(Qt.AlignRight|Qt.AlignCenter)

        label2 = QLabel("감사합니다.")
        label2.setAlignment(Qt.AlignCenter)
        font1 = label2.font()
        font1.setPointSize(40)
        font1.setBold(True)
        
        label2.setFont(font1)
        grid_layout.addWidget(label1,1,1)
        grid_layout.addWidget(label2,1,2)
        for i in range(5):
            grid_layout.addWidget(QLabel(),0,i)
            grid_layout.addWidget(QLabel(),2,i)
        self.setLayout(grid_layout)
         #25 ms
    
    def moveFirstWindow(self):
        if self.widget.currentIndex() == 2:
            self.widget.setCurrentIndex(0)
    
    # def mouseReleaseEvent(self, e):
    #     print("click!!")
    #     if self.widget.currentIndex() == 2:
    #         self.widget.setCurrentIndex(self.widget.currentIndex()+1)
        
class TPRForthWindow(QWidget):
    def __init__(self, widget):
        self.widget = widget
        super().__init__()
        self.initUI()
    
    def initUI(self):
        print("TPR Forth Window init")

        grid_layout = QGridLayout()
        recycle = QPixmap()
        recycle.load("C:/Users/nav96/Desktop/recycling-304974_1280.png")
        recycle = recycle.scaledToHeight(120)

        label1 = QLabel()
        label1.setPixmap(recycle)

        label1.setAlignment(Qt.AlignCenter)

        label2 = QLabel("작업 완료 시 까지 기다리시겠습니까?")
        label2.setAlignment(Qt.AlignCenter)
        font1 = label2.font()
        font1.setPointSize(40)
        font1.setBold(True)
        
        btn_yes = QPushButton("예")
        btn_no = QPushButton("아니오")

        btn_yes.setFont(QFont('Arial',30))
        btn_no.setFont(QFont('Arial',30))

        btn_yes.clicked.connect(self.yes_func)
        btn_no.clicked.connect(self.no_func)

        btn_yes.setStyleSheet("""
                            QPushButton{
                                background-color: #70AD47;
                                border : 1px solid black;
                                color: white;
                            }
                            QPushButton:hover{
                                color: blue;
                            }
                            """)
        
        btn_no.setStyleSheet("""
                            QPushButton{
                                background-color: #70AD47;
                                border : 1px solid black;
                                color: white;
                            }
                            QPushButton:hover{
                                color: blue;
                            }
                            """)

        btn_yes.setMaximumHeight(120)
        btn_yes.setMaximumWidth(360)
        btn_no.setMaximumHeight(120)
        btn_no.setMaximumWidth(360)

        label2.setFont(font1)
        grid_layout.addWidget(label1,1,1)
        grid_layout.addWidget(label2,1,2,1,2)
        
        # grid_layout.addWidget(btn_yes,3,1,1,2)
        # grid_layout.addWidget(btn_no,3,3,1,-1)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_yes)
        hbox.addWidget(btn_no)
        grid_layout.addLayout(hbox,3,0,1,5)

        for i in range(5):
            grid_layout.addWidget(QLabel(),0,i)
            grid_layout.addWidget(QLabel(),4,i)
            # grid_layout.addWidget(QLabel(),2,i)
        self.setLayout(grid_layout)

        QtCore.QTimer.singleShot(30000, self.moveFirstWindow) #25 ms
    
    def moveFirstWindow(self):
        if self.widget.currentIndex() == 3:
            self.widget.setCurrentIndex(0)

    def yes_func(self):
        print("yes_function")
        self.widget.setCurrentIndex(self.widget.currentIndex()+1)
        QtCore.QTimer.singleShot(5000, self.widget.ff.moveFirstWindow)

    def no_func(self):
        print("no_function")
        QtCore.QTimer.singleShot(5000, self.widget.t.moveFirstWindow)
        self.widget.setCurrentIndex(2)



class TPRFifthWindow(QWidget):
    def __init__(self, widget):
        self.widget = widget
        super().__init__()
        self.initUI()

    def initUI(self):
        print("TPR Fifth Window init")
        grid_layout = QGridLayout()
        recycle = QPixmap()
        recycle.load("C:/Users/nav96/Desktop/recycling-304974_1280.png")
        recycle = recycle.scaledToHeight(100)
        
        bottle = QPixmap()
        bottle.load("C:/Users/nav96/Desktop/water.png")
        bottle = bottle.scaledToHeight(100)

        point = QPixmap()
        point.load("C:/Users/nav96/Desktop/dollar.png")
        point = point.scaledToHeight(100)

        label1 = QLabel()
        label1.setPixmap(recycle)

        label1.setAlignment(Qt.AlignCenter)

        label2 = QLabel("분리가 완료 되었습니다.")
        label2.setAlignment(Qt.AlignCenter)

        font1 = label2.font()
        font1.setPointSize(30)
        font1.setBold(True)
        
        bottleimg = QLabel("")
        bottleimg.setPixmap(bottle)
        bottleimg.setAlignment(Qt.AlignCenter|Qt.AlignRight)
        
        pointimg = QLabel("")
        pointimg.setPixmap(point)
        pointimg.setAlignment(Qt.AlignRight|Qt.AlignCenter) 

        bottleLabel = QLabel("투명 페트병의 개수")
        font1 = bottleLabel.font()
        font1.setPointSize(30)
        font1.setBold(True)
        bottleLabel.setFont(font1)

        pointLabel = QLabel("적립 예정 포인트")
        font1 = pointLabel.font()
        font1.setPointSize(30)
        font1.setBold(True)
        pointLabel.setFont(font1)

        bottleLabel.setAlignment(Qt.AlignCenter)
        pointLabel.setAlignment(Qt.AlignCenter)

        grid_layout.addWidget(bottleimg,2,0)
        grid_layout.addWidget(bottleLabel,2,1,1,2)
        grid_layout.addWidget(pointimg,2,0,2,1)
        grid_layout.addWidget(pointLabel,2,1,2,2)


        self.bottlePer = QPushButton("0 개",self)
        self.pointPer = QPushButton("0 P",self)

        self.bottlePer.setFont(QFont('Arial',30))
        self.pointPer.setFont(QFont('Arial',30))

        self.bottlePer.setStyleSheet("""
                            QPushButton{
                                background-color: #70AD47;
                                border : 1px solid black;
                                color: white;
                            }
                            """)
        
        self.pointPer.setStyleSheet("""
                            QPushButton{
                                background-color: #70AD47;
                                border : 1px solid black;
                                color: white;
                            }
                            """)

        self.bottlePer.setMaximumHeight(120)
        self.bottlePer.setMaximumWidth(360)
        self.pointPer.setMaximumHeight(120)
        self.pointPer.setMaximumWidth(360)

        label2.setFont(font1)
        grid_layout.addWidget(label1,1,1,2,1)
        grid_layout.addWidget(label2,1,1,2,3)

        
        grid_layout.addWidget(self.bottlePer,2,3,1,2)
        grid_layout.addWidget(self.pointPer,2,3,2,2)
        self.i = 1
        self.setLayout(grid_layout)
        

    def setBottle(self, s):
        self.bottlePer.setText(s+" 개")
    def setPoint(self, s):
        self.pointPer.setText(s+" P")

    def moveFirstWindow(self):
        self.widget.setCurrentIndex(0)

    

class TPRWindowManager(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.vid = ShowVideo(self)
        self.init_widget()

    def init_widget(self):
        self.widget = self
        self.w = TPRFirstWindow(self)
        self.s = TPRSecondWindow(self)
        self.t = TPRThirdWindow(self)
        self.f = TPRForthWindow(self)
        self.ff = TPRFifthWindow(self)

        self.widget.addWidget(self.w)
        self.widget.addWidget(self.s)
        self.widget.addWidget(self.t)
        self.widget.addWidget(self.f)
        self.widget.addWidget(self.ff)

        self.widget.setWindowTitle("TPR Service")
        self.widget.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.widget.showFullScreen()
        print("widget current", self.widget.currentIndex())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            #esc
            self.widget.close()
            sys.exit()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    wid = TPRWindowManager()
    sys.exit(app.exec_())
    