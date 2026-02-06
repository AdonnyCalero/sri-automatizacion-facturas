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
    filtrar_fechas,
    descargar_documentos
)
from generar_excel import generar_excel
from guardar_html import guardar_html

# Crear directorios de descarga si no existen
os.makedirs(RECIBIDAS_PATH, exist_ok=True)
os.makedirs(EMITIDAS_PATH, exist_ok=True)

# Configurar opciones de Chrome para descargas automáticas
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": RECIBIDAS_PATH,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "safebrowsing.disable_download_protection": True,
    "profile.default_content_setting_values.automatic_downloads": 1
})

# Opciones adicionales para evitar problemas de descarga
options.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(options=options)

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

    print("Descargando documentos recibidos (XML y PDF)...")
    descargar_documentos(driver, descargar_xml=True, descargar_pdf=True, directorio_descarga=RECIBIDAS_PATH)

    # ========= FACTURAS EMITIDAS =========
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": EMITIDAS_PATH}
    )

    ir_a_comprobantes(driver, "EMITIDAS")
    time.sleep(5)
    guardar_html(driver, "04_emitidas_menu")

    filtrar_fechas(driver, FECHA_DESDE, FECHA_HASTA)
    time.sleep(5)
    guardar_html(driver, "05_emitidas_filtradas")

    print("Descargando documentos emitidos (XML y PDF)...")
    descargar_documentos(driver, descargar_xml=True, descargar_pdf=True, directorio_descarga=EMITIDAS_PATH)

finally:
    driver.quit()

# Genera el Excel automáticamente
generar_excel()
