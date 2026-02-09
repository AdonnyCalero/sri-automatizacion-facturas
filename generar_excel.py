# generar_excel.py

import os
import pandas as pd
from procesar_xml import leer_factura_xml
from config import RECIBIDAS_PATH, EMITIDAS_PATH
import glob

def cargar_xmls(ruta, tipo):
    registros = []

    for archivo in os.listdir(ruta):
        if archivo.endswith(".xml"):
            datos = leer_factura_xml(os.path.join(ruta, archivo))
            datos["tipo"] = tipo
            registros.append(datos)

    return registros

def leer_reporte_txt(ruta_archivo=None):
    """
    Lee el archivo TXT del reporte descargado del SRI y retorna un DataFrame
    """
    # Si no se especifica ruta, buscar el archivo TXT ms reciente
    if ruta_archivo is None:
        # Buscar en ambas carpetas: recibidas y emitidas
        archivos_txt = []
        
        # Buscar en recibidas
        if os.path.exists(RECIBIDAS_PATH):
            archivos_txt.extend(glob.glob(os.path.join(RECIBIDAS_PATH, "*.txt")))
        
        # Buscar en emitidas
        if os.path.exists(EMITIDAS_PATH):
            archivos_txt.extend(glob.glob(os.path.join(EMITIDAS_PATH, "*.txt")))
        
        if not archivos_txt:
            print(f" No se encontraron archivos TXT en {RECIBIDAS_PATH} ni {EMITIDAS_PATH}")
            return None
        
        # Tomar el archivo ms reciente
        ruta_archivo = max(archivos_txt, key=os.path.getctime)
        print(f" Archivo encontrado: {os.path.basename(ruta_archivo)}")
        print(f" Ubicacin: {ruta_archivo}")
    
    try:
        # Leer el archivo TXT
        # El formato del SRI generalmente usa tabulaciones o punto y coma como separador
        print(f"   Leyendo archivo...")
        
        df = None
        
        # Intentar con diferentes separadores y encodings
        encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
        separadores = ['\t', ';', ',']
        
        for encoding in encodings:
            for separador in separadores:
                try:
                    df_temp = pd.read_csv(ruta_archivo, sep=separador, encoding=encoding)
                    if len(df_temp.columns) > 1:
                        df = df_temp
                        print(f"    Formato detectado: separador '{separador}', encoding '{encoding}'")
                        break
                except:
                    continue
            if df is not None:
                break
        
        # Si ninguno funciona, leer lnea por lnea
        if df is None:
            for encoding in encodings:
                try:
                    with open(ruta_archivo, 'r', encoding=encoding) as f:
                        lineas = f.readlines()
                    print(f"    Archivo ledo con encoding: {encoding}")
                    break
                except:
                    continue
            else:
                print("    No se pudo leer el archivo con ningn encoding")
                return None
            
            print(f"   Total de lneas: {len(lineas)}")
            
            # Intentar detectar encabezados en la primera lnea
            if lineas:
                encabezados = lineas[0].strip().split('\t')
                datos = []
                for linea in lineas[1:]:
                    campos = linea.strip().split('\t')
                    if len(campos) == len(encabezados):
                        datos.append(dict(zip(encabezados, campos)))
                
                df = pd.DataFrame(datos)
            else:
                return None
        
        if df is None or df.empty:
            print(" No se pudieron extraer datos del archivo")
            return None
            
        print(f"    Registros encontrados: {len(df)}")
        print(f"    Columnas: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f" Error al leer el archivo: {e}")
        import traceback
        traceback.print_exc()
        return None

def generar_excel_desde_txt(ruta_txt=None, nombre_salida="facturas_sri.xlsx"):
    """
    Genera un archivo Excel a partir del reporte TXT descargado
    """
    print("\n Generando Excel desde reporte TXT...")
    
    df = leer_reporte_txt(ruta_txt)
    
    if df is not None and not df.empty:
        # Limpiar y formatear datos
        print("   Formateando datos...")
        
        # Convertir columnas numricas
        columnas_numericas = ['Valor sin impuestos', 'IVA', 'Importe Total', 
                             'valor_sin_impuestos', 'iva', 'importe_total',
                             'VALOR_SIN_IMPUESTOS', 'IVA', 'IMPORTE_TOTAL']
        
        for col in df.columns:
            if any(num_col.lower() in col.lower() for num_col in columnas_numericas):
                try:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
                except:
                    pass
        
        # Guardar en Excel
        df.to_excel(nombre_salida, index=False, engine='openpyxl')
        
        print(f"\n Excel generado exitosamente:")
        print(f"    Archivo: {nombre_salida}")
        print(f"    Total de facturas: {len(df)}")
        print(f"    Columnas: {len(df.columns)}")
        
        # Mostrar primeras filas
        print(f"\n Vista previa (primeras 5 filas):")
        print(df.head().to_string())
        
        return True
    else:
        print(" No se pudieron procesar los datos")
        return False

def generar_excel_por_tipo(ruta_carpeta, nombre_salida, tipo_nombre):
    """
    Genera un archivo Excel para un tipo especfico (recibidos o emitidos)
    """
    print(f"\n{'='*60}")
    print(f"GENERANDO EXCEL - {tipo_nombre.upper()}")
    print(f"{'='*60}")
    
    print(f"\n Buscando archivos en: {ruta_carpeta}")
    
    if not os.path.exists(ruta_carpeta):
        print(f"   La carpeta no existe")
        return False
    
    archivos = os.listdir(ruta_carpeta)
    archivos_txt = [f for f in archivos if f.endswith('.txt')]
    
    print(f"   Archivos encontrados: {len(archivos)}")
    print(f"   Archivos TXT: {len(archivos_txt)}")
    
    if not archivos_txt:
        print(f"   No se encontraron archivos TXT")
        return False
    
    # Procesar todos los archivos TXT y combinarlos
    print(f"\n Procesando {len(archivos_txt)} archivos...")
    dataframes = []
    
    for archivo in archivos_txt:
        ruta_completa = os.path.join(ruta_carpeta, archivo)
        print(f"\n   Procesando: {archivo}")
        df = leer_reporte_txt(ruta_completa)
        if df is not None and not df.empty:
            dataframes.append(df)
    
    if not dataframes:
        print(f"   No se pudieron procesar los datos")
        return False
    
    # Combinar todos los DataFrames
    print(f"\n Combinando {len(dataframes)} archivos...")
    df_combinado = pd.concat(dataframes, ignore_index=True)
    
    # Eliminar duplicados si los hay
    df_combinado = df_combinado.drop_duplicates()
    
    # Limpiar y formatear datos
    print("   Formateando datos...")
    
    # Convertir columnas numricas
    columnas_numericas = ['Valor sin impuestos', 'IVA', 'Importe Total', 
                         'valor_sin_impuestos', 'iva', 'importe_total',
                         'VALOR_SIN_IMPUESTOS', 'IVA', 'IMPORTE_TOTAL']
    
    for col in df_combinado.columns:
        if any(num_col.lower() in col.lower() for num_col in columnas_numericas):
            try:
                df_combinado[col] = pd.to_numeric(df_combinado[col].astype(str).str.replace(',', '.'), errors='coerce')
            except:
                pass
    
    # Guardar en Excel
    df_combinado.to_excel(nombre_salida, index=False, engine='openpyxl')
    
    print(f"\n[OK] Excel generado exitosamente:")
    print(f"   Archivo: {nombre_salida}")
    print(f"   Total de facturas: {len(df_combinado)}")
    print(f"   Columnas: {len(df_combinado.columns)}")
    
    # Mostrar primeras filas
    print(f"\n Vista previa (primeras 5 filas):")
    print(df_combinado.head().to_string())
    
    return True


def generar_excel():
    """
    Funcin principal: Genera dos archivos Excel separados
    - facturas_recibidas.xlsx
    - facturas_emitidas.xlsx
    """
    print("\n" + "="*60)
    print("GENERANDO ARCHIVOS EXCEL")
    print("="*60)
    
    exitos = []
    
    # Generar Excel para RECIBIDOS
    print("\n[ENTRADA] Procesando comprobantes RECIBIDOS...")
    exito_rec = generar_excel_por_tipo(
        RECIBIDAS_PATH, 
        "facturas_recibidas.xlsx", 
        "Comprobantes Recibidos"
    )
    exitos.append(exito_rec)
    
    # Generar Excel para EMITIDOS
    print("\n[SALIDA] Procesando comprobantes EMITIDOS...")
    exito_emi = generar_excel_por_tipo(
        EMITIDAS_PATH, 
        "facturas_emitidas.xlsx", 
        "Comprobantes Emitidos"
    )
    exitos.append(exito_emi)
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE GENERACIN")
    print("="*60)
    
    if exito_rec:
        print("[OK] facturas_recibidas.xlsx - Generado correctamente")
    else:
        print("[ERROR] facturas_recibidas.xlsx - No se pudo generar")
    
    if exito_emi:
        print("[OK] facturas_emitidas.xlsx - Generado correctamente")
    else:
        print("[ERROR] facturas_emitidas.xlsx - No se pudo generar")
    
    print("="*60)
