# Imports
import sys
from PyQt5 import QtWidgets, uic

#Recomendar
usuario = ""
n_pelis = ""
u_sim = ""
#Predecir
pred_usu = ""
pred_peli = ""


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
    
    def get_usu(): #Recoge usuario de recomendacion
        return "usu"

    def get_npelis(): #Recoge numero de pelis a mostrar en la tabla de recomendacion
        return "npelis"

    def get_u_sim(): #Recoge umbral de similitud de recomendacion
        return "u_sim"

    def get_pred_usu(): #Recoge el usuario de prediccion
        return "u_sim"
    
    def get_pred_peli(): #Recoge el peli de prediccion
        return "pred_peli"

    def controlador_comboBox(self):
        value = str(self.comboBox_Algoritmo.currentText())

        if value == "Naive Bayes":
                self.txt_Algoritmo.setText("Naive Bayes")
        elif value == "Árbol de decisión":
                self.txt_Algoritmo.setText("Árbol de decisión")
        elif value == "k-NN":
                self.txt_Algoritmo.setText("k-NN")



#Método main de la aplicación
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())