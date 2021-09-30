import os
import glob
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy 
from sqlalchemy import create_engine
import xlrd
data = pd.DataFrame()

def filtarFecha(dfResult):
    #dfResult[['StartDate', 'EndDate']] = dfResult[['StartDate', 'EndDate']].apply((pd.to_datetime(format="%m/%d")))
    dfResult['StartDate'] = dfResult['StartDate'].map(str) + "/" + dfResult['Year']
    dfResult['EndDate'] = dfResult['EndDate'].map(str) + "/" + dfResult['Year']
    dfResult['StartDate'] = pd.to_datetime((dfResult['StartDate']), format="%m/%d/%Y")
    dfResult['EndDate'] = pd.to_datetime((dfResult['EndDate']), format="%m/%d/%Y")
    dfResult.__delitem__('Year')
    return dfResult

#############################################
def leer(ruta):
    archivo = ruta
    wb = xlrd.open_workbook(archivo)
    hoja = wb.sheet_by_index(0)
    row = hoja.cell_value(1, 0)

    arrayInfo = row.split(sep=",")
    arrayFecha = arrayInfo[2].split(sep=" ")

    pais = arrayInfo[0]
    fechaInicio = arrayFecha[3]
    fechaFin = arrayFecha[5].split("/")
    valores = []
    valores.append(pais)
    valores.append(fechaInicio)
    valores.append(fechaFin[0] + '/' + fechaFin[1])
    valores.append(fechaFin[2])
    return valores

################################################


def cargarDatos():
    archivos = glob.glob('./Reportes/*.xls')

    valores = []

    for archivo in archivos:
##################################################
        informacionArchivo = leer(archivo)
##################################################
        datos = pd.read_excel(archivo,sheet_name='Engagements by Locations', skiprows=2)
##########################
        datos = datos.assign(Country=informacionArchivo[0], StartDate=informacionArchivo[1], EndDate=informacionArchivo[2], Year=informacionArchivo[3])
##########################
        valores.append(datos)
    
    dframe = pd.concat(valores, ignore_index=True)

    dFrameProcesado = dframe.iloc[:,[1,4,5,15,23,34,42,46,47,48,49]]

    dFrameProcesado.columns = ['Pelicula','Cine','Cadena','AsistenciaFinde','AsistenciaSemanal','RecaudacionFinde','RecaudacionSemanal','Pais','StartDate','EndDate','Year'] 
    dFrameProcesado = filtarFecha(dFrameProcesado)


# Crear tabla en la base de datos e insertarlos
    engine = create_engine('sqlite:///movies.db', echo=True,)
    sqlite_connection = engine.connect()
    sqlite_table= "tablaMovies"
    dFrameProcesado.to_sql(sqlite_table, sqlite_connection,if_exists='replace')
    sqlite_connection.close()




