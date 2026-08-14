# db.py
import pymysql
from pymysql.cursors import DictCursor

def get_connection():
    return pymysql.connect(
        host="200.58.106.156",
        port=3306,
        user="c2710325_killer",
        password="SistemaIES6021",
        database="c2710325_muni",
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False
    )
