"""
Backend API para SRI Automatización
Conecta el frontend con el script Python de automatización
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import subprocess
import json
import os
import time
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)  # Permitir CORS para que el frontend pueda comunicarse

# Variables globales para el estado del proceso
proceso_estado = {
    'activo': False,
    'inicio': None,
    'fin': None,
    'logs': [],
    'progreso': 0,
    'archivos_recibidos': 0,
    'archivos_emitidos': 0,
    'error': None
}

# Ruta al script principal
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'main.py')

def agregar_log(mensaje):
    """Agrega un mensaje al log"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    proceso_estado['logs'].append({
        'timestamp': timestamp,
        'mensaje': mensaje
    })
    print(f"[{timestamp}] {mensaje}")

@app.route('/api/estado', methods=['GET'])
def obtener_estado():
    """Retorna el estado actual del proceso"""
    return jsonify({
        'activo': proceso_estado['activo'],
        'inicio': proceso_estado['inicio'],
        'fin': proceso_estado['fin'],
        'progreso': proceso_estado['progreso'],
        'archivos_recibidos': proceso_estado['archivos_recibidos'],
        'archivos_emitidos': proceso_estado['archivos_emitidos'],
        'error': proceso_estado['error'],
        'logs_count': len(proceso_estado['logs'])
    })

@app.route('/api/logs', methods=['GET'])
def obtener_logs():
    """Retorna los logs del proceso"""
    desde = request.args.get('desde', 0, type=int)
    logs = proceso_estado['logs'][desde:]
    return jsonify({
        'logs': logs,
        'total': len(proceso_estado['logs'])
    })

@app.route('/api/iniciar', methods=['POST'])
def iniciar_proceso():
    """Inicia el proceso de automatización"""
    global proceso_estado
    
    if proceso_estado['activo']:
        return jsonify({
            'success': False,
            'message': 'Ya hay un proceso en ejecución'
        }), 400
    
    # Reiniciar estado
    proceso_estado = {
        'activo': True,
        'inicio': datetime.now().isoformat(),
        'fin': None,
        'logs': [],
        'progreso': 0,
        'archivos_recibidos': 0,
        'archivos_emitidos': 0,
        'error': None
    }
    
    # Obtener configuración del request
    data = request.get_json() or {}
    fecha_desde = data.get('fecha_desde', '07/02/2026')
    fecha_hasta = data.get('fecha_hasta', '07/02/2026')
    ruc = data.get('ruc', '1713166765001')
    clave = data.get('clave', '')
    
    agregar_log('Iniciando proceso de automatización...')
    agregar_log(f'Configuración: RUC={ruc}, Fecha={fecha_desde}')
    
    # Iniciar proceso en un thread separado
    thread = threading.Thread(
        target=ejecutar_script,
        args=(fecha_desde, fecha_hasta, ruc, clave)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Proceso iniciado correctamente'
    })

@app.route('/api/detener', methods=['POST'])
def detener_proceso():
    """Detiene el proceso actual"""
    if not proceso_estado['activo']:
        return jsonify({
            'success': False,
            'message': 'No hay proceso en ejecución'
        }), 400
    
    proceso_estado['activo'] = False
    proceso_estado['fin'] = datetime.now().isoformat()
    agregar_log('Proceso detenido por el usuario')
    
    return jsonify({
        'success': True,
        'message': 'Proceso detenido'
    })

@app.route('/api/archivos', methods=['GET'])
def listar_archivos():
    """Lista los archivos descargados y cuenta facturas reales"""
    recibidas_path = 'facturas_xml/recibidas'
    emitidas_path = 'facturas_xml/emitidas'
    
    archivos_recibidos = []
    archivos_emitidos = []
    total_facturas_recibidas = 0
    total_facturas_emitidas = 0
    
    def contar_facturas_en_archivo(ruta_archivo):
        """Cuenta cuántas facturas hay en un archivo TXT"""
        try:
            with open(ruta_archivo, 'r', encoding='latin-1') as f:
                lineas = f.readlines()
            # Restar 1 por el encabezado
            return max(0, len(lineas) - 1)
        except:
            return 0
    
    if os.path.exists(recibidas_path):
        for f in os.listdir(recibidas_path):
            if f.endswith('.txt'):
                ruta = os.path.join(recibidas_path, f)
                num_facturas = contar_facturas_en_archivo(ruta)
                total_facturas_recibidas += num_facturas
                archivos_recibidos.append({
                    'nombre': f,
                    'tipo': 'recibido',
                    'tamaño': os.path.getsize(ruta),
                    'facturas': num_facturas,
                    'fecha': datetime.fromtimestamp(
                        os.path.getmtime(ruta)
                    ).isoformat()
                })
    
    if os.path.exists(emitidas_path):
        for f in os.listdir(emitidas_path):
            if f.endswith('.txt'):
                ruta = os.path.join(emitidas_path, f)
                num_facturas = contar_facturas_en_archivo(ruta)
                total_facturas_emitidas += num_facturas
                archivos_emitidos.append({
                    'nombre': f,
                    'tipo': 'emitido',
                    'tamaño': os.path.getsize(ruta),
                    'facturas': num_facturas,
                    'fecha': datetime.fromtimestamp(
                        os.path.getmtime(ruta)
                    ).isoformat()
                })
    
    return jsonify({
        'recibidos': archivos_recibidos,
        'emitidos': archivos_emitidos,
        'total_recibidos': len(archivos_recibidos),
        'total_emitidos': len(archivos_emitidos),
        'total_facturas_recibidas': total_facturas_recibidas,
        'total_facturas_emitidas': total_facturas_emitidas
    })

@app.route('/api/descargar/<tipo>/<nombre>', methods=['GET'])
def descargar_archivo(tipo, nombre):
    """Permite descargar un archivo específico"""
    if tipo == 'recibido':
        path = os.path.join('facturas_xml/recibidas', nombre)
    elif tipo == 'emitido':
        path = os.path.join('facturas_xml/emitidas', nombre)
    else:
        return jsonify({'error': 'Tipo inválido'}), 400
    
    if not os.path.exists(path):
        return jsonify({'error': 'Archivo no encontrado'}), 404
    
    return send_file(path, as_attachment=True)

def ejecutar_script(fecha_desde, fecha_hasta, ruc, clave):
    """Ejecuta el script Python principal mostrando el navegador"""
    global proceso_estado
    
    try:
        agregar_log('Iniciando proceso...')
        agregar_log('IMPORTANTE: No cierres esta ventana ni el navegador Chrome')
        agregar_log('El proceso se ejecutara en una ventana separada')
        proceso_estado['progreso'] = 5
        
        # Actualizar config.py con los valores recibidos
        actualizar_config(fecha_desde, fecha_hasta, ruc, clave)
        
        agregar_log('Abriendo navegador Chrome...')
        proceso_estado['progreso'] = 10
        
        # Ejecutar el script SIN capturar output (para que se muestre todo en consola)
        # Usamos shell=True en Windows para que se abra la ventana de consola
        import platform
        if platform.system() == 'Windows':
            # En Windows, usar start para abrir en ventana nueva
            proceso = subprocess.Popen(
                ['start', 'cmd', '/k', 'python', SCRIPT_PATH],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # En Linux/Mac
            proceso = subprocess.Popen(
                ['python', SCRIPT_PATH],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        agregar_log('Proceso iniciado en ventana separada')
        agregar_log('Espera a que Chrome se abra y complete la descarga...')
        proceso_estado['progreso'] = 20
        
        # Esperar un poco y luego verificar si hay archivos nuevos
        import time
        time.sleep(10)  # Esperar 10 segundos inicial
        
        # Monitorear la creación de archivos
        archivos_iniciales_rec = set()
        archivos_iniciales_emi = set()
        
        if os.path.exists('facturas_xml/recibidas'):
            archivos_iniciales_rec = set(os.listdir('facturas_xml/recibidas'))
        if os.path.exists('facturas_xml/emitidas'):
            archivos_iniciales_emi = set(os.listdir('facturas_xml/emitidas'))
        
        # Esperar hasta 5 minutos revisando cada 5 segundos
        tiempo_maximo = 300  # 5 minutos
        tiempo_transcurrido = 10
        
        while tiempo_transcurrido < tiempo_maximo and proceso_estado['activo']:
            time.sleep(5)
            tiempo_transcurrido += 5
            
            # Verificar si hay archivos nuevos
            archivos_actuales_rec = set()
            archivos_actuales_emi = set()
            
            if os.path.exists('facturas_xml/recibidas'):
                archivos_actuales_rec = set(os.listdir('facturas_xml/recibidas'))
            if os.path.exists('facturas_xml/emitidas'):
                archivos_actuales_emi = set(os.listdir('facturas_xml/emitidas'))
            
            nuevos_rec = len(archivos_actuales_rec - archivos_iniciales_rec)
            nuevos_emi = len(archivos_actuales_emi - archivos_iniciales_emi)
            
            if nuevos_rec > 0:
                proceso_estado['archivos_recibidos'] = nuevos_rec
                agregar_log(f'Descargadas {nuevos_rec} facturas recibidas')
                proceso_estado['progreso'] = min(50, 20 + (nuevos_rec * 5))
            
            if nuevos_emi > 0:
                proceso_estado['archivos_emitidos'] = nuevos_emi
                agregar_log(f'Descargadas {nuevos_emi} facturas emitidas')
                proceso_estado['progreso'] = min(90, 50 + (nuevos_emi * 10))
            
            # Verificar si se generaron Excel
            if os.path.exists('facturas_recibidas.xlsx') or os.path.exists('facturas_emitidas.xlsx'):
                proceso_estado['progreso'] = 100
                agregar_log('Archivos Excel generados')
                break
        
        agregar_log('Proceso finalizado')
        proceso_estado['progreso'] = 100
        
        # Verificar resultado final
        if proceso_estado['archivos_recibidos'] > 0 or proceso_estado['archivos_emitidos'] > 0:
            agregar_log('Descarga completada exitosamente')
        else:
            agregar_log('No se detectaron nuevas descargas')
            agregar_log('Verifica la ventana de Chrome para mas detalles')
        
    except Exception as e:
        agregar_log(f'Error: {str(e)}')
        proceso_estado['error'] = str(e)
    
    finally:
        proceso_estado['activo'] = False
        proceso_estado['fin'] = datetime.now().isoformat()

def actualizar_config(fecha_desde, fecha_hasta, ruc, clave):
    """Actualiza el archivo config.py con los nuevos valores"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.py')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Actualizar RUC
        import re
        contenido = re.sub(r'RUC = "[^"]*"', f'RUC = "{ruc}"', contenido)
        
        # Actualizar CLAVE
        contenido = re.sub(r'CLAVE = "[^"]*"', f'CLAVE = "{clave}"', contenido)
        
        # Actualizar Fechas
        contenido = re.sub(r'FECHA_DESDE = "[^"]*"', f'FECHA_DESDE = "{fecha_desde}"', contenido)
        contenido = re.sub(r'FECHA_HASTA = "[^"]*"', f'FECHA_HASTA = "{fecha_hasta}"', contenido)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        agregar_log('Configuración actualizada (RUC, fechas)')
    except Exception as e:
        agregar_log(f'Error actualizando configuración: {e}')

@app.route('/', methods=['GET'])
def index():
    """Endpoint raíz"""
    return jsonify({
        'message': 'API SRI Automatización',
        'version': '2.0',
        'endpoints': [
            '/api/estado - Obtener estado del proceso',
            '/api/logs - Obtener logs',
            '/api/iniciar - Iniciar proceso',
            '/api/detener - Detener proceso',
            '/api/archivos - Listar archivos descargados',
            '/api/descargar/<tipo>/<nombre> - Descargar archivo'
        ]
    })

if __name__ == '__main__':
    print('[INICIO] API SRI Automatizacion...')
    print('[INFO] Servidor disponible en: http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
