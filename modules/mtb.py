# modules/mtb.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import os
from db import get_connection  # Importa tu conexión de db.py

mtb_bp = Blueprint('mtb', __name__)

UPLOAD_FOLDER = 'static/uploads/participantes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@mtb_bp.route('/inscripcion-mtb')
def inscripcion_mtb():
    return render_template('inscripcion_mtb.html')

# API que consulta categorías en la BD usando tu conexión de db.py
@mtb_bp.route('/api/obtener-categorias', methods=['POST'])
def obtener_categorias():
    data = request.get_json() or {}
    fecha_nac_str = data.get('fecha_nacimiento')
    genero = data.get('genero')

    if not fecha_nac_str or not genero:
        return jsonify({'error': 'Faltan datos requeridos'}), 400

    # Calcular edad
    fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d')
    hoy = datetime.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

    conn = get_connection()
    categorias = []
    try:
        with conn.cursor() as cursor:
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
                  AND (c.genero = %s OR c.genero = 'UNISEX')
                ORDER BY c.grupo, c.nombre
            """
            cursor.execute(query, (edad, genero))
            categorias = cursor.fetchall()
    finally:
        conn.close()

    return jsonify({
        'edad': edad,
        'categorias': categorias
    })

# Guardar inscripción
@mtb_bp.route('/guardar-inscripcion', methods=['POST'])
def guardar_inscripcion():
    dni = request.form.get('dni', '').strip()
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Validar que el DNI no esté duplicado
            cursor.execute("SELECT id FROM participantes WHERE dni = %s", (dni,))
            existente = cursor.fetchone()

            if existente:
                flash('ERROR: El DNI ingresado ya se encuentra inscripto.', 'danger')
                return redirect(url_for('mtb.inscripcion_mtb'))

            # 2. Recibir los datos del formulario
            apellido = request.form.get('apellido')
            nombre = request.form.get('nombre')
            localidad = request.form.get('localidad')
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            genero = request.form.get('genero')
            categoria_id = request.form.get('categoria_id')
            circuito_id = request.form.get('circuito_id')
            
            # Guardar la foto subida
            foto = request.files.get('foto')
            filename = None
            if foto and foto.filename != '':
                filename = f"{dni}_{foto.filename}"
                foto.save(os.path.join(UPLOAD_FOLDER, filename))

            # Insertar en MySQL remota
            query = """
                INSERT INTO participantes 
                (apellido, nombre, dni, localidad, fecha_nacimiento, genero, foto, categoria_id, circuito_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (apellido, nombre, dni, localidad, fecha_nacimiento, genero, filename, categoria_id, circuito_id))
        
        conn.commit()  # Confirmamos el guardado ya que autocommit=False
    except Exception as e:
        conn.rollback()
        flash(f'Ocurrió un error al guardar: {e}', 'danger')
        return redirect(url_for('mtb.inscripcion_mtb'))
    finally:
        conn.close()

    flash('¡Inscripción realizada con éxito!', 'success')
    return redirect(url_for('mtb.inscripcion_mtb'))