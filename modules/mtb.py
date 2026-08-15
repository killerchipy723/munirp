# modules/mtb.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime
import os
from db import get_connection  # Importa tu conexión de db.py

mtb_bp = Blueprint('mtb', __name__)

UPLOAD_FOLDER = 'static/uploads/participantes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@mtb_bp.route('/inscripcion-mtb')
def inscripcion_mtb():
    return render_template('inscripcion_mtb.html')

# API que consulta categorías en la BD según edad y género
@mtb_bp.route('/api/obtener-categorias', methods=['POST'])
def obtener_categorias():
    data = request.get_json() or {}
    fecha_nac_str = data.get('fecha_nacimiento')
    genero = data.get('genero')

    if not fecha_nac_str or not genero:
        return jsonify({'error': 'Faltan datos requeridos'}), 400

    try:
        # Calcular edad
        fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d')
        hoy = datetime.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400

    conn = get_connection()
    categorias = []
    try:
        with conn.cursor() as cursor:
            # Usamos UPPER() en género para evitar fallos por minúsculas/mayúsculas
            query = """
                SELECT 
                    c.id AS categoria_id,
                    c.grupo,
                    c.nombre AS categoria_nombre,
                    cir.id AS circuito_id,
                    cir.nombre AS circuito_nombre,
                    cir.kilometros
                FROM categorias c
                JOIN circuitos cir ON c.circuito_id = cir.id
                WHERE %s BETWEEN c.edad_min AND c.edad_max
                  AND (UPPER(c.genero) = UPPER(%s) OR UPPER(c.genero) = 'UNISEX')
                ORDER BY c.grupo, c.nombre
            """
            cursor.execute(query, (edad, genero))
            categorias = cursor.fetchall()
    except Exception as e:
        print(f"ERROR EN OBTENER CATEGORIAS: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({
        'edad': edad,
        'categorias': categorias
    })

# Guardar inscripción y preparar datos para el comprobante
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime
import os
from db import get_connection  # Usa la versión con PooledDB

mtb_bp = Blueprint('mtb', __name__)

UPLOAD_FOLDER = 'static/uploads/participantes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@mtb_bp.route('/inscripcion-mtb')
def inscripcion_mtb():
    return render_template('inscripcion_mtb.html')

@mtb_bp.route('/api/obtener-categorias', methods=['POST'])
def obtener_categorias():
    data = request.get_json() or {}
    fecha_nac_str = data.get('fecha_nacimiento')
    genero = data.get('genero')

    if not fecha_nac_str or not genero:
        return jsonify({'error': 'Faltan datos'}), 400

    try:
        fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d')
        hoy = datetime.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    except:
        return jsonify({'error': 'Fecha inválida'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT c.id AS categoria_id, c.grupo, c.nombre AS categoria_nombre, 
                       cir.id AS circuito_id, cir.nombre AS circuito_nombre, cir.kilometros
                FROM categorias c
                JOIN circuitos cir ON c.circuito_id = cir.id
                WHERE %s BETWEEN c.edad_min AND c.edad_max
                AND (UPPER(c.genero) = UPPER(%s) OR UPPER(c.genero) = 'UNISEX')
            """
            cursor.execute(query, (edad, genero))
            categorias = cursor.fetchall()
    finally:
        conn.close() # Devuelve al Pool

    return jsonify({'categorias': categorias})

@mtb_bp.route('/guardar-inscripcion', methods=['POST'])
def guardar_inscripcion():
    dni = request.form.get('dni', '').strip()
    apellido = request.form.get('apellido', '').strip().upper()
    nombre = request.form.get('nombre', '').strip().upper()
    localidad = request.form.get('localidad', '').strip().upper()
    fecha_nac = request.form.get('fecha_nacimiento')
    genero = request.form.get('genero', '').strip().upper()
    categoria_id = request.form.get('categoria_id')
    circuito_id = request.form.get('circuito_id')
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Validar duplicado
            cursor.execute("SELECT id FROM participantes WHERE dni = %s", (dni,))
            if cursor.fetchone():
                flash('ERROR: El DNI ya está inscripto.', 'danger')
                return redirect(url_for('mtb.inscripcion_mtb'))

            # 2. Guardar foto
            foto = request.files.get('foto')
            filename = None
            if foto and foto.filename:
                # Limpiamos el nombre del archivo para evitar caracteres raros
                clean_name = "".join([c for c in foto.filename if c.isalnum() or c in ('.', '_')])
                filename = f"{dni}_{clean_name}"
                foto.save(os.path.join(UPLOAD_FOLDER, filename))

            # 3. Insertar
            query = """INSERT INTO participantes (apellido, nombre, dni, localidad, fecha_nacimiento, genero, foto, categoria_id, circuito_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (apellido, nombre, dni, localidad, fecha_nac, genero, filename, categoria_id, circuito_id))
            inscrito_id = cursor.lastrowid

            # 4. Sesión (Feedback usuario)
            session['inscrito_id'] = str(inscrito_id).zfill(3)
            session['inscrito_nombre'] = f"{nombre} {apellido}"
            
    except Exception as e:
        print(f"ERROR: {e}")
        flash('Error al procesar inscripción. Intente de nuevo.', 'danger')
        return redirect(url_for('mtb.inscripcion_mtb'))
    finally:
        conn.close() # Fundamental para no agotar conexiones

    flash('¡Inscripción exitosa!', 'success')
    return redirect(url_for('mtb.inscripcion_mtb'))