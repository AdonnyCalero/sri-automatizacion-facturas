"""
Script de prueba para verificar la configuración
Ejecutar: python test_sistema.py
"""
import os
import sys

print("="*70)
print("PRUEBA DEL SISTEMA SRI AUTOMATIZACIÓN")
print("="*70)

# Verificar archivos necesarios
archivos_necesarios = [
    'main.py',
    'api.py',
    'config.py',
    'index.html',
    'package.json'
]

print("\n1. Verificando archivos:")
faltantes = []
for archivo in archivos_necesarios:
    if os.path.exists(archivo):
        print(f"   [OK] {archivo}")
    else:
        print(f"   [X] {archivo} - NO ENCONTRADO")
        faltantes.append(archivo)

if faltantes:
    print(f"\n   ERROR: Faltan archivos: {', '.join(faltantes)}")
    sys.exit(1)

# Verificar configuración
print("\n2. Verificando configuración:")
try:
    from config import RUC, CLAVE, FECHA_DESDE, FECHA_HASTA
    print(f"   [OK] RUC configurado: {RUC}")
    print(f"   [OK] Fechas: {FECHA_DESDE} - {FECHA_HASTA}")
except Exception as e:
    print(f"   [X] Error en configuración: {e}")
    sys.exit(1)

# Verificar carpetas
print("\n3. Verificando carpetas:")
carpetas = ['facturas_xml/recibidas', 'facturas_xml/emitidas', 'debug/html']
for carpeta in carpetas:
    if os.path.exists(carpeta):
        archivos = len([f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))])
        print(f"   [OK] {carpeta}: {archivos} archivos")
    else:
        os.makedirs(carpeta, exist_ok=True)
        print(f"   [OK] {carpeta}: creada")

# Verificar archivos actuales
print("\n4. Archivos actuales:")
for tipo in ['recibidas', 'emitidas']:
    ruta = f"facturas_xml/{tipo}"
    if os.path.exists(ruta):
        archivos = [f for f in os.listdir(ruta) if f.endswith('.txt')]
        print(f"   {tipo}: {len(archivos)} archivos TXT")

print("\n" + "="*70)
print("[OK] Sistema listo para usar!")
print("="*70)
print("\nPara iniciar con interfaz visual:")
print("  1. Abre TERMINAL 1 y ejecuta: python api.py")
print("  2. Abre TERMINAL 2 y ejecuta: npm run dev")
print("  3. Abre navegador en: http://localhost:3001")
print("\nO ejecuta directamente:")
print("  - doble clic en: ejecutar.bat")
print("  - o: python main.py")
print("="*70)
