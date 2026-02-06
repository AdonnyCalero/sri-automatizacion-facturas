import os
import glob
import pandas as pd
from datetime import datetime

# Buscar archivo TXT en múltiples ubicaciones
rutas_busqueda = [
    "facturas_xml/recibidas",
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Descargas"),
    "."
]

print("Buscando archivos TXT...")
archivos_encontrados = []

for ruta in rutas_busqueda:
    if os.path.exists(ruta):
        pattern = os.path.join(ruta, "*.txt")
        files = glob.glob(pattern)
        if files:
            print(f"  Encontrados en {ruta}: {len(files)}")
            archivos_encontrados.extend(files)

if not archivos_encontrados:
    print("No se encontraron archivos TXT")
    exit(1)

# Tomar el archivo más reciente
archivo_reciente = max(archivos_encontrados, key=os.path.getctime)
print(f"\nUsando archivo: {archivo_reciente}")
print(f"Tamaño: {os.path.getsize(archivo_reciente)} bytes")

# Intentar leer con diferentes encodings
encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
df = None

for encoding in encodings:
    try:
        # Intentar con punto y coma como separador (formato común del SRI)
        df = pd.read_csv(archivo_reciente, sep=';', encoding=encoding)
        if len(df.columns) > 1:
            print(f"\nArchivo leído correctamente con encoding: {encoding}")
            print(f"Columnas encontradas: {len(df.columns)}")
            print(f"Registros: {len(df)}")
            break
    except Exception as e:
        continue

if df is None:
    print("No se pudo leer el archivo")
    exit(1)

# Mostrar información
print("\n" + "="*60)
print("VISTA PREVIA DE DATOS")
print("="*60)
print(df.head())

# Generar Excel
output_file = "facturas_sri.xlsx"
df.to_excel(output_file, index=False, engine='openpyxl')

print("\n" + "="*60)
print("EXCEL GENERADO EXITOSAMENTE")
print("="*60)
print(f"Archivo: {output_file}")
print(f"Ubicacion: {os.path.abspath(output_file)}")
print(f"Registros exportados: {len(df)}")
