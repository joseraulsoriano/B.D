from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST', 'mysql_sistema_eventos'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'rootpassword'),
    'database': os.getenv('MYSQL_DATABASE', 'sistema_eventos')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

@app.route('/')
def home():
    return jsonify({"message": "Sistema de Eventos - API"})

@app.route('/test-connection')
def test_connection():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"status": "success", "message": "Conexión exitosa a la base de datos"})
    return jsonify({"status": "error", "message": "Error al conectar a la base de datos"}), 500

@app.route('/api/eventos')
def get_eventos():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, t.nombre as tematica,
                   COUNT(DISTINCT ep.id_participante) as total_participantes,
                   COUNT(DISTINCT ei.id_instructor) as total_instructores
            FROM Evento e
            LEFT JOIN Evento_Participante ep ON e.id_evento = ep.id_evento
            LEFT JOIN Evento_Instructor ei ON e.id_evento = ei.id_evento
            LEFT JOIN Tematica t ON e.id_tematica = t.id_tematica
            GROUP BY e.id_evento
            ORDER BY e.fecha_inicio DESC
        """)
        eventos = cursor.fetchall()
        
        # Convertir fechas a formato string para JSON
        for evento in eventos:
            if evento.get('fecha_inicio'):
                evento['fecha_inicio'] = evento['fecha_inicio'].isoformat()
            if evento.get('fecha_fin'):
                evento['fecha_fin'] = evento['fecha_fin'].isoformat()
        
        return jsonify({"status": "success", "data": eventos})
    except mysql.connector.Error as err:
        print(f"Error al obtener eventos: {err}")
        return jsonify({"status": "error", "message": "Error al obtener los eventos"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/participantes')
def get_participantes():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                p.id_participante,
                u.nombres,
                u.apellidoP,
                u.apellidoM,
                u.género,
                u.nacionalidad,
                u.correo,
                p.tipo,
                p.procedencia,
                COUNT(DISTINCT ep.id_evento) as eventos_inscritos
            FROM Participante p
            JOIN Usuario u ON p.id_usuario = u.id_usuario
            LEFT JOIN Evento_Participante ep ON p.id_participante = ep.id_participante
            GROUP BY p.id_participante
            ORDER BY u.apellidoP, u.apellidoM, u.nombres
        """)
        participantes = cursor.fetchall()
        return jsonify(participantes)
    except mysql.connector.Error as err:
        print(f"Error al obtener participantes: {err}")
        return jsonify({"status": "error", "message": "Error al obtener los participantes"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Total de participantes
        cursor.execute("SELECT COUNT(*) as total FROM Participante")
        total_participantes = cursor.fetchone()['total']

        # Eventos activos
        cursor.execute("SELECT COUNT(*) as total FROM Evento WHERE estado = 'Activo'")
        eventos_activos = cursor.fetchone()['total']

        # Total de instructores
        cursor.execute("SELECT COUNT(DISTINCT id_instructor) as total FROM Evento_Instructor")
        total_instructores = cursor.fetchone()['total']

        # Total de organizaciones
        cursor.execute("SELECT COUNT(*) as total FROM Organizacion")
        total_organizaciones = cursor.fetchone()['total']

        return jsonify({
            "total_participantes": total_participantes,
            "eventos_activos": eventos_activos,
            "total_instructores": total_instructores,
            "total_organizaciones": total_organizaciones
        })
    except mysql.connector.Error as err:
        print(f"Error al obtener estadísticas: {err}")
        return jsonify({"status": "error", "message": "Error al obtener las estadísticas"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/genero')
def get_genero_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                ROUND(COUNT(CASE WHEN u.género = 'Masculino' THEN 1 END) * 100.0 / COUNT(*), 1) as hombres,
                ROUND(COUNT(CASE WHEN u.género = 'Femenino' THEN 1 END) * 100.0 / COUNT(*), 1) as mujeres
            FROM Participante p
            JOIN Usuario u ON p.id_usuario = u.id_usuario
        """)
        result = cursor.fetchone()
        return jsonify(result)
    except mysql.connector.Error as err:
        print(f"Error al obtener estadísticas de género: {err}")
        return jsonify({"status": "error", "message": "Error al obtener las estadísticas de género"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/modalidades')
def get_modalidades_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                modalidad,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Evento), 1) as porcentaje
            FROM Evento
            GROUP BY modalidad
        """)
        modalidades = cursor.fetchall()
        return jsonify(modalidades)
    except mysql.connector.Error as err:
        print(f"Error al obtener estadísticas de modalidades: {err}")
        return jsonify({"status": "error", "message": "Error al obtener las estadísticas de modalidades"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/eventos/<int:id_evento>')
def get_evento_detalle(id_evento):
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Obtener detalles del evento incluyendo finanzas
        cursor.execute("""
            SELECT 
                e.*,
                t.nombre as tematica_nombre,
                COUNT(DISTINCT ep.id_participante) as total_participantes,
                COUNT(DISTINCT ei.id_instructor) as total_instructores,
                GROUP_CONCAT(DISTINCT o.nombre) as organizaciones,
                GROUP_CONCAT(DISTINCT ods.id_ods) as ods_ids,
                GROUP_CONCAT(DISTINCT ods.nombre) as objetivos_desarrollo,
                f.porcentaje_ingreso,
                f.fee_aportado
            FROM Evento e
            LEFT JOIN Evento_Participante ep ON e.id_evento = ep.id_evento
            LEFT JOIN Evento_Instructor ei ON e.id_evento = ei.id_evento
            LEFT JOIN Tematica t ON e.id_tematica = t.id_tematica
            LEFT JOIN Evento_Organizacion eo ON e.id_evento = eo.id_evento
            LEFT JOIN Organizacion o ON eo.id_organizacion = o.id_organizacion
            LEFT JOIN Evento_ODS eods ON e.id_evento = eods.id_evento
            LEFT JOIN ODS ods ON eods.id_ods = ods.id_ods
            LEFT JOIN FinanzaEvento f ON e.id_evento = f.id_evento
            WHERE e.id_evento = %s
            GROUP BY e.id_evento
        """, (id_evento,))
        evento = cursor.fetchone()
        
        if not evento:
            return jsonify({"status": "error", "message": "Evento no encontrado"}), 404

        # Obtener lista completa de ODS con estado
        cursor.execute("""
            SELECT 
                ods.id_ods,
                ods.nombre,
                CASE WHEN eods.id_evento IS NOT NULL THEN 1 ELSE 0 END as seleccionado
            FROM ODS ods
            LEFT JOIN Evento_ODS eods ON ods.id_ods = eods.id_ods AND eods.id_evento = %s
            ORDER BY ods.id_ods
        """, (id_evento,))
        ods_completo = cursor.fetchall()

        # Obtener participantes del evento
        cursor.execute("""
            SELECT 
                p.id_participante,
                u.nombres,
                u.apellidoP,
                u.apellidoM,
                u.género,
                u.nacionalidad,
                p.tipo,
                p.procedencia
            FROM Evento_Participante ep
            JOIN Participante p ON ep.id_participante = p.id_participante
            JOIN Usuario u ON p.id_usuario = u.id_usuario
            WHERE ep.id_evento = %s
        """, (id_evento,))
        participantes = cursor.fetchall()
        
        # Obtener instructores del evento
        cursor.execute("""
            SELECT 
                i.id_instructor,
                u.nombres,
                u.apellidoP,
                u.apellidoM,
                u.género,
                u.nacionalidad,
                ei.pagoInstructor
            FROM Evento_Instructor ei
            JOIN Instructor i ON ei.id_instructor = i.id_instructor
            JOIN Usuario u ON i.id_usuario = u.id_usuario
            WHERE ei.id_evento = %s
        """, (id_evento,))
        instructores = cursor.fetchall()

        # Formatear fechas para JSON
        if evento.get('fecha_inicio'):
            evento['fecha_inicio'] = evento['fecha_inicio'].isoformat()
        if evento.get('fecha_fin'):
            evento['fecha_fin'] = evento['fecha_fin'].isoformat()

        return jsonify({
            "status": "success",
            "data": {
                "evento": evento,
                "participantes": participantes,
                "instructores": instructores,
                "ods_completo": ods_completo
            }
        })
    except mysql.connector.Error as err:
        print(f"Error al obtener detalles del evento: {err}")
        return jsonify({"status": "error", "message": "Error al obtener los detalles del evento"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/estadisticas/participantes')
def get_estadisticas_participantes():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Distribución por nacionalidad
        cursor.execute("""
            SELECT 
                ROUND(COUNT(CASE WHEN u.nacionalidad = 'Mexicana' THEN 1 END) * 100.0 / COUNT(*), 1) as nacionales,
                ROUND(COUNT(CASE WHEN u.nacionalidad != 'Mexicana' THEN 1 END) * 100.0 / COUNT(*), 1) as extranjeros
            FROM Participante p
            JOIN Usuario u ON p.id_usuario = u.id_usuario
        """)
        nacionalidad = cursor.fetchone()

        # Distribución por edad
        cursor.execute("""
            SELECT 
                ROUND(COUNT(CASE WHEN TIMESTAMPDIFF(YEAR, u.fecha_nac, CURDATE()) < 18 THEN 1 END) * 100.0 / COUNT(*), 1) as menores_18,
                ROUND(COUNT(CASE WHEN TIMESTAMPDIFF(YEAR, u.fecha_nac, CURDATE()) BETWEEN 18 AND 30 THEN 1 END) * 100.0 / COUNT(*), 1) as entre_18_30,
                ROUND(COUNT(CASE WHEN TIMESTAMPDIFF(YEAR, u.fecha_nac, CURDATE()) BETWEEN 31 AND 50 THEN 1 END) * 100.0 / COUNT(*), 1) as entre_31_50,
                ROUND(COUNT(CASE WHEN TIMESTAMPDIFF(YEAR, u.fecha_nac, CURDATE()) > 50 THEN 1 END) * 100.0 / COUNT(*), 1) as mayores_50
            FROM Participante p
            JOIN Usuario u ON p.id_usuario = u.id_usuario
        """)
        edad = cursor.fetchone()

        # Distribución por procedencia
        cursor.execute("""
            SELECT procedencia, COUNT(*) as total,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Participante), 1) as porcentaje
            FROM Participante
            GROUP BY procedencia
        """)
        procedencia = cursor.fetchall()

        return jsonify({
            "nacionalidad": nacionalidad,
            "edad": edad,
            "procedencia": procedencia
        })
    except mysql.connector.Error as err:
        print(f"Error al obtener estadísticas de participantes: {err}")
        return jsonify({"status": "error", "message": "Error al obtener las estadísticas de participantes"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/estadisticas/organizaciones')
def get_estadisticas_organizaciones():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Distribución por tipo de organización
        cursor.execute("""
            SELECT tipo, COUNT(*) as total,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Organizacion), 1) as porcentaje
            FROM Organizacion
            GROUP BY tipo
        """)
        tipos = cursor.fetchall()

        return jsonify({
            "tipos": tipos
        })
    except mysql.connector.Error as err:
        print(f"Error al obtener estadísticas de organizaciones: {err}")
        return jsonify({"status": "error", "message": "Error al obtener las estadísticas de organizaciones"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/estadisticas/tematicas')
def get_estadisticas_tematicas():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Top 10 temáticas más demandadas
        cursor.execute("""
            SELECT t.nombre, COUNT(e.id_evento) as total_eventos,
                   ROUND(COUNT(e.id_evento) * 100.0 / (SELECT COUNT(*) FROM Evento), 1) as porcentaje
            FROM Tematica t
            LEFT JOIN Evento e ON t.id_tematica = e.id_tematica
            GROUP BY t.id_tematica
            ORDER BY total_eventos DESC
            LIMIT 10
        """)
        tematicas = cursor.fetchall()

        return jsonify({
            "tematicas": tematicas
        })
    except mysql.connector.Error as err:
        print(f"Error al obtener estadísticas de temáticas: {err}")
        return jsonify({"status": "error", "message": "Error al obtener las estadísticas de temáticas"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 