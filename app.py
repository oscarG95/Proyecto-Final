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
    dfResult = consultas.consultar("select * from tablaMovies limit 10")
    dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False, index_names=False)
    return render_template('todasPelis.html')

#Cargar los datos desde los archivos xls
@app.route('/load')
def load():
    guardar.cargarDatos()
    return "Datos cargados"




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

@app.route('/filtrarXpelicula', methods=['POST', 'GET'])
def pelicula2():
    if request.method == 'POST':
        movie = request.form["movie"]
        dfResult = consultas.consultar(f"select * from tablaMovies where Title='{movie}'")
        dfResult.to_html('./templates/todos.html')
        return render_template('filtrarXmovie.html')
    else:
        dfResult= consultas.consultar(f"select * from tablaMovies")
        dfResult.to_html('./templates/todos.html', table_id="tblPelis", index=False, index_names=False)
        return render_template('filtrarXmovie.html')
        
if __name__ == "__main__":
    app.run(debug=True)