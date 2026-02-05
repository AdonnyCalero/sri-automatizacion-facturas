# login_sri.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import RUC, CLAVE, URL_SRI

def login(driver):
    driver.get(URL_SRI)

    wait = WebDriverWait(driver, 30)

    # 1️⃣ Clic en "Iniciar sesión" (arriba a la derecha)
    btn_login = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(., 'Iniciar sesión')]")
        )
    )
    btn_login.click()

    # 2️⃣ Esperar campo usuario (RUC / cédula)
    usuario = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='text' or @type='email']")
        )
    )
    usuario.clear()
    usuario.send_keys(RUC)

    # 3️⃣ Esperar campo contraseña
    password = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='password']")
        )
    )
    password.clear()
    password.send_keys(CLAVE)
    password.send_keys(Keys.ENTER)

    # 4️⃣ Tiempo para captcha y carga del sistema
    time.sleep(12)
