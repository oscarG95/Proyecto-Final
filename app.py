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
    return render_template('index.html')

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
    return redirect('/todos')

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


def filtarFecha(dfResult):
    # dfResult[['StartDate', 'EndDate']] = dfResult[['StartDate', 'EndDate']].apply((pd.to_datetime(format="%m/%d")))
    dfResult['StartDate'] = dfResult['StartDate'].map(
        str) + "/" + dfResult['Year']
    dfResult['EndDate'] = dfResult['EndDate'].map(str) + "/" + dfResult['Year']
    dfResult['StartDate'] = pd.to_datetime(
        (dfResult['StartDate']), format="%m/%d/%Y")
    dfResult['EndDate'] = pd.to_datetime(
        (dfResult['EndDate']), format="%m/%d/%Y")
    return dfResult

def aproximar(dfTodos):
    decimals = 2    
    dfTodos['Recaudacion'] = dfTodos['Recaudacion'].apply(lambda x: round(x, decimals))
    return dfTodos


@app.route('/prueba', methods=['POST', 'GET'])
def prueba():
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar2(
            f"SELECT * from TablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'")
        dfResult.index = dfResult.index + 1
        dfResult.__delitem__('index')

        dfResult.to_html('./templates/todos.html', table_id="tblTodos",
                         index_names=False, justify='left', classes="display cell-border")

        return render_template('prueba.html')
    else:
        dfResult = consultas.consultar2("select * from tablaMovies limit 1000")
        dfResult.index = dfResult.index + 1
        dfResult.__delitem__('index')

        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('prueba.html')


# Total  de asistencia semanal para cada país
@app.route('/asistenciaporpais', methods=['POST', 'GET'])
def asistenciaPorPais():
    descripcion = "Total  de asistencia semanal para cada país:"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"select Pais, sum(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group BY Pais")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"select Pais, sum(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies group BY Pais")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)


# Total de sistencia semanal por cadena de cine para cada país
@app.route('/asistenciaporcadena', methods=['POST', 'GET'])
def asistenciaPorCadena():
    descripcion = "Asistencia por cadena de cine"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"SELECT Cadena ,sum(AsistenciaSemanal) as Asistencia_Semanal, Pais FROM tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group BY Cadena, Pais ORDER BY Pais")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"SELECT Cadena ,sum(AsistenciaSemanal) as Asistencia_Semanal, Pais FROM tablaMovies group BY Cadena, Pais ORDER BY Pais")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)


# Top 5 Peliculas Mayor Asistencia
@app.route('/asistenciaporpelicula', methods=['POST', 'GET'])
def asistenciaPorPelicula():
    descripcion = "Top 5 Peliculas Mayor Asistencia:"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select  Pelicula, sum(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group BY Pelicula ORDER BY Asistencia_Semanal DESC limit 5")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"Select  Pelicula, sum(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies group by Pelicula order by Asistencia_Semanal DESC limit 5")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)



# Película con mayor asistencia por cada cadena de cine
@app.route('/peliculasporcadena', methods=['POST', 'GET'])
def asistenciaPorPeliculas():
    descripcion = "Asistencia por Cadena"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select  Cadena, Pelicula, Pais, max(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Cadena, Pais ORDER BY Asistencia_Semanal DESC")
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"Select  Cadena, Pelicula, Pais, max(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies group by Cadena,Pais order by Asistencia_Semanal")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)


#Peliculas más vistas por cadena y pais
@app.route('/peliculasporcadenapais', methods=['POST', 'GET'])
def pelicula_Cadena_Pais():
    descripcion = "Peliculas por Cadena,Pais"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select Pais, Pelicula,Cadena,sum(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}' group by Pelicula,Cadena order by Cadena,Pais,Asistencia_Semanal DESC")
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"Select Pais, Pelicula,Cadena,sum(AsistenciaSemanal) as Asistencia_Semanal from tablaMovies group by Pelicula, Cadena order by Cadena, Pais,Asistencia_Semanal DESC")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)

#Peliculas mas vistas en fin de semana
@app.route('/peliculasfinde', methods=['POST', 'GET'])
def masvistasfinde():
    descripcion = "Películas mas vistas en Fin de Semana por Cadena"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select Cadena,Pais,Pelicula, max(AsistenciaFinde) as Asistencia_Finde from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}' group by Cadena, Pais order by Asistencia_Finde DESC")
        total = dfResult['Asistencia_Finde'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Finde']/dfResult['Asistencia_Finde'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"Select  Cadena, Pais, Pelicula, max(AsistenciaFinde) as Asistencia_Finde from tablaMovies group by Cadena, Pais Order By Asistencia_Finde DESC")
        dfResult.index = dfResult.index + 1
        total = dfResult['Asistencia_Finde'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Finde']/dfResult['Asistencia_Finde'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)

#Asistencia Por Pelicula
@app.route('/asistenciapelicula', methods=['POST', 'GET'])
def asistenciaPelicula():
    descripcion = "Asistencia por Pelicula"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select Pelicula, sum(AsistenciaSemanal) as Asistencia_Semanal, sum(RecaudacionSemanal) as Recaudacion from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Pelicula ORDER BY Asistencia_Semanal DESC")
        dfResult=aproximar(dfResult)
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"Select  Pelicula, sum(AsistenciaSemanal) as Asistencia_Semanal, sum(RecaudacionSemanal) as Recaudacion from tablaMovies group by Pelicula order by Asistencia_Semanal")
        dfResult.index = dfResult.index + 1
        dfResult=aproximar(dfResult)
        total = dfResult['Asistencia_Semanal'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Asistencia_Semanal']/dfResult['Asistencia_Semanal'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista.html', total=total, descripcion=descripcion)


########################################################################################################################################
# Peliculas con mayor recaudacion por pais
@app.route('/mayorrecaudacion_pais', methods=['POST', 'GET'])
def mayorRecaudacion():
    descripcion = "Peliculas mas taquillera en cada pais"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select  Pais, Pelicula, max(RecaudacionSemanal) as Recaudacion from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Pais")
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"Select  Pais, Pelicula, max(RecaudacionSemanal) as Recaudacion from tablaMovies group by Pais")
        dfResult.index = dfResult.index + 1
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)

# Peliculas con mayor recaudacion por Cadena
@app.route('/mayorrecaudacion_cadena', methods=['POST', 'GET'])
def mayorRecaudacion_Cadena():
    descripcion = "Peliculas mas taquillera en cada Cadena"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select  Cadena, Pelicula, Pais, max(RecaudacionSemanal) as Recaudacion from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Cadena, Pais")
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"Select  Cadena, Pelicula,Pais, max(RecaudacionSemanal) as Recaudacion from tablaMovies group by Cadena, Pais")
        dfResult.index = dfResult.index + 1
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)

#Recaudacion por pais
@app.route('/recaudacionpais', methods=['POST', 'GET'])
def recaudacionPais():
    descripcion = "Recaudacion Semanal por Pais"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select Pais, sum(RecaudacionSemanal) as Recaudacion from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Pais")
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"select Pais, sum(RecaudacionSemanal) as Recaudacion from tablaMovies group by Pais")
        dfResult.index = dfResult.index + 1
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)

@app.route('/recaudacioncadena', methods=['POST','GET'])
def recaudacionCadena():
    descripcion = "Recaudacion Semanal por Cadena"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select Cadena, Pais, sum(RecaudacionSemanal) as Recaudacion from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Cadena,Pais")
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"select Cadena, Pais, sum(RecaudacionSemanal) as Recaudacion from tablaMovies group by Cadena, Pais")
        dfResult.index = dfResult.index + 1
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)


@app.route('/recaudacionpelicula', methods=['POST','GET'])
def recaudacionPelicula():
    descripcion = "Recaudacion Semanal por Cadena"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select  Pelicula, sum(RecaudacionSemanal) as Recaudacion from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Pelicula")
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"select Pelicula, sum(RecaudacionSemanal) as Recaudacion from tablaMovies group by Pelicula")
        dfResult.index = dfResult.index + 1
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)

@app.route('/recaudacionpeliculaporcadena', methods=['POST','GET'])
def recaudacionPeliculaCadena():
    descripcion = "Recaudacion Pelicula por Cadena"
    if request.method == 'POST':
        startDate = request.form['startD']
        endDate = request.form['endD']
        dfResult = consultas.consultar(
            f"Select  Pelicula,Cadena,Pais, sum(RecaudacionSemanal) as Recaudacion from tablaMovies where StartDate BETWEEN'{startDate}' AND '{endDate}'  group by Pelicula, Cadena")
        dfResult=aproximar(dfResult)
        dfResult.index = dfResult.index + 1
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)
    else:
        dfResult = consultas.consultar(
            f"select Pelicula, Cadena, Pais, sum(RecaudacionSemanal) as Recaudacion from tablaMovies group by Pelicula, Cadena")
        dfResult.index = dfResult.index + 1
        dfResult=aproximar(dfResult)
        total = dfResult['Recaudacion'].sum()
        dfResult['Porcentaje'] = (
            dfResult['Recaudacion']/dfResult['Recaudacion'].sum()) * 100
        dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=True,
                         index_names=False, justify='left', classes="display cell-border")
        return render_template('vista2.html', total=total, descripcion=descripcion)


if __name__ == "__main__":
    app.run(debug=True)
