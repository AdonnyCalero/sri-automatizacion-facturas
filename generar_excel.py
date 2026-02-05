# generar_excel.py

import os
import pandas as pd
from procesar_xml import leer_factura_xml
from config import RECIBIDAS_PATH, EMITIDAS_PATH

def cargar_xmls(ruta, tipo):
    registros = []

    for archivo in os.listdir(ruta):
        if archivo.endswith(".xml"):
            datos = leer_factura_xml(os.path.join(ruta, archivo))
            datos["tipo"] = tipo
            registros.append(datos)

    return registros

def generar_excel():
    data = []
    data += cargar_xmls(RECIBIDAS_PATH, "RECIBIDA")
    data += cargar_xmls(EMITIDAS_PATH, "EMITIDA")

    df = pd.DataFrame(data)
    df.to_excel("facturas_sri.xlsx", index=False)

    print("✅ Archivo facturas_sri.xlsx generado automáticamente")
