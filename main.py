# main.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

options = Options()
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
    descargar_documentos(driver, descargar_xml=True, descargar_pdf=True)

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
    descargar_documentos(driver, descargar_xml=True, descargar_pdf=True)

finally:
    driver.quit()

# Genera el Excel automáticamente
generar_excel()
