# generar_excel_manual.py
# Script para generar Excel desde el archivo TXT existente

from generar_excel import generar_excel_desde_txt
import os

# Generar Excel desde el archivo TXT más reciente
print("Generando Excel desde archivo TXT existente...")
print("-" * 60)

exito = generar_excel_desde_txt()

if exito:
    print("\n" + "=" * 60)
    print("EXCEL GENERADO EXITOSAMENTE")
    print("=" * 60)
    
    # Verificar que el archivo existe
    if os.path.exists("facturas_sri.xlsx"):
        print(f"\nArchivo: facturas_sri.xlsx")
        print(f"Tamaño: {os.path.getsize('facturas_sri.xlsx')} bytes")
else:
    print("\n" + "=" * 60)
    print("NO SE PUDO GENERAR EL EXCEL")
    print("=" * 60)
    print("\nVerifica que exista un archivo .txt en la carpeta:")
    print("facturas_xml/recibidas/")

input("\nPresiona Enter para salir...")
