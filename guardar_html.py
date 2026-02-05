# guardar_html.py

import os
from datetime import datetime

def guardar_html(driver, nombre="pagina"):
    os.makedirs("debug/html", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = f"debug/html/{nombre}_{timestamp}.html"

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    print(f"HTML guardado en: {ruta}")
