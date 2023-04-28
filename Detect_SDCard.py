import sys
from os import path as p
from os import makedirs as md
from os import rename as r
from os import remove as rm
from glob import glob as ls
from shutil import move as mv
import configparser
cfg = configparser.ConfigParser(interpolation=None)
cfg.read('Detect_SDCard.ini')
import threading
from datetime import date, datetime as dt, timedelta as td
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QAction,
    QDateEdit,
    QMessageBox,
    QTextEdit,
    QMenuBar
)
from PyQt5.QtCore import (
    QSize
)
from PyQt5.QtGui import (
    QIcon
)

from _Detect_SDCard_version import __version__

def get_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return p.join(sys._MEIPASS, filename)
    else:
        return filename


aboutText = '<img src="' + get_path('./images/25_trans_60x60.png') + '"<br><br>' \
            '<span style="color:Blue;"><b>GoPro SD card transfer</b></span><hr>' \
            + p.basename(__file__) + '<br>Version: <i>' + __version__ \
            + '</i><hr>Import hd and proxy video from GoPro SD card.'

helpText = '<img src="' + get_path('./images/25_trans_60x60.png') + '"<br><br>' \
           '<span style="color:Blue;"><b>GoPro SD card transfer</b></span><hr>' \
           '<br><span style="color:Blue;">Src. folder:</span> Specifies the full path to the files on they SD card (e.g. /media/sdcard/382-3234/DCIM/*/*) \
           note the 2 uses of wildcard to allow collection of files from multipe directories.<br> \
           <span style="color:Blue;">Dest. folder:</span> Full path to destination folder, default is date based but can be changed. \
            A proxy folder is automatically created within the destination. <br> \
            <span style="color:Blue;">List Src.:</span> List HD and Proxy files on the SD Card. <br> \
            <span style="color:Blue;">Make Dir:</span> Makes the directories based on the root specified by "Dest. folder". <br> \
            <span style="color:Blue;">Move Files:</span> Moves the "MP4" and "LRV" files from the SD Card to the destination folder \
            renaming proxy files with "mov" extension. <br> \
         <span style="color:Blue;">List Dest.:</span> Lists the contents of the "Dest folder", both "MP4" and "mov" files are listed. <br> \
             <a href="mailto:mike.norris@nodmore.info?subject=Thank you for the GoPro SDCard transfer script.&body= \
             Many thanks. ">created by Mike Norris</a>'

base_src_folder = cfg['DEFAULT']['base_src_folder']
base_dest_folder = cfg['DEFAULT']['base_dest_folder']
hd_extension = cfg['DEFAULT']['hd_extension']
proxy_extension = cfg['DEFAULT']['proxy_extension']
new_proxy_extension = cfg['DEFAULT']['new_proxy_extension']
date_format = cfg['DEFAULT']['date_format']
proxy_name = cfg['DEFAULT']['proxy_name']

today = dt.now()
year_folder = str(today.year)
folder_name = today.strftime(date_format) + ' ' + ' '
folder_name = folder_name.strip()
dest_folder = p.join(base_dest_folder, year_folder, folder_name)



class UiMainWindow(object):

    def setupui(self, mainwindow):
        mainwindow.setObjectName("MainWindow")
        mainwindow.resize(800, 580)
        self.centralwidget = QtWidgets.QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")

        self.outBox = QTextEdit(self.centralwidget)
        self.outBox.setReadOnly(True)
        self.outBox.setObjectName("outBox")
        self.outBox.move(20, 80)
        self.outBox.resize(760, 420)
        mainwindow.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(mainwindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 163, 22))
        self.menubar.setObjectName("menubar")
        mainwindow.setMenuBar(self.menubar)

        self.minimpLabel = QLabel(self)
        self.minimpLabel.setText('Src. folder:')
        self.minimp = QLineEdit(self)
        self.minimp.setText(base_src_folder)
        self.minimp.move(124, 30)
        self.minimp.resize(404, 25)
        self.minimpLabel.move(32, 30)
        
        self.minexpLabel = QLabel(self)
        self.minexpLabel.setText('Dest. folder:')
        self.minexp = QLineEdit(self)
        self.minexp.setText(dest_folder)
        self.minexp.move(124, 60)
        self.minexp.resize(404, 25)
        self.minexpLabel.move(32, 60)

        self.mvbutt = QPushButton('mvbutt', self)
        self.mvbutt.move(400, 535)
        self.mvbutt.resize(100, 32)

        self.mkdirbutt = QPushButton('mkdirbutt', self)
        self.mkdirbutt.move(250, 535)
        self.mkdirbutt.resize(100, 32)

        self.listbutt = QPushButton('listbutt', self)
        self.listbutt.move(100, 535)
        self.listbutt.resize(100, 32)

        self.outbutt = QPushButton('outbutt', self)
        self.outbutt.move(550, 535)
        self.outbutt.resize(100, 32)

        self.retranslateui(mainwindow)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)

        exitaction = QAction(QIcon(get_path('./images/exit.png')), '&Exit', self)
        exitaction.setShortcut('Ctrl+Q')
        exitaction.setStatusTip('Exit application')
        exitaction.triggered.connect(self.exitcall)

        aboutaction = QAction(QIcon(get_path('./images/help-about.png')), '&About', self)
        aboutaction.setShortcut('Ctrl+a')
        aboutaction.setStatusTip('About application')
        aboutaction.triggered.connect(self.aboutcall)

        helpaction = QAction(QIcon(get_path('./images/help-contents.png')), '&Help', self)
        helpaction.setShortcut('Ctrl+h')
        helpaction.setStatusTip('Help application')
        helpaction.triggered.connect(self.helpcall)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitaction)
        filemenu = menubar.addMenu('&Help')
        filemenu.addAction(helpaction)
        filemenu.addAction(aboutaction)

    def aboutcall(self):
        msgbox = QMessageBox(self)
        msgbox.about(self, "ABOUT", aboutText)

    def helpcall(self):
        msgbox = QMessageBox(self)
        msgbox.about(self, "HELP", helpText)

    def exitcall(self):
        sys.exit()

    def retranslateui(self, mainwindow):
        _translate = QtCore.QCoreApplication.translate
        mainwindow.setWindowTitle(_translate("mainwindow", "GoPro SD card transfer"))
        mainwindow.setMinimumSize(QSize(800, 580))
        mainwindow.setMaximumSize(QSize(800, 580))
        self.mvbutt.setText(_translate("MainWindow", "Move Files"))
        self.mkdirbutt.setText(_translate("MainWindow", "Make Dir"))
        self.listbutt.setText(_translate("MainWindow", "List Src."))
        self.outbutt.setText(_translate("MainWindow", "List Dest."))

class MainWindow(QtWidgets.QMainWindow, UiMainWindow):
    valueChanged = QtCore.pyqtSignal(str)
    clearScreen = QtCore.pyqtSignal(str)


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupui(self)
        self.valueChanged.connect(self.on_value_changed)
        self.clearScreen.connect(self.on_clear_screen)
        self.mvbutt.clicked.connect(self.on_clicked)
        self.mkdirbutt.clicked.connect(self.on_clicked2)
        self.listbutt.clicked.connect(self.on_clicked3)
        self.outbutt.clicked.connect(self.on_clicked4)

    @QtCore.pyqtSlot()
    def on_clicked(self):
        w.func_clear()
        threading.Thread(target=self.func_move, daemon=True).start()
        
    @QtCore.pyqtSlot()
    def on_clicked2(self):
        w.func_clear()
        threading.Thread(target=self.func_mkdir, daemon=True).start()

    @QtCore.pyqtSlot()
    def on_clicked3(self):
        w.func_clear()
        threading.Thread(target=self.func_inlist, daemon=True).start()

    @QtCore.pyqtSlot()
    def on_clicked4(self):
        w.func_clear()
        threading.Thread(target=self.func_outlist, daemon=True).start()

    @QtCore.pyqtSlot(str)
    def on_value_changed(self, value):
        self.outBox.append(value)

    @QtCore.pyqtSlot(str)
    def on_clear_screen(self, value):
        self.outBox.clear()
        self.outBox.append(value)
        
#    def func_output(self, selected_files):  

    
    def func_mkdir(self):
        dest_folder = self.minexp.text()
        proxy_folder = p.join(dest_folder, proxy_name)
        try:
            md(dest_folder)
            self.valueChanged.emit('<span style="color:Blue;">Created new HD folder: </span>' + dest_folder + '<br>')
        except FileExistsError as exists:
            self.valueChanged.emit('<span style="color:Green;">HD folder exists: </span>' + exists.filename + '<br>')
            self.valueChanged.emit('<span style="color:Green;">Using existing HD folder...</span><br>')
        
        try:
            md(proxy_folder)
            self.valueChanged.emit('<span style="color:Blue;">Created new Proxy folder: </span>' + proxy_folder + '<br>')
        except FileExistsError as exists:
            self.valueChanged.emit('<span style="color:Green;">Proxy folder exists: </span>' + exists.filename + '<br>')
            self.valueChanged.emit('<span style="color:Green;">Using existing Proxy folder...</span><br>')
             
    def func_inlist(self):        
        sd_list = ls(base_src_folder)
        hd_files = [k for k in sd_list if k.endswith(hd_extension)]
        proxy_files = [k for k in sd_list if k.endswith(proxy_extension)]
        str_hd_files = ('<br>'.join(map(str, hd_files)))  
        str_proxy_files = ('<br>'.join(map(str, proxy_files)))  
        self.valueChanged.emit('<span style="color:Blue;">Contents of SD Card:</span><br>')
        self.valueChanged.emit('<span style="color:Green;">HD Files:</span><br>' + str_hd_files + '<br')
        self.valueChanged.emit('<span style="color:Green;">Proxy Files:</span><br>' + str_proxy_files + '<br>')
        
    def func_outlist(self):
        dest_folder = self.minexp.text()        
        hd_list = ls(dest_folder + '/*')
        proxy_list = ls(dest_folder + '/' + proxy_name + '/*')
        hd_files = [k for k in hd_list if k.endswith(hd_extension)]
        proxy_files = [k for k in proxy_list if k.endswith(new_proxy_extension)]        
        str_hd_files = ('<br>'.join(map(str, hd_files)))
        str_proxy_files = ('<br>'.join(map(str, proxy_files))) 
        self.valueChanged.emit('<span style="color:Blue;">Contents of output folders:</span><br>')
        self.valueChanged.emit('<span style="color:Green;">HD Files:</span><br>' + str_hd_files + '<br>')
        self.valueChanged.emit('<span style="color:Green;">Proxy Files:</span><br>' + str_proxy_files + '<br>')

    def func_move(self):
        w.func_mkdir()
        dest_folder = self.minexp.text()
        proxy_folder = p.join(dest_folder, proxy_name)
        sd_files = ls(base_src_folder)
        hd_files = [k for k in sd_files if k.endswith(hd_extension)]
        proxy_files = [k for k in sd_files if k.endswith(proxy_extension)]
        for hd_file in hd_files:
            hd_base = p.splitext(hd_file)[0]            
            mv(hd_file,dest_folder)
#            mv(hd_base + '.THM',dest_folder)            
        for proxy_file in proxy_files:
            proxy_base = p.splitext(proxy_file)[0]
            r(proxy_file, proxy_base + '.' + new_proxy_extension)
            mv(proxy_base + '.' + new_proxy_extension, proxy_folder)      
        w.func_clear()
        w.func_inlist()
        w.func_outlist()  
 
    def func_clear(self):
        self.clearScreen.emit('')
                   
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.func_clear()
    w.func_inlist()
    sys.exit(app.exec_())
