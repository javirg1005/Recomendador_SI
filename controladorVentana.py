# Imports
import sys
from PyQt5 import QtWidgets, uic

class MyWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(MyWindow,self).__init__()
        uic.loadUi('instagram.ui',self)      

    if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)
        window = MyWindow()
        window.showMaximized()
        sys.exit(app.exec_())