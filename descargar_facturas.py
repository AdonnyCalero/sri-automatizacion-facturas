from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
from guardar_html import guardar_html


def descargar_reporte_txt_requests(driver, directorio_descarga=None):
    """
    Descarga el reporte TXT usando requests con las cookies de sesión de Selenium
    Este método es más confiable que hacer clic en el navegador
    """
    if not directorio_descarga:
        directorio_descarga = "facturas_xml/recibidas"
    
    # Asegurar que el directorio existe
    os.makedirs(directorio_descarga, exist_ok=True)
    
    try:
        print("   Descargando reporte con requests...")
        
        # Obtener cookies del driver
        cookies = driver.get_cookies()
        session = requests.Session()
        
        # Agregar cookies a la sesión
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        # Headers para simular navegador
        headers = {
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': driver.current_url,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Obtener ViewState
        try:
            viewstate = driver.find_element(By.NAME, "javax.faces.ViewState").get_attribute("value")
        except:
            viewstate = ""
        
        # Datos del formulario para descargar el reporte
        data = {
            "frmPrincipal": "frmPrincipal",
            "frmPrincipal:lnkTxtlistado": "frmPrincipal:lnkTxtlistado",
            "javax.faces.ViewState": viewstate
        }
        
        # Hacer la petición POST
        url = driver.current_url
        response = session.post(url, data=data, headers=headers, timeout=30, allow_redirects=True)
        
        if response.status_code == 200:
            # Verificar que no sea HTML (que sería un error)
            content_type = response.headers.get('Content-Type', '')
            
            if 'text/html' in content_type:
                # Guardar HTML de error para debug
                debug_file = os.path.join(directorio_descarga, "debug_reporte_error.html")
                with open(debug_file, 'wb') as f:
                    f.write(response.content)
                print(f"   ⚠️ La respuesta es HTML (error). Guardado en: {debug_file}")
                return False
            
            # Determinar extensión
            if 'text/plain' in content_type or response.content.startswith(b'Clave'):
                extension = 'txt'
            else:
                extension = 'txt'  # Por defecto
            
            # Generar nombre de archivo
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_sri_{timestamp}.{extension}"
            ruta_archivo = os.path.join(directorio_descarga, nombre_archivo)
            
            # Guardar archivo
            with open(ruta_archivo, 'wb') as f:
                f.write(response.content)
            
            print(f"   ✅ Reporte descargado: {nombre_archivo}")
            print(f"   📁 Tamaño: {len(response.content)} bytes")
            print(f"   📂 Ubicación: {ruta_archivo}")
            return True
        else:
            print(f"   ⚠️ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Error: {str(e)[:100]}")
        return False


def descargar_reporte_txt(driver, directorio_descarga=None, max_intentos=3):
    """
    Intenta descargar el reporte primero con requests, si falla intenta con Selenium
    """
    if not directorio_descarga:
        directorio_descarga = "facturas_xml/recibidas"
    
    # Intentar primero con requests
    if descargar_reporte_txt_requests(driver, directorio_descarga):
        return True
    
    # Si falla, intentar con Selenium (método anterior)
    print("   Intentando método alternativo (Selenium)...")
    
    for intento in range(max_intentos):
        try:
            archivos_antes = set(os.listdir(directorio_descarga))
            
            # Buscar el botón
            try:
                boton_descarga = driver.find_element(By.ID, "frmPrincipal:lnkTxtlistado")
            except:
                script = """
                const enlaces = document.querySelectorAll('a');
                for (let enlace of enlaces) {
                    const texto = enlace.innerText || enlace.textContent || '';
                    if (texto.toLowerCase().includes('descargar reporte')) {
                        return enlace.id;
                    }
                }
                return null;
                """
                boton_id = driver.execute_script(script)
                if not boton_id:
                    return False
                boton_descarga = driver.find_element(By.ID, boton_id)
            
            # Hacer clic normal (no con JavaScript)
            boton_descarga.click()
            
            # Esperar
            tiempo_espera = 0
            while tiempo_espera < 20:
                time.sleep(1)
                tiempo_espera += 1
                
                try:
                    archivos_despues = set(os.listdir(directorio_descarga))
                    archivos_nuevos = archivos_despues - archivos_antes
                    archivos_nuevos = [f for f in archivos_nuevos if not f.endswith(('.crdownload', '.tmp'))]
                    
                    if archivos_nuevos:
                        print(f"   ✅ Descargado: {archivos_nuevos[0]}")
                        return True
                except:
                    continue
            
            if intento < max_intentos - 1:
                time.sleep(2)
                
        except Exception as e:
            if intento < max_intentos - 1:
                time.sleep(2)
            continue
    
    return False


def descargar_documentos(driver, descargar_xml=True, descargar_pdf=True, directorio_descarga=None):
    """
    Descarga el reporte TXT completo
    """
    print("📄 Descargando reporte...")
    
    exito = descargar_reporte_txt(driver, directorio_descarga)
    
    if exito:
        print("\n✅ Reporte descargado exitosamente")
        return {'xml': 1, 'pdf': 0}
    else:
        print("\n❌ No se pudo descargar el reporte")
        print("💡 Sugerencia: Intenta hacer clic manualmente en el botón 'Descargar reporte'")
        return {'xml': 0, 'pdf': 0}


def cambiar_a_iframe_menu(driver):
    """Cambia al iframe del menú si es necesario"""
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


def ir_a_comprobantes(driver, tipo):
    """Navega a comprobantes recibidos o emitidos"""
    if tipo == "RECIBIDAS":
        submenu_texto = "Comprobantes electrónicos recibidos"
    else:
        submenu_texto = "Comprobantes electrónicos emitidos"
    
    print("Abriendo menú hamburguesa...")
    script_menu = """
    const menuBtn = document.getElementById('sri-menu');
    if (menuBtn) {
        menuBtn.click();
        return true;
    }
    const menuAlt = document.querySelector('.sri-menu-icon-menu-hamburguesa');
    if (menuAlt) {
        menuAlt.click();
        return true;
    }
    return false;
    """
    
    menu_abierto = driver.execute_script(script_menu)
    if menu_abierto:
        print("✅ Menú abierto")
        time.sleep(3)
    else:
        print("⚠️ No se pudo abrir el menú")
    
    print("Buscando FACTURACIÓN ELECTRÓNICA...")
    script_facturacion = """
    const elementos = [...document.querySelectorAll('span, a, div, li')];
    const facturacion = elementos.find(el => {
        const texto = el.innerText || el.textContent || '';
        return texto.toUpperCase().includes('FACTURACIÓN ELECTRÓNICA');
    });
    
    if (facturacion) {
        let clickable = facturacion;
        while (clickable && clickable.tagName !== 'BODY') {
            if (clickable.onclick || clickable.tagName === 'A' || clickable.tagName === 'BUTTON' || 
                clickable.classList.contains('ui-panelmenu-header') ||
                clickable.classList.contains('menu-item')) {
                clickable.click();
                return true;
            }
            clickable = clickable.parentElement;
        }
        facturacion.click();
        return true;
    }
    return false;
    """
    
    facturacion_encontrada = driver.execute_script(script_facturacion)
    if facturacion_encontrada:
        print("✅ FACTURACIÓN ELECTRÓNICA desplegada")
        time.sleep(2)
    else:
        print("⚠️ No se encontró FACTURACIÓN ELECTRÓNICA")
    
    print(f"Buscando submenú: {submenu_texto}...")
    script = f"""
    const spans = [...document.querySelectorAll('span')];
    const target = spans.find(s => s.innerText.includes('{submenu_texto}'));
    if (target) {{
        target.click();
        return true;
    }}
    
    const links = [...document.querySelectorAll('a')];
    const linkTarget = links.find(a => a.innerText.includes('{submenu_texto}'));
    if (linkTarget) {{
        linkTarget.click();
        return true;
    }}
    
    const menuItems = [...document.querySelectorAll('.w3-bar-item, .menu-item, .ui-menuitem, .ui-panelmenu-content')];
    const menuTarget = menuItems.find(item => item.innerText.includes('{submenu_texto}'));
    if (menuTarget) {{
        menuTarget.click();
        return true;
    }}
    
    const allElements = [...document.querySelectorAll('*')];
    const partialTarget = allElements.find(el => {{
        const text = el.innerText || el.textContent || '';
        return text.toLowerCase().includes('{submenu_texto.lower().replace("comprobantes electrónicos ", "")}');
    }});
    if (partialTarget) {{
        partialTarget.click();
        return true;
    }}
    
    return false;
    """
    
    encontrado = driver.execute_script(script)
    
    if not encontrado:
        raise Exception(f"No se encontró opción: {submenu_texto}")
    
    print(f"✅ Navegando a {submenu_texto}")
    time.sleep(5)
    guardar_html(driver, f"menu_{tipo.lower()}")


def filtrar_fechas(driver, desde, hasta, ruc=None):
    """Filtra facturas por rango de fechas y descarga el reporte"""
    wait = WebDriverWait(driver, 20)
    
    try:
        time.sleep(3)
        print(f"Filtrando desde: {desde} hasta: {hasta}")
        
        desde_partes = desde.split('/')
        desde_anio = desde_partes[2]
        desde_mes = desde_partes[1]
        
        def obtener_nombre_mes(numero_mes):
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            return meses[int(numero_mes) - 1] if numero_mes.isdigit() else meses[0]
        
        mes_nombre = obtener_nombre_mes(desde_mes)
        print(f"Configurando fecha: {desde_anio} - {mes_nombre} - Todos")
        
        script_formulario = f"""
        const resultado = {{}};
        
        if ('{ruc if ruc else ""}') {{
            const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
            for (let input of inputs) {{
                const placeholder = input.getAttribute('placeholder') || '';
                if (placeholder.toLowerCase().includes('ruc') || 
                    placeholder.toLowerCase().includes('cédula') ||
                    placeholder.toLowerCase().includes('pasaporte')) {{
                    input.value = '{ruc}';
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    resultado.ruc = true;
                    break;
                }}
            }}
        }}
        
        const allSelects = document.querySelectorAll('select');
        console.log('Total de selects encontrados:', allSelects.length);
        
        let periodoSelects = [];
        for (let i = 0; i < allSelects.length; i++) {{
            const parent = allSelects[i].closest('div, td, label, tr');
            const parentText = parent ? (parent.innerText || parent.textContent || '') : '';
            if (parentText.toLowerCase().includes('periodo') || 
                parentText.toLowerCase().includes('emisión')) {{
                periodoSelects.push(allSelects[i]);
            }}
        }}
        
        console.log('Selects de período encontrados:', periodoSelects.length);
        
        if (periodoSelects.length === 0) {{
            periodoSelects = Array.from(allSelects).slice(0, 3);
        }}
        
        if (periodoSelects[0]) {{
            for (let option of periodoSelects[0].options) {{
                if (option.value === '{desde_anio}' || option.text === '{desde_anio}') {{
                    periodoSelects[0].value = option.value;
                    periodoSelects[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    resultado.anio = true;
                    console.log('Año seleccionado:', option.text);
                    break;
                }}
            }}
        }}
        
        if (periodoSelects[1]) {{
            for (let option of periodoSelects[1].options) {{
                if (option.text === '{mes_nombre}' || 
                    option.text === '{desde_mes}' || 
                    option.text.includes('{mes_nombre}') ||
                    option.value === '{int(desde_mes)}' ||
                    option.text === '{int(desde_mes)}') {{
                    periodoSelects[1].value = option.value;
                    periodoSelects[1].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    resultado.mes = true;
                    console.log('Mes seleccionado:', option.text);
                    break;
                }}
            }}
        }}
        
        if (periodoSelects[2]) {{
            for (let option of periodoSelects[2].options) {{
                const optionText = option.text || option.value || '';
                if (optionText.toUpperCase().includes('TODOS') || 
                    option.value === '0' || 
                    option.value === '' ||
                    optionText.trim() === '') {{
                    periodoSelects[2].value = option.value;
                    periodoSelects[2].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    resultado.todos = true;
                    console.log('Opción Todos seleccionada:', option.text);
                    break;
                }}
            }}
        }}
        
        for (let select of allSelects) {{
            const parent = select.closest('div, td, label, tr');
            const parentText = parent ? (parent.innerText || parent.textContent || '') : '';
            
            if (parentText.toLowerCase().includes('tipo de comprobante')) {{
                for (let option of select.options) {{
                    if (option.text === 'Factura' || 
                        option.text.includes('Factura') ||
                        option.value.toUpperCase().includes('FACTURA')) {{
                        select.value = option.value;
                        select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        resultado.tipoComprobante = true;
                        console.log('Tipo de comprobante seleccionado:', option.text);
                        break;
                    }}
                }}
            }}
        }}
        
        return resultado;
        """
        
        resultado = driver.execute_script(script_formulario)
        print(f"Campos configurados: {resultado}")
        
        time.sleep(2)
        print("⏳ Esperando a que el reCAPTCHA esté listo...")
        time.sleep(3)
        
        script_boton = """
        const botones = document.querySelectorAll('button, input[type="submit"], input[type="button"], a');
        for (let btn of botones) {
            const texto = (btn.textContent || btn.value || '').toLowerCase();
            if (texto.trim() === 'consultar' || 
                texto.includes('consultar') || 
                texto.includes('buscar') ||
                texto.includes('filtrar') ||
                btn.className.toLowerCase().includes('consultar') ||
                btn.id.toLowerCase().includes('consultar')) {
                if (btn.offsetParent !== null && !btn.disabled) {
                    console.log('Botón encontrado:', btn);
                    btn.click();
                    return true;
                }
            }
        }
        
        const btnConsultar = document.querySelector('[id*="consultar"], [id*="Consultar"], .ui-button, .btn-consultar');
        if (btnConsultar && btnConsultar.offsetParent !== null && !btnConsultar.disabled) {
            btnConsultar.click();
            return true;
        }
        
        return false;
        """
        
        boton_encontrado = driver.execute_script(script_boton)
        
        if boton_encontrado:
            print("✅ Botón de consulta presionado")
        else:
            print("⚠️ No se encontró botón de consulta")
        
        time.sleep(5)
        
        script_recaptcha = """
        const recaptcha = document.querySelector('.g-recaptcha, [id*="recaptcha"], iframe[title*="reCAPTCHA"]');
        if (recaptcha) {
            console.log('reCAPTCHA detectado');
            return true;
        }
        return false;
        """
        
        recaptcha_detectado = driver.execute_script(script_recaptcha)
        if recaptcha_detectado:
            print("🔐 reCAPTCHA detectado - Esperando 10 segundos para resolución manual...")
            time.sleep(10)
        
        # Después de filtrar, descargar el reporte
        print("\n📥 Descargando reporte...")
        descargar_reporte_txt(driver)
        
    except Exception as e:
        print(f"⚠️ Error al filtrar fechas: {e}")
        import traceback
        traceback.print_exc()


def descargar_xmls(driver):
    """Función legacy - ahora usa descargar_documentos"""
    resultado = descargar_documentos(driver, descargar_xml=True, descargar_pdf=False)
    return resultado['xml']
