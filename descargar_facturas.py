from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from guardar_html import guardar_html


def cambiar_a_iframe_menu(driver):
    wait = WebDriverWait(driver, 20)

    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    for iframe in iframes:
        driver.switch_to.frame(iframe)
        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'Facturación')]")
            print("✅ IFRAME correcto encontrado")
            return
        except:
            driver.switch_to.default_content()

    raise Exception("❌ No se encontró iframe del menú")


import time
from guardar_html import guardar_html


def ir_a_comprobantes(driver, tipo):
    if tipo == "RECIBIDAS":
        texto = "Comprobantes recibidos"
    else:
        texto = "Comprobantes emitidos"

    script = f"""
    const spans = [...document.querySelectorAll('span')];
    const target = spans.find(s => s.innerText.includes('{texto}'));
    if (target) {{
        target.click();
        return true;
    }}
    return false;
    """

    encontrado = driver.execute_script(script)

    if not encontrado:
        raise Exception(f"No se encontró opción: {texto}")

    time.sleep(5)

    guardar_html(driver, f"menu_{tipo.lower()}")


def filtrar_fechas(driver, desde, hasta):
    pass


def descargar_xmls(driver):
    pass
