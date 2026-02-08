# main.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
from config import (
    RECIBIDAS_PATH,
    EMITIDAS_PATH,
    FECHA_DESDE,
    FECHA_HASTA
)
from login_sri import login
from descargar_facturas import (
    ir_a_comprobantes,
    ir_a_emitidas_nuevo_menu,
    diagnosticar_menu,
    filtrar_fechas,
    descargar_documentos
)
from generar_excel import generar_excel
from guardar_html import guardar_html

# Crear directorios de descarga si no existen
os.makedirs(RECIBIDAS_PATH, exist_ok=True)
os.makedirs(EMITIDAS_PATH, exist_ok=True)

# Configurar opciones de Chrome para descargas automticas
options = Options()

# Usar rutas absolutas para los directorios de descarga
recibidas_abs = os.path.abspath(RECIBIDAS_PATH)

options.add_experimental_option("prefs", {
    "download.default_directory": recibidas_abs,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "safebrowsing.disable_download_protection": True,
    "profile.default_content_setting_values.automatic_downloads": 1
})

print(f"Directorio de descarga configurado: {recibidas_abs}")

# Opciones adicionales para evitar problemas de descarga
options.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(options=options)

# Variable para controlar si descargamos algo
descarga_exitosa = False

try:
    login(driver)

    shadow_test = driver.execute_script("""
    return document.querySelectorAll('*')
    .length;
    """)

    print("DOM cargado correctamente")


    # DEBUG: listar iframes
    iframes = driver.find_elements("tag name", "iframe")
    print(f"IFRAMES encontrados: {len(iframes)}")

    for i, iframe in enumerate(iframes):
        print(f"Iframe {i}: {iframe.get_attribute('src')}")

    import time
    time.sleep(5)

    guardar_html(driver, "01_dashboard")

    # ========= FACTURAS RECIBIDAS =========
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": RECIBIDAS_PATH}
    )

    ir_a_comprobantes(driver, "RECIBIDAS")
    time.sleep(5)
    guardar_html(driver, "02_recibidas_menu")

    filtrar_fechas(driver, FECHA_DESDE, FECHA_HASTA)
    time.sleep(5)
    guardar_html(driver, "03_recibidas_filtradas")

    print("Descargando documentos recibidos...")
    resultado = descargar_documentos(driver, descargar_xml=True, descargar_pdf=True, directorio_descarga=RECIBIDAS_PATH)
    
    if resultado and (resultado.get('xml', 0) > 0 or resultado.get('pdf', 0) > 0):
        descarga_exitosa = True
        print(f" Descarga de recibidas completada")

    # ========= FACTURAS EMITIDAS (OPCIONAL) =========
    try:
        print("\n" + "="*60)
        print("PREPARANDO NAVEGACION A COMPROBANTES EMITIDOS")
        print("="*60)
        
        # Esperar un momento para asegurar que la página esté estable
        print("Esperando 3 segundos para estabilizar la página...")
        time.sleep(3)
        
        # Ejecutar diagnóstico del menú
        diagnosticar_menu(driver)
        
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": EMITIDAS_PATH}
        )

        ir_a_emitidas_nuevo_menu(driver)
        time.sleep(5)
        guardar_html(driver, "04_emitidas_menu")

        filtrar_fechas(driver, FECHA_DESDE, FECHA_HASTA)
        time.sleep(5)
        guardar_html(driver, "05_emitidas_filtradas")

        print("Descargando documentos emitidos...")
        resultado = descargar_documentos(driver, descargar_xml=True, descargar_pdf=True, directorio_descarga=EMITIDAS_PATH)
        
        if resultado and (resultado.get('xml', 0) > 0 or resultado.get('pdf', 0) > 0):
            descarga_exitosa = True
            print(f" Descarga de emitidas completada")
            
    except Exception as e:
        print(f" No se pudieron descargar emitidas: {e}")
        print("   Continuando con generacin de Excel...")

except Exception as e:
    print(f"\n Error durante la ejecucin: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()

# Genera el Excel automticamente al final (siempre, incluso si hubo errores)
print("\n" + "="*60)
print("PROCESO FINALIZADO - GENERANDO EXCEL")
print("="*60)

try:
    generar_excel()
    print("\n PROCESO COMPLETADO")
except Exception as e:
    print(f"\n Error al generar Excel: {e}")
    import traceback
    traceback.print_exc()
