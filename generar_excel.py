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

def generar_excel():
    """
    Funcin principal: intenta generar Excel desde TXT primero, 
    si no hay TXT, procesa los XML individuales
    """
    print("\n" + "="*60)
    print("GENERANDO EXCEL")
    print("="*60)
    
    # Debug: mostrar informacin de bsqueda
    print(f"\n Buscando archivos...")
    print(f"   Carpeta recibidas: {RECIBIDAS_PATH}")
    print(f"   Existe: {os.path.exists(RECIBIDAS_PATH)}")
    print(f"   Carpeta emitidas: {EMITIDAS_PATH}")
    print(f"   Existe: {os.path.exists(EMITIDAS_PATH)}")
    
    # Buscar en ambas carpetas
    archivos_txt_total = []
    
    if os.path.exists(RECIBIDAS_PATH):
        archivos = os.listdir(RECIBIDAS_PATH)
        archivos_txt_rec = [f for f in archivos if f.endswith('.txt')]
        print(f"\n   RECIBIDAS:")
        print(f"   - Archivos: {len(archivos)}")
        print(f"   - TXT: {len(archivos_txt_rec)}")
        if archivos_txt_rec:
            print(f"   - Lista: {archivos_txt_rec}")
        archivos_txt_total.extend([os.path.join(RECIBIDAS_PATH, f) for f in archivos_txt_rec])
    
    if os.path.exists(EMITIDAS_PATH):
        archivos = os.listdir(EMITIDAS_PATH)
        archivos_txt_emi = [f for f in archivos if f.endswith('.txt')]
        print(f"\n   EMITIDAS:")
        print(f"   - Archivos: {len(archivos)}")
        print(f"   - TXT: {len(archivos_txt_emi)}")
        if archivos_txt_emi:
            print(f"   - Lista: {archivos_txt_emi}")
        archivos_txt_total.extend([os.path.join(EMITIDAS_PATH, f) for f in archivos_txt_emi])
    
    print(f"\n   Total TXT encontrados: {len(archivos_txt_total)}")
    
    # Intentar primero con el reporte TXT
    print("\n Intentando generar desde TXT...")
    if generar_excel_desde_txt():
        return
    
    # Si no hay TXT, procesar XMLs individuales (mtodo anterior)
    print("\n No se encontr reporte TXT, procesando archivos XML individuales...")
    
    data = []
    data += cargar_xmls(RECIBIDAS_PATH, "RECIBIDA")
    data += cargar_xmls(EMITIDAS_PATH, "EMITIDA")

    if data:
        df = pd.DataFrame(data)
        df.to_excel("facturas_sri.xlsx", index=False)
        print(f" Archivo facturas_sri.xlsx generado ({len(df)} facturas)")
    else:
        print(" No se encontraron datos para generar el Excel")
