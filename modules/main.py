# modules/main.py
from flask import Blueprint, render_template
from db import get_connection

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    conn = get_connection()
    destacada = None
    recientes = []
    
    try:
        with conn.cursor() as cursor:
            # 1. Obtener la última destacada
            cursor.execute("SELECT * FROM noticias WHERE es_destacada = 1 ORDER BY fecha_creacion DESC LIMIT 1")
            destacada = cursor.fetchone()
            
            # 2. Obtener las demás noticias
            if destacada:
                cursor.execute("SELECT * FROM noticias WHERE id != %s ORDER BY fecha_creacion DESC LIMIT 6", (destacada['id'],))
            else:
                cursor.execute("SELECT * FROM noticias ORDER BY fecha_creacion DESC LIMIT 6")
                
            recientes = cursor.fetchall()
    finally:
        conn.close()

    return render_template("index.html", destacada=destacada, recientes=recientes)