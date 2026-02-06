from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def descargar_documentos_simplificado(driver, directorio_descarga, tipo="xml"):
    """
    Descarga todos los documentos (XML o PDF) de la página actual
    usando los IDs específicos de los enlaces
    """
    print(f"   Buscando enlaces de {tipo.upper()}...")
    
    # Buscar todos los enlaces con el patrón lnkXml o lnkPdf
    selector = f'a[id*="lnk{tipo.upper()}"]'
    enlaces = driver.find_elements(By.CSS_SELECTOR, selector)
    
    print(f"   Encontrados {len(enlaces)} enlaces de {tipo.upper()}")
    
    descargados = 0
    fallidos = 0
    
    for i, enlace in enumerate(enlaces):
        try:
            # Extraer el ID de la clave de acceso (del enlace de la misma fila)
            fila_id = enlace.get_attribute('id').split(':')[2]  # Ej: "0" de "frmPrincipal:tablaCompRecibidos:0:lnkXml"
            
            # Buscar el enlace de clave de acceso en la misma fila
            clave_selector = f'a[id*="tablaCompRecibidos:{fila_id}:j_idt"]'
            try:
                clave_elem = driver.find_element(By.CSS_SELECTOR, clave_selector)
                clave_texto = clave_elem.text.strip().replace('-', '')
                nombre_base = clave_texto[-10:] if len(clave_texto) >= 10 else f"doc_{i+1}"
            except:
                nombre_base = f"doc_{i+1}"
            
            # Registrar archivos existentes
            archivos_antes = set(os.listdir(directorio_descarga))
            
            # Hacer clic en el enlace
            driver.execute_script("arguments[0].click();", enlace)
            
            # Esperar descarga
            tiempo_espera = 0
            archivo_descargado = False
            archivo_nuevo = None
            
            while tiempo_espera < 15:
                time.sleep(1)
                tiempo_espera += 1
                
                archivos_despues = set(os.listdir(directorio_descarga))
                archivos_nuevos = archivos_despues - archivos_antes
                archivos_nuevos = [f for f in archivos_nuevos if not f.endswith(('.crdownload', '.tmp'))]
                
                if tipo == "xml":
                    tipo_nuevos = [f for f in archivos_nuevos if f.endswith('.xml')]
                else:
                    tipo_nuevos = [f for f in archivos_nuevos if f.endswith('.pdf')]
                
                if tipo_nuevos:
                    archivo_nuevo = tipo_nuevos[0]
                    archivo_descargado = True
                    break
            
            if archivo_descargado and archivo_nuevo:
                nuevo_nombre = f"{nombre_base}.{tipo}"
                ruta_original = os.path.join(directorio_descarga, archivo_nuevo)
                ruta_nueva = os.path.join(directorio_descarga, nuevo_nombre)
                
                contador = 1
                while os.path.exists(ruta_nueva):
                    ruta_nueva = os.path.join(directorio_descarga, f"{nombre_base}_{contador}.{tipo}")
                    contador += 1
                
                os.rename(ruta_original, ruta_nueva)
                print(f"   ✓ {tipo.upper()}: {os.path.basename(ruta_nueva)}")
                descargados += 1
            else:
                print(f"   ⚠️ {tipo.upper()} {i+1}: timeout")
                fallidos += 1
                
        except Exception as e:
            print(f"   ⚠️ Error en {tipo.upper()} {i+1}: {str(e)[:50]}")
            fallidos += 1
        
        time.sleep(1)
    
    return descargados, fallidos


# Probar el script
if __name__ == "__main__":
    options = Options()
    options.add_experimental_option("prefs", {
        "download.prompt_for_download": False,
        "download.default_directory": os.path.abspath("facturas_xml/recibidas"),
    })
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Aquí iría tu código de login y navegación
        # Por ahora, asumimos que ya estamos en la página correcta
        
        directorio = "facturas_xml/recibidas"
        os.makedirs(directorio, exist_ok=True)
        
        print("Descargando XMLs...")
        xml_ok, xml_fail = descargar_documentos_simplificado(driver, directorio, "xml")
        
        print("Descargando PDFs...")
        pdf_ok, pdf_fail = descargar_documentos_simplificado(driver, directorio, "pdf")
        
        print(f"\n✅ Resumen:")
        print(f"   XMLs: {xml_ok} descargados, {xml_fail} fallidos")
        print(f"   PDFs: {pdf_ok} descargados, {pdf_fail} fallidos")
        
    finally:
        driver.quit()
