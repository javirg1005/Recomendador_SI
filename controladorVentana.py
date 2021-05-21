# Imports
import sys
from PyQt5 import QtWidgets, uic

#Recomendar
usuario = ""
n_pelis = ""
u_sim = ""
#Predecir
pred_usu = ""
pref_peli = ""


class MyWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MyWindow,self).__init__()
        uic.loadUi('interfaz.ui',self)      

        #Metodos de botones
        self.btn_reco.clicked.connect(self.controlador_recomendar)

        self.btn_pred.clicked.connect(self.controlador_predecir)

    def controlador_recomendar():
        print("Recomiendo")

    def controlador_predecir():
        print("Predizco")

#Método main de la aplicación
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.showMaximized()
    sys.exit(app.exec_())