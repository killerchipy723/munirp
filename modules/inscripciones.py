# modules/inscripciones.py
from flask import Blueprint, render_template, request, send_file
import pandas as pd
import io
from db import get_connection

inscripciones_bp = Blueprint('inscripciones', __name__)

@inscripciones_bp.route('/admin/inscripciones')
def listar_inscripciones():
    conn = get_connection()
    inscripciones = []
    categorias = []
    circuitos = []
    
    # Capturar filtros de la URL (si existen)
    filtro_categoria = request.args.get('categoria_id', '')
    filtro_circuito = request.args.get('circuito_id', '')
    filtro_busqueda = request.args.get('busqueda', '').strip()

    try:
        with conn.cursor() as cursor:
            # 1. Obtener listas para los selectores de filtro
            cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
            categorias = cursor.fetchall()

            cursor.execute("SELECT id, nombre FROM circuitos ORDER BY nombre")
            circuitos = cursor.fetchall()

            # 2. Armar la consulta principal con filtros dinámicos
            query = """
                SELECT 
                    p.id, p.apellido, p.nombre, p.dni, p.localidad, 
                    p.fecha_nacimiento, p.genero, p.foto,
                    c.nombre AS categoria_nombre, c.grupo,
                    cir.nombre AS circuito_nombre, cir.kilometros
                FROM participantes p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN circuitos cir ON p.circuito_id = cir.id
                WHERE 1=1
            """
            params = []

            if filtro_categoria:
                query += " AND p.categoria_id = %s"
                params.append(filtro_categoria)
            
            if filtro_circuito:
                query += " AND p.circuito_id = %s"
                params.append(filtro_circuito)

            if filtro_busqueda:
                query += " AND (p.dni LIKE %s OR p.apellido LIKE %s OR p.nombre LIKE %s OR p.localidad LIKE %s)"
                busq_param = f"%{filtro_busqueda}%"
                params.extend([busq_param, busq_param, busq_param, busq_param])

            query += " ORDER BY p.id DESC"
            
            cursor.execute(query, tuple(params))
            inscripciones = cursor.fetchall()
    finally:
        conn.close()

    return render_template(
        'admin_inscripciones.html',
        inscripciones=inscripciones,
        categorias=categorias,
        circuitos=circuitos,
        filtro_categoria=filtro_categoria,
        filtro_circuito=filtro_circuito,
        filtro_busqueda=filtro_busqueda
    )

# Ruta para exportar a Excel profesional
@inscripciones_bp.route('/admin/inscripciones/excel')
def exportar_excel():
    conn = get_connection()
    try:
        query = """
            SELECT 
                p.dni AS DNI,
                p.apellido AS Apellido,
                p.nombre AS Nombre,
                p.localidad AS Localidad,
                p.fecha_nacimiento AS 'Fecha de Nacimiento',
                p.genero AS Género,
                c.nombre AS Categoría,
                c.grupo AS Grupo,
                cir.nombre AS Circuito,
                cir.kilometros AS 'Kilómetros'
            FROM participantes p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN circuitos cir ON p.circuito_id = cir.id
            ORDER BY p.apellido, p.nombre
        """
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            datos = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
        
        df = pd.DataFrame(datos, columns=columnas)

        # --- TRANSFORMACIÓN A MAYÚSCULAS ---
        # Convertimos las columnas específicas a mayúsculas
        columnas_a_mayusculas = ['Apellido', 'Nombre', 'Localidad']
        for col in columnas_a_mayusculas:
            if col in df.columns:
                df[col] = df[col].astype(str).str.upper()
        # ----------------------------------
        
    finally:
        conn.close()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inscriptos MTB')
        
        # Ajustar ancho de columnas profesionalmente
        worksheet = writer.sheets['Inscriptos MTB']
        for idx, col in enumerate(df.columns):
            # Calculamos el ancho basado en el contenido más largo
            series = df[col].astype(str)
            max_len = max(series.map(len).max(), len(col)) + 4
            worksheet.column_dimensions[chr(65 + idx)].width = max_len
    
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Inscripciones_MTB.xlsx'
    )