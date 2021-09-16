import os
import glob
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy 
from sqlalchemy import create_engine

data = pd.DataFrame()

def cargarDatos():
    archivos = glob.glob('./Reportes/*.xls')

    valores = []
    for archivo in archivos:
        datos = pd.read_excel(archivo,sheet_name='Engagements by Locations', skiprows=2)
        valores.append(datos)
    
    dframe = pd.concat(valores, ignore_index=True)

    dFrameProcesado = dframe.iloc[:,[1,4,5,15,23,34,42]]


    engine = create_engine('sqlite:///movies.db', echo=True,)
    sqlite_connection = engine.connect()
    sqlite_table= "tablaMovies"
    dFrameProcesado.to_sql(sqlite_table, sqlite_connection,if_exists='replace')
    sqlite_connection.close()




