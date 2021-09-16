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