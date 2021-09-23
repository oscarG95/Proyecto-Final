from app import index
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy 
from sqlalchemy import create_engine

engine = create_engine('sqlite:///movies.db', echo=True,)

def consultar(consulta):
    dfTodos = pd.read_sql_query(consulta, engine)
    return dfTodos

def consultar2(consulta):
    dfTodos = pd.read_sql_query(consulta, engine)
    decimals = 2    
    dfTodos['RecaudacionFinde'] = dfTodos['RecaudacionFinde'].apply(lambda x: round(x, decimals))
    dfTodos['RecaudacionSemanal'] = dfTodos['RecaudacionSemanal'].apply(lambda x: round(x, decimals))
    return dfTodos