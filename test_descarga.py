"""
Script de prueba para verificar descargas
Ejecutar: python test_descarga.py
"""
from descargar_facturas import (
    descargar_reporte_txt_requests,
    descargar_reporte_txt
)
import os

print("="*60)
print("PRUEBA DE DESCARGA")
print("="*60)

# Verificar carpetas
print("\n📁 Verificando carpetas...")
print(f"  Recibidas: {os.path.exists('facturas_xml/recibidas')}")
print(f"  Emitidas: {os.path.exists('facturas_xml/emitidas')}")

# Listar archivos actuales
print("\n📄 Archivos en recibidas:")
if os.path.exists('facturas_xml/recibidas'):
    files = os.listdir('facturas_xml/recibidas')
    for f in files:
        print(f"  - {f}")
else:
    print("  (Carpeta no existe)")

print("\n📄 Archivos en emitidas:")
if os.path.exists('facturas_xml/emitidas'):
    files = os.listdir('facturas_xml/emitidas')
    for f in files:
        print(f"  - {f}")
else:
    print("  (Carpeta no existe)")

print("\n✅ Prueba completada")
print("\nSi no ves archivos, el proceso no se ejecutó correctamente.")
print("Ejecuta main.py manualmente para ver los errores:")
print("  python main.py")
