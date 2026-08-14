# modules/noticias.py
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
from db import get_connection

noticias_bp = Blueprint('noticias', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif', 'webp'}

def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@noticias_bp.route('/admin_noticias')
def admin_noticias():
    conn = get_connection()
    destacada = None
    recientes = []
    try:
        with conn.cursor() as cursor:
            # Obtener destacada
            cursor.execute("SELECT * FROM noticias WHERE es_destacada = 1 ORDER BY fecha_creacion DESC LIMIT 1")
            destacada = cursor.fetchone()
            
            # Obtener restantes
            if destacada:
                cursor.execute("SELECT * FROM noticias WHERE id != %s ORDER BY fecha_creacion DESC", (destacada['id'],))
            else:
                cursor.execute("SELECT * FROM noticias ORDER BY fecha_creacion DESC")
            
            recientes = cursor.fetchall()
    finally:
        conn.close()
        
    return render_template('admin_noticias.html', destacada=destacada, recientes=recientes)

# Crear Noticia
@noticias_bp.route('/crear-noticia', methods=['POST'])
def crear_noticia():
    titulo = request.form.get('titulo')
    subtitulo = request.form.get('subtitulo')
    cuerpo = request.form.get('cuerpo')
    epigrafe = request.form.get('epigrafe')
    categoria = request.form.get('categoria')
    es_destacada = 1 if request.form.get('es_destacada') else 0

    file = request.files.get('imagen')
    filename = 'default.jpg'
    
    if file and file.filename != '' and archivo_permitido(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{int(datetime.now().timestamp())}_{filename}"
        upload_path = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Si se marca como destacada, quitar el estado de destacada a las demás
            if es_destacada == 1:
                cursor.execute("UPDATE noticias SET es_destacada = 0")

            sql = """
                INSERT INTO noticias (titulo, subtitulo, cuerpo, imagen_url, epigrafe, categoria, es_destacada, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (titulo, subtitulo, cuerpo, filename, epigrafe, categoria, es_destacada))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al insertar noticia: {e}")
    finally:
        conn.close()

    return redirect(url_for('noticias.admin_noticias'))

# Editar Noticia
@noticias_bp.route('/editar-noticia', methods=['POST'])
def editar_noticia():
    id_noticia = request.form.get('id')
    
    # Validar que tengamos un ID válido
    if not id_noticia:
        return redirect(url_for('noticias.admin_noticias'))

    titulo = request.form.get('titulo')
    subtitulo = request.form.get('subtitulo')
    cuerpo = request.form.get('cuerpo')
    epigrafe = request.form.get('epigrafe')
    categoria = request.form.get('categoria')
    es_destacada = 1 if request.form.get('es_destacada') else 0

    file = request.files.get('imagen')
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Si esta noticia se marca como destacada, quitar el atributo a las demás
            if es_destacada == 1:
                cursor.execute("UPDATE noticias SET es_destacada = 0 WHERE id != %s", (id_noticia,))

            if file and file.filename != '' and archivo_permitido(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{int(datetime.now().timestamp())}_{filename}"
                upload_path = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))

                sql = """
                    UPDATE noticias 
                    SET titulo=%s, subtitulo=%s, cuerpo=%s, imagen_url=%s, epigrafe=%s, categoria=%s, es_destacada=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (titulo, subtitulo, cuerpo, filename, epigrafe, categoria, es_destacada, id_noticia))
            else:
                sql = """
                    UPDATE noticias 
                    SET titulo=%s, subtitulo=%s, cuerpo=%s, epigrafe=%s, categoria=%s, es_destacada=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (titulo, subtitulo, cuerpo, epigrafe, categoria, es_destacada, id_noticia))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al editar noticia: {e}")
    finally:
        conn.close()

    return redirect(url_for('noticias.admin_noticias'))

# Eliminar Noticia
@noticias_bp.route('/eliminar-noticia/<int:id>')
def eliminar(id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM noticias WHERE id = %s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al eliminar noticia: {e}")
    finally:
        conn.close()

    return redirect(url_for('noticias.admin_noticias'))