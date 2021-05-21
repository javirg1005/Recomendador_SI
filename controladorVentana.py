# Imports
import sys
from PyQt5 import QtWidgets, uic
import recomendador as reco
import re




class MyWindow(QtWidgets.QMainWindow):
    
    def post_usu(self):
        users = []
        users_ints = reco.obtenerUsuarios()
        for user in users_ints:
            users.append("ID. " + str(user[0]))
        return users

    def post_peli(self, usu):
        pelis = []
        pelis_tupla = reco.obtenerPelis(usu)
        for peli in pelis_tupla:
            pelis.append("ID. " + str(peli[0]) + ". " + str(peli[1]))
        return pelis

    def __init__(self):
        super(MyWindow,self).__init__()
        uic.loadUi('interfaz.ui',self)      

        #Cargar los datos en las combobox
        usus = self.post_usu()
       

        self.cbox_usu.clear()
        self.cbox_usu.addItems(usus)

        self.cbox_usu_pred.clear()
        self.cbox_usu_pred.addItems(usus)

        #Acciones de botones botones
        self.btn_reco.clicked.connect(self.controlador_recomendar)

        self.btn_pred.clicked.connect(self.controlador_predecir)

        self.btn_selec_usu.clicked.connect(self.controlador_select_usu)

    #BOTONES
    
    def controlador_recomendar(self):
        print("Intento recomendar")
        usu = self.get_usu()
        print("Usuario: " + usu)
        n_pelis = self.get_npelis()
        print("Número de filas: " + n_pelis)
        u_sim = self.get_u_sim()
        print("Umbral: " + u_sim)

    def controlador_predecir(self):
        usu = self.get_pred_usu()
        peli = self.get_pred_peli()
        print("Usuario: " + usu)
        print("Pelicula: " + peli)

        print("Intento predecir")

    def controlador_select_usu(self):
        usu = self.get_usu()
        pelis = self.post_peli(usu)
        self.cbox_mov.clear()
        self.cbox_mov.addItems(pelis)

        print("Usuario seleccionado")
        
    
    #COMBOX  - #DONE no tocar
    
    def get_usu(self): #Recoge usuario de recomendacion
        cbox_value = str(self.cbox_usu.currentText())
        userId = re.match("ID\.\s*(\d*)", cbox_value)
        return userId.group(1)

    def get_pred_usu(self): #Recoge el usuario de prediccion
        cbox_value = str(self.cbox_usu_pred.currentText())
        userId = re.match("ID\.\s*(\d*)", cbox_value)
        return userId.group(1)


    def get_pred_peli(self): #Recoge el peli de prediccion
        cbox_value = str(self.cbox_mov.currentText())
        movId = re.match("ID\.\s*(\d*)", cbox_value)
        return movId.group(1)
    
    #TEXTFIELD - #DONE no tocar
    
    def get_npelis(self): #Recoge numero de pelis a mostrar en la tabla de recomendacion
        n_pelis = self.te_filas.toPlainText()
        return n_pelis

    def get_u_sim(self): #Recoge umbral de similitud de recomendacion
        u_sim = self.te_umbral.toPlainText()
        return u_sim
    
    #QTABLE



    #LABELS
    def set_label(self, pred):
        self.lbl_prediccion.setText("La prediccion es de " + pred)


    #PROGESSBAR



#Método main de la aplicación
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())