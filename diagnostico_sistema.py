"""
Script de diagnóstico para verificar el proceso paso a paso
"""
import os
import sys

print("="*70)
print("DIAGNÓSTICO DEL SISTEMA SRI AUTOMATIZACIÓN")
print("="*70)

# 1. Verificar Python y dependencias
print("\n1. VERIFICANDO DEPENDENCIAS:")
try:
    import selenium
    print(f"   [OK] Selenium: {selenium.__version__}")
except:
    print("   [ERROR] Selenium no instalado")

try:
    import pandas
    print(f"   [OK] Pandas: {pandas.__version__}")
except:
    print("   [ERROR] Pandas no instalado")

try:
    import requests
    print(f"   [OK] Requests: {requests.__version__}")
except:
    print("   [ERROR] Requests no instalado")

# 2. Verificar estructura de carpetas
print("\n2. VERIFICANDO ESTRUCTURA:")
carpetas = [
    "facturas_xml/recibidas",
    "facturas_xml/emitidas", 
    "debug/html"
]

for carpeta in carpetas:
    if os.path.exists(carpeta):
        archivos = len([f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))])
        print(f"   [OK] {carpeta}: {archivos} archivos")
    else:
        print(f"   [ERROR] {carpeta}: No existe")
        os.makedirs(carpeta, exist_ok=True)
        print(f"     -> Carpeta creada")

# 3. Verificar archivos de configuración
print("\n3. VERIFICANDO CONFIGURACIÓN:")
if os.path.exists("config.py"):
    print("   [OK] config.py existe")
    try:
        from config import RUC, CLAVE, FECHA_DESDE, FECHA_HASTA
        print(f"   [OK] RUC configurado: {RUC}")
        print(f"   [OK] Fechas: {FECHA_DESDE} - {FECHA_HASTA}")
    except Exception as e:
        print(f"   [ERROR] Error en config.py: {e}")
else:
    print("   [ERROR] config.py no encontrado")

# 4. Verificar archivos HTML de debug
print("\n4. ARCHIVOS HTML DE DEBUG (últimos 5):")
if os.path.exists("debug/html"):
    archivos = sorted([f for f in os.listdir("debug/html") if f.endswith('.html')])
    for archivo in archivos[-5:]:
        print(f"   - {archivo}")
else:
    print("   No hay archivos de debug")

# 5. Verificar archivos descargados
print("\n5. ARCHIVOS DESCARGADOS:")
for tipo in ['recibidas', 'emitidas']:
    ruta = f"facturas_xml/{tipo}"
    if os.path.exists(ruta):
        archivos = [f for f in os.listdir(ruta) if f.endswith('.txt') or f.endswith('.xlsx')]
        print(f"   {tipo}: {len(archivos)} archivos")
        for arch in archivos[-3:]:  # Mostrar últimos 3
            print(f"     - {arch}")
    else:
        print(f"   {tipo}: Carpeta no existe")

# 6. Verificar archivos Excel generados
print("\n6. ARCHIVOS EXCEL:")
excels = [f for f in os.listdir('.') if f.endswith('.xlsx')]
if excels:
    for excel in excels:
        tamano = os.path.getsize(excel) / 1024  # KB
        print(f"   [OK] {excel} ({tamano:.1f} KB)")
else:
    print("   No se encontraron archivos Excel")

# 7. Instrucciones
print("\n" + "="*70)
print("RESULTADO DEL DIAGNÓSTICO:")
print("="*70)

if os.path.exists("facturas_xml/recibidas") and os.path.exists("facturas_xml/emitidas"):
    recibidas = [f for f in os.listdir("facturas_xml/recibidas") if f.endswith('.txt')]
    emitidas = [f for f in os.listdir("facturas_xml/emitidas") if f.endswith('.txt')]
    
    if len(recibidas) > 0 or len(emitidas) > 0:
        print("[EXITO] ¡Las facturas SÍ se descargaron!")
        print(f"   - Recibidas: {len(recibidas)} archivos")
        print(f"   - Emitidas: {len(emitidas)} archivos")
        print("\n[CARPETA] Ubicación:")
        print("   Recibidas: facturas_xml/recibidas/")
        print("   Emitidas: facturas_xml/emitidas/")
        
        excels = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        if excels:
            print(f"\n[EXCEL] Archivos Excel generados: {len(excels)}")
            for e in excels:
                print(f"   - {e}")
    else:
        print("[ADVERTENCIA]️ No se encontraron facturas descargadas")
        print("\nPosibles causas:")
        print("1. El proceso no llegó a la etapa de descarga")
        print("2. Hubo un error durante la ejecución")
        print("3. No hay facturas para la fecha configurada")
        print("\n[TIP] Recomendación:")
        print("   Ejecuta: python main.py")
        print("   Y observa si aparece algún error en la terminal")
else:
    print("[FALLO] Las carpetas de descarga no existen")

print("\n" + "="*70)
