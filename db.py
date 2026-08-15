# db.py
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

# Configuración del Pool
pool = PooledDB(
    creator=pymysql, 
    maxconnections=10, # Máximo de conexiones simultáneas
    mincached=2,       # Conexiones mínimas al arrancar
    blocking=True,     # Esperar si el pool está lleno
    host="200.58.106.156",
    port=3306,
    user="c2710325_killer",
    password="SistemaIES6021",
    database="c2710325_muni",
    charset="utf8mb4",
    cursorclass=DictCursor,
    autocommit=True # Cambiado a True para mayor seguridad en webs concurridas
)

def get_connection():
    return pool.connection()