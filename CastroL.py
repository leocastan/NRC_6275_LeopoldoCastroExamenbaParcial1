# Importar la biblioteca de flask y librerias necesarias
# Repositorio Git https://github.com/leocastan/NRC_6275_LeopoldoCastroExamenbaParcial1.git
from tkinter import messagebox
from flask import Flask, redirect, render_template, request, url_for, flash
import pickle
import datetime
import requests
import os
import argparse
import re
import json
from dateutil.easter import easter
from dateutil.relativedelta import relativedelta as rd, FR
from holidays.constants import JAN, MAY, AUG, OCT, NOV, DEC
from holidays.holiday_base import HolidayBase




# Instanciar la aplicación
# Nombre por defecto y ruta donde están los modelos
app = Flask(__name__)

# Arreglo para almacenar las tareas
listaLlamadas = []

# 1. Funcion controlador que muestra lista actual de tareas pendientes y un formulario para ingresar un nuevo elemento
# Definicion de la ruta por defecto,
@app.route('/')
# Lamar a principal
def home():
    return render_template('index.html', listaLlamadas=listaLlamadas)

# 2. Funcion controlador para agregar llamada a lista de llamadas
# Definicion de la ruta
@app.route('/enviar', methods=['POST'])
# Llamar a enviar
def enviar():
    # Funcion condicional para enviar los datos del formulario
    if request.method == 'POST':

        nroLlamada = request.form['nroLlamada']
        placaVehiculo = request.form['placaVehiculo']
        fecha = request.form['fecha']
        hora = request.form['hora']
        prediccion = request.form['prediccion']



        # Funcion condicional para no registrar en caso de datos vacios
        if nroLlamada == '' or placaVehiculo == '' or fecha == '' or hora == '' or prediccion == '':
            #Mensaje de alerta de campos faltantes
            messagebox.showwarning("¡Alerta!","Ingrese todos los campos")
            return redirect(url_for('home'))
        else:
            #Mensaje de autorizacion de registro
            resultado = messagebox.askquestion("Registrar", "¿Está seguro que desea registrar los datos?")
            #Funcion condicional de confirmacion de registro
            if resultado == "yes":
                listaLlamadas.append({'nroLlamada': nroLlamada, 'placaVehiculo': placaVehiculo, 'fecha': fecha, 'hora': hora, 'prediccion': prediccion })
                return redirect(url_for('home'))
            else:
                return redirect(url_for('home'))

# 3. Funcion controlador para borrar la lista de tareas
@app.route('/borrar', methods=['POST'])
def borrar():
    if request.method == 'POST':
        # Funcion condicional para mostrar alerta en caso de no existir
        if listaLlamadas == []:
            messagebox.showwarning("¡Alerta!", "No existen llamadas pendientes")
            return redirect(url_for('home'))
        else:
            # Mensaje de autorizacion de borrado
            resultado = messagebox.askquestion(
                "Borrar datos", "¿Está seguro de que desea borrar los datos?")
            # Funcion condicional de confirmacion de borrado
            if resultado == "yes":
                messagebox.showinfo("Info", "Los datos han sido borrados")
                listaLlamadas.clear()
                return redirect(url_for('home'))
            else:
                return redirect(url_for('home'))

# 4. Funcion controlador para guardar registros en archivo *.pickle
@app.route('/guardar', methods=['POST'])
def guardar():
    if request.method == 'POST':
        # Funcion condicional para mostrar alerta en caso de no existir
        if listaLlamadas == []:
            messagebox.showwarning(
                "¡Alerta!", "No existen llamdas para almacenar")
            return redirect(url_for('home'))
        else:
            # Mensaje de autorizacion de guardado
            resultado = messagebox.askquestion(
                "Guardar registros", "¿Está seguro de que desea guardar los datos?")
            # Funcion condicional de confirmacion de guardado
            if resultado == "yes":
                # Funcion de creacion y sobreescritura de archivo *.pickle
                with open('llamadas.pickle', 'wb') as f:
                    llamadas = {'llamadas': listaLlamadas}
                    pickle.dump(llamadas, f)
                messagebox.showinfo("Info", "Los datos han sido guardados")
                return redirect(url_for('home'))
            else:
                return redirect(url_for('home'))

#llamar a holidays

#Holidays para ecuador
class HolidayEcuador(HolidayBase):
    """
    A class to represent a Holiday in Ecuador by province (HolidayEcuador)
    It aims to make determining whether a 
    specific date is a holiday as fast and flexible as possible.
    https://www.turismo.gob.ec/wp-content/uploads/2020/03/CALENDARIO-DE-FERIADOS.pdf
    ...
    Attributes (It inherits the HolidayBase class)
    ----------
    prov: str
        province code according to ISO3166-2
    Methods
    -------
    __init__(self, plate, date, time, online=False):
        Constructs all the necessary attributes for the HolidayEcuador object.
    _populate(self, year):
        Returns if a date is holiday or not
    """     
    # ISO 3166-2 codes for the principal subdivisions, called provinces
    # https://es.wikipedia.org/wiki/ISO_3166-2:EC
    PROVINCES = ["EC-P"]  # TODO add more provinces

    def __init__(self, **kwargs):
        """
        Constructs all the necessary attributes for the HolidayEcuador object.
        """         
        self.country = "ECU"
        self.prov = kwargs.pop("prov", "ON")
        HolidayBase.__init__(self, **kwargs)

    def _populate(self, year):
        """
        Checks if a date is holiday or not
        
        Parameters
        ----------
        year : str
            year of a date
        Returns
        -------
        Returns true if a date is a holiday otherwise flase 
        """                    
        # New Year's Day 
        self[datetime.date(year, JAN, 1)] = "Año Nuevo [New Year's Day]"
        
        # Christmas
        self[datetime.date(year, DEC, 25)] = "Navidad [Christmas]"
        
        # Holy Week
        self[easter(year) + rd(weekday=FR(-1))] = "Semana Santa (Viernes Santo) [Good Friday)]"
        self[easter(year)] = "Día de Pascuas [Easter Day]"
        
        # Carnival
        total_lent_days = 46
        self[easter(year) - datetime.timedelta(days=total_lent_days+2)] = "Lunes de carnaval [Carnival of Monday)]"
        self[easter(year) - datetime.timedelta(days=total_lent_days+1)] = "Martes de carnaval [Tuesday of Carnival)]"
        
        # Labor day
        name = "Día Nacional del Trabajo [Labour Day]"
        # (Law 858/Reform Law to the LOSEP (in force since December 21, 2016 /R.O # 906)) If the holiday falls on Saturday or Tuesday
        # the mandatory rest will go to the immediate previous Friday or Monday
        # respectively
        if year > 2015 and datetime.date(year, MAY, 1).weekday() in (5,1):
            self[datetime.date(year, MAY, 1) - datetime.timedelta(days=1)] = name
        # (Law 858/Reform Law to the LOSEP (in force since December 21, 2016 /R.O # 906)) if the holiday falls on Sunday
        # the mandatory rest will go to the following Monday
        elif year > 2015 and datetime.date(year, MAY, 1).weekday() == 6:
            self[datetime.date(year, MAY, 1) + datetime.timedelta(days=1)] = name
        # (Law 858/Reform Law to the LOSEP (in force since December 21, 2016 /R.O # 906)) Holidays that are on Wednesday or Thursday
        # will be moved to the Friday of that week
        elif year > 2015 and  datetime.date(year, MAY, 1).weekday() in (2,3):
            self[datetime.date(year, MAY, 1) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, MAY, 1)] = name
        
        # Pichincha battle, the rules are the same as the labor day
        name = "Batalla del Pichincha [Pichincha Battle]"
        if year > 2015 and datetime.date(year, MAY, 24).weekday() in (5,1):
            self[datetime.date(year, MAY, 24).weekday() - datetime.timedelta(days=1)] = name
        elif year > 2015 and datetime.date(year, MAY, 24).weekday() == 6:
            self[datetime.date(year, MAY, 24) + datetime.timedelta(days=1)] = name
        elif year > 2015 and  datetime.date(year, MAY, 24).weekday() in (2,3):
            self[datetime.date(year, MAY, 24) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, MAY, 24)] = name        
        
        # First Cry of Independence, the rules are the same as the labor day
        name = "Primer Grito de la Independencia [First Cry of Independence]"
        if year > 2015 and datetime.date(year, AUG, 10).weekday() in (5,1):
            self[datetime.date(year, AUG, 10)- datetime.timedelta(days=1)] = name
        elif year > 2015 and datetime.date(year, AUG, 10).weekday() == 6:
            self[datetime.date(year, AUG, 10) + datetime.timedelta(days=1)] = name
        elif year > 2015 and  datetime.date(year, AUG, 10).weekday() in (2,3):
            self[datetime.date(year, AUG, 10) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, AUG, 10)] = name       
        
        # Guayaquil's independence, the rules are the same as the labor day
        name = "Independencia de Guayaquil [Guayaquil's Independence]"
        if year > 2015 and datetime.date(year, OCT, 9).weekday() in (5,1):
            self[datetime.date(year, OCT, 9) - datetime.timedelta(days=1)] = name
        elif year > 2015 and datetime.date(year, OCT, 9).weekday() == 6:
            self[datetime.date(year, OCT, 9) + datetime.timedelta(days=1)] = name
        elif year > 2015 and  datetime.date(year, MAY, 1).weekday() in (2,3):
            self[datetime.date(year, OCT, 9) + rd(weekday=FR)] = name
        else:
            self[datetime.date(year, OCT, 9)] = name        
        
        # Day of the Dead and
        namedd = "Día de los difuntos [Day of the Dead]" 
        # Independence of Cuenca
        nameic = "Independencia de Cuenca [Independence of Cuenca]"
        #(Law 858/Reform Law to the LOSEP (in force since December 21, 2016 /R.O # 906)) 
        #For national and/or local holidays that coincide on continuous days, 
        #the following rules will apply:
        if (datetime.date(year, NOV, 2).weekday() == 5 and  datetime.date(year, NOV, 3).weekday() == 6):
            self[datetime.date(year, NOV, 2) - datetime.timedelta(days=1)] = namedd
            self[datetime.date(year, NOV, 3) + datetime.timedelta(days=1)] = nameic     
        elif (datetime.date(year, NOV, 3).weekday() == 2):
            self[datetime.date(year, NOV, 2)] = namedd
            self[datetime.date(year, NOV, 3) - datetime.timedelta(days=2)] = nameic
        elif (datetime.date(year, NOV, 3).weekday() == 3):
            self[datetime.date(year, NOV, 3)] = nameic
            self[datetime.date(year, NOV, 2) + datetime.timedelta(days=2)] = namedd
        elif (datetime.date(year, NOV, 3).weekday() == 5):
            self[datetime.date(year, NOV, 2)] =  namedd
            self[datetime.date(year, NOV, 3) - datetime.timedelta(days=2)] = nameic
        elif (datetime.date(year, NOV, 3).weekday() == 0):
            self[datetime.date(year, NOV, 3)] = nameic
            self[datetime.date(year, NOV, 2) + datetime.timedelta(days=2)] = namedd
        else:
            self[datetime.date(year, NOV, 2)] = namedd
            self[datetime.date(year, NOV, 3)] = nameic  
            
        # Foundation of Quito, applies only to Pichincha province, 
        # the rules are the same as the labor day
        name = "Fundación de Quito [Foundation of Quito]"        
        if self.prov in ("EC-P"):
            if year > 2015 and datetime.date(year, DEC, 6).weekday() in (5,1):
                self[datetime.date(year, DEC, 6) - datetime.timedelta(days=1)] = name
            elif year > 2015 and datetime.date(year, DEC, 6).weekday() == 6:
                self[(datetime.date(year, DEC, 6).weekday()) + datetime.timedelta(days=1)] =name
            elif year > 2015 and  datetime.date(year, DEC, 6).weekday() in (2,3):
                self[datetime.date(year, DEC, 6) + rd(weekday=FR)] = name
            else:
                self[datetime.date(year, DEC, 6)] = name


# Metodo main del programa
if __name__ == '__main__':
    # debug = True, para reiniciar automatica el servidor
    app.run(debug=True)
