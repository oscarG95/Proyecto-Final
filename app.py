from flask import Flask, render_template, request, url_for
from flask.helpers import url_for
from werkzeug.utils import redirect
import guardar
import consultas

import os
import glob
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine

app = Flask(__name__)
# headings = []
# data = []
dfResult = pd.DataFrame(index=None)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'


@app.route('/')
def index():
    return "Hello World"

# Cargar todas las peliculas que hay en la base de datos


@app.route('/todos', methods=['POST', 'GET'])
def consultarTodos():
    dfResult = consultas.consultar2("select * from tablaMovies limit 1000")
    dfResult.index = dfResult.index + 1
    dfResult.__delitem__('index')

    

    dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                     index_names=False, justify='left', classes="display cell-border")
    return render_template('todasPelis.html')

# Cargar los datos desde los archivos xls


@app.route('/load')
def load():
    guardar.cargarDatos()
    return "Datos cargados"

# Metodo para filtrar pelicula por nombre


@app.route('/filtrarXpelicula', methods=['POST', 'GET'])
def filtrarPorPelicula():
    if request.method == 'POST':
        movie = request.form["movie"]
        dfResult = consultas.consultar(
            f"select * from tablaMovies where Title='{movie}'")
        dfResult.index = dfResult.index + 1
        dfResult.__delitem__('index')
        dfResult.to_html('./templates/todos.html')
        return render_template('filtrarXmovie.html')
    else:
        dfResult = consultas.consultar(f"select * from tablaMovies")
        dfResult.to_html('./templates/todos.html',
                         table_id="tblPelis", index=False, index_names=False)
        return render_template('filtrarXmovie.html')


# # Consultar por peliculas pasando el nombre de una pelicula como argumento
# @app.route('/movies', methods=['POST', 'GET'])
# def pelicula():
#     if request.method == 'POST':
#         movie = request.form["movie"]
#         return redirect(url_for("consultarPelicula",movie=movie))
#     else:
#         return render_template('filtrarXmovie.html')


# @app.route('/movies/<movie>', methods=['POST', 'GET'])
# def consultarPelicula(movie):
#     movie2=movie
#     dfResult = consultas.consultar(f"select * from tablaMovies where Title='{movie2}'")
#     dfResult.to_html('./templates/todos.html')
#     movie = request.form["movie"]
#     pelicula()
#     # movie = request.form["movie"]
#     # return redirect(url_for('pelicula',movie=movie))

#     return render_template('filtrarPeliculas.html')

@app.route('/prueba')
def prueba():
    dfResult = consultas.consultar(
        f"SELECT  Pelicula,SUM(AsistenciaSemanal) AS Asistencia_Semanal, Year FROM tablaMovies WHERE Year = '2019' GROUP BY Pelicula")
    dfResult.index = dfResult.index + 1
    dfResult.__delitem__('index')
    
    dfResult.to_html('./templates/todos.html',
                     table_id="myTable", index=False, index_names=False)
    return render_template('todasPelis.html')


@app.route('/asistenciaporpais')
def asistenciaPorPais():
    dfResult = consultas.consultar(
        "select Pais, sum(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies group BY Pais")
    # dfResult.index = dfResult.index + 1
    # dfResult.__delitem__('index')

   
    
    dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                     index_names=False, justify='left', classes="display cell-border")
    return render_template('asistenciaPais.html')


@app.route('/asistenciaporcadena')
def asistenciaPorCadena():
    dfResult = consultas.consultar(
        "SELECT Cadena ,sum(AsistenciaSemanal) as Asistencia_Semanal, Pais FROM tablaMovies group by Cadena, Pais order by Pais")
    # dfResult.index = dfResult.index + 1
    # dfResult.__delitem__('index')
    dfResult['Porcentaje']= (dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
    dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                     index_names=False, justify='left', classes="display cell-border")
    return render_template('asistenciaPorCadena.html')


@app.route('/asistenciaporpelicula')
def asistenciaPorPelicula():
    dfResult = consultas.consultar(
        "SELECT  Pais, Pelicula,SUM(AsistenciaSemanal) AS Asistencia_Semanal FROM tablaMovies GROUP BY Pelicula, Pais order by Asistencia_Semanal DESC limit 5")
    # dfResult.index = dfResult.index + 1
    # dfResult.__delitem__('index')
    dfResult['Porcentaje']= (dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
    dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                     index_names=False, justify='left', classes="display cell-border")
    return render_template('asistenciaPorPelicula.html')



if __name__ == "__main__":
    app.run(debug=True)
