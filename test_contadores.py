"""
Script de prueba para verificar contadores
Ejecutar: python test_contadores.py
"""
import os

print("="*70)
print("VERIFICACIÓN DE CONTADORES")
print("="*70)

def contar_facturas_en_archivo(ruta_archivo):
    """Cuenta cuántas facturas hay en un archivo TXT"""
    try:
        with open(ruta_archivo, 'r', encoding='latin-1') as f:
            lineas = f.readlines()
        # Restar 1 por el encabezado
        return max(0, len(lineas) - 1)
    except Exception as e:
        print(f"Error leyendo {ruta_archivo}: {e}")
        return 0

print("\n1. Archivos en RECIBIDAS:")
total_rec = 0
if os.path.exists('facturas_xml/recibidas'):
    archivos = [f for f in os.listdir('facturas_xml/recibidas') if f.endswith('.txt')]
    for archivo in archivos:
        ruta = os.path.join('facturas_xml/recibidas', archivo)
        num = contar_facturas_en_archivo(ruta)
        total_rec += num
        print(f"   {archivo}: {num} facturas")
    print(f"   TOTAL: {total_rec} facturas")
else:
    print("   Carpeta no existe")

print("\n2. Archivos en EMITIDAS:")
total_emi = 0
if os.path.exists('facturas_xml/emitidas'):
    archivos = [f for f in os.listdir('facturas_xml/emitidas') if f.endswith('.txt')]
    for archivo in archivos:
        ruta = os.path.join('facturas_xml/emitidas', archivo)
        num = contar_facturas_en_archivo(ruta)
        total_emi += num
        print(f"   {archivo}: {num} facturas")
    print(f"   TOTAL: {total_emi} facturas")
else:
    print("   Carpeta no existe")

print("\n" + "="*70)
print(f"TOTAL GENERAL: {total_rec + total_emi} facturas")
print("="*70)
