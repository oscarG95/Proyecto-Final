from flask import Flask, render_template
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


@app.route('/todos', methods=['POST', 'GET'])
def consultarTodos():
    dfResult = consultas.consultar("select * from tablaMovies limit 10")
    dfResult.to_html('./templates/todos.html', table_id="tblTodos", index=False, index_names=False)
    return render_template('base.html')


@app.route('/load')
def load():
    guardar.cargarDatos()
    return "Datos cargados"

# Consultar por peliculas pasando el nombre de una pelicula como argumento
@app.route('/movies/<movie>', methods=['POST', 'GET'])
def consultarPorPelicula(movie):
    movie2 =movie
    dfResult = consultas.consultar(f"select * from tablaMovies where Title='{movie2}'")
    dfResult.to_html('./templates/todos.html')
    return render_template('movie.html')



if __name__ == "__main__":
    app.run(debug=True)