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
        
        # Verificar que estamos en la página correcta
        url_actual = driver.current_url
        print(f"   URL actual: {url_actual}")
        
        if 'menu.jsf' in url_actual and 'recuperarComprobantes' not in url_actual:
            print("   ⚠️ No estamos en la página de resultados. Intentando navegar desde el menú...")
            # Si estamos en el menú, no podemos descargar directamente
            return False
        
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
    
    print("Abriendo menu hamburguesa...")
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
        raise Exception(f"No se encontro opcion: {submenu_texto}")
    
    print(f"Navegando a {submenu_texto}")
    time.sleep(5)
    guardar_html(driver, f"menu_{tipo.lower()}")


def diagnosticar_menu(driver):
    """
    Función de diagnóstico para entender la estructura real del menú SRI
    """
    print("\n🔍 DIAGNÓSTICO DEL MENÚ")
    print("="*60)
    
    script = """
    const resultado = {
        botonMenu: null,
        cssmenu: null,
        menuNuevo: null,
        itemsPrincipales: [],
        elementosFacturacion: []
    };
    
    // Buscar botón de menú hamburguesa
    const menuIcon = document.querySelector('.sri-menu-icon-menu-hamburguesa');
    const menuLink = document.querySelector('a[onclick*="mostrarOcultaSidebar"]');
    
    if (menuIcon) {
        resultado.botonMenu = {
            tipo: 'icono',
            className: menuIcon.className,
            tieneMenuLink: !!menuLink
        };
    } else if (menuLink) {
        resultado.botonMenu = {
            tipo: 'enlace',
            onclick: menuLink.getAttribute('onclick')
        };
    }
    
    // Buscar #cssmenu (menú principal)
    const cssmenu = document.querySelector('#cssmenu');
    resultado.cssmenu = {
        existe: !!cssmenu,
        htmlLength: cssmenu ? cssmenu.innerHTML.length : 0
    };
    
    // Buscar #menuNuevo
    const menuNuevo = document.querySelector('#menuNuevo');
    resultado.menuNuevo = {
        existe: !!menuNuevo,
        clases: menuNuevo ? menuNuevo.className : null,
        visible: menuNuevo ? menuNuevo.offsetParent !== null : false
    };
    
    // Si existe cssmenu, obtener todos los items principales
    if (cssmenu) {
        const items = cssmenu.querySelectorAll(':scope > ul > li');
        resultado.itemsPrincipales = Array.from(items).map(li => {
            const enlace = li.querySelector('a');
            return {
                texto: (li.innerText || '').trim().substring(0, 80),
                tieneSubmenu: li.classList.contains('has-sub'),
                idEnlace: enlace ? enlace.id : null,
                onclick: enlace ? (enlace.getAttribute('onclick') || '').substring(0, 100) : null
            };
        });
    }
    
    // Buscar elementos relacionados con Facturación electrónica
    const todosElementos = document.querySelectorAll('#cssmenu *');
    for (let el of todosElementos) {
        const texto = (el.innerText || el.textContent || '').trim().toUpperCase();
        if ((texto.includes('FACTURACIÓN') || texto.includes('FACTURACION')) && 
            (texto.includes('ELECTRÓNICA') || texto.includes('ELECTRONICA'))) {
            resultado.elementosFacturacion.push({
                texto: el.innerText.trim().substring(0, 60),
                tagName: el.tagName,
                visible: el.offsetParent !== null,
                parentText: el.parentElement ? el.parentElement.innerText.trim().substring(0, 40) : ''
            });
        }
    }
    
    return resultado;
    """
    
    resultado = driver.execute_script(script)
    
    print(f"Botón de menú: {resultado.get('botonMenu')}")
    print(f"\nCSSMENU: {resultado.get('cssmenu')}")
    print(f"MenuNuevo: {resultado.get('menuNuevo')}")
    print(f"\nItems principales del menú ({len(resultado.get('itemsPrincipales', []))}):")
    for item in resultado.get('itemsPrincipales', []):
        print(f"  - {item.get('texto')} {'[-submenu]' if item.get('tieneSubmenu') else ''}")
        if item.get('idEnlace'):
            print(f"    ID: {item.get('idEnlace')}")
    
    print(f"\nElementos 'Facturación electrónica' ({len(resultado.get('elementosFacturacion', []))}):")
    for elem in resultado.get('elementosFacturacion', []):
        print(f"  - {elem.get('texto')} [{elem.get('tagName')}] {'(visible)' if elem.get('visible') else '(oculto)'}")
    
    print("="*60)


def ir_a_emitidas_nuevo_menu(driver):
    """
    Navega a Comprobantes electrónicos emitidos siguiendo el nuevo flujo:
    Facturación electrónica -> Producción -> Consultas -> Comprobantes electrónicos emitidos
    Basado en la estructura real del HTML del SRI.
    """
    print("\n" + "="*60)
    print("NAVEGANDO A EMITIDAS (NUEVO MENU)")
    print("="*60)
    
    wait = WebDriverWait(driver, 10)
    
    # 1. Abrir el menú hamburguesa
    print("\n1. Abriendo menu hamburguesa...")
    script_abrir_menu = """
    // Usar la función JavaScript del SRI para abrir el menú
    if (typeof mostrarOcultaSidebar === 'function') {
        mostrarOcultaSidebar();
        return {encontrado: true, metodo: 'funcion_js'};
    }
    
    // Alternativa: buscar el botón de menú
    const menuIcon = document.querySelector('.sri-menu-icon-menu-hamburguesa');
    if (menuIcon) {
        menuIcon.click();
        return {encontrado: true, metodo: 'icono'};
    }
    
    const menuLink = document.querySelector('.top-icono-menu');
    if (menuLink) {
        menuLink.click();
        return {encontrado: true, metodo: 'top_icono'};
    }
    
    return {encontrado: false};
    """
    
    resultado = driver.execute_script(script_abrir_menu)
    if resultado.get('encontrado'):
        print(f"   ✅ Menú abierto ({resultado.get('metodo')})")
        time.sleep(4)  # Esperar a que el menú se cargue completamente
    else:
        print("   ❌ No se encontró botón de menú")
        raise Exception("No se pudo abrir el menú")
    
    # 2. Esperar a que el menú se cargue dinámicamente con AJAX
    print("\n2. Esperando que el menú se cargue completamente...")
    time.sleep(5)  # Esperar carga del menú via AJAX
    
    # Guardar HTML para debugging
    guardar_html(driver, "debug_menu_abierto")
    
    # 3. Hacer clic en "Facturación electrónica" expandiendo el submenú
    print("\n3. Expandiendo 'Facturación electrónica'...")
    script_facturacion = """
    const cssmenu = document.querySelector('#cssmenu');
    if (!cssmenu) {
        return {encontrado: false, error: 'No se encontró #cssmenu'};
    }
    
    // Buscar el enlace principal de Facturación Electrónica
    const items = cssmenu.querySelectorAll('li.has-sub > a');
    
    for (let item of items) {
        const texto = (item.innerText || item.textContent || '').trim().toUpperCase();
        
        if (texto.includes('FACTURACIÓN') && texto.includes('ELECTRÓNICA')) {
            // Verificar si ya está expandido
            const parentLi = item.parentElement;
            if (!parentLi.classList.contains('open')) {
                // Hacer clic para expandir
                item.click();
                return {encontrado: true, texto: texto, accion: 'expandido'};
            } else {
                return {encontrado: true, texto: texto, accion: 'ya_expandido'};
            }
        }
    }
    
    return {encontrado: false, error: 'No se encontró Facturación electrónica'};
    """
    
    resultado = driver.execute_script(script_facturacion)
    if resultado.get('encontrado'):
        print(f"   ✅ {resultado.get('texto')} ({resultado.get('accion')})")
        time.sleep(3)
    else:
        print(f"   ❌ {resultado.get('error')}")
    
    guardar_html(driver, "debug_despues_facturacion")
    
    # 4. Hacer clic en "Producción" expandiendo el submenú
    print("\n4. Expandiendo 'Producción'...")
    script_produccion = """
    const cssmenu = document.querySelector('#cssmenu');
    if (!cssmenu) {
        return {encontrado: false, error: 'No se encontró #cssmenu'};
    }
    
    // Buscar dentro de Facturación Electrónica
    const facturacionLi = Array.from(cssmenu.querySelectorAll('li.has-sub')).find(li => {
        const texto = (li.innerText || li.textContent || '').toUpperCase();
        return texto.includes('FACTURACIÓN') && texto.includes('ELECTRÓNICA');
    });
    
    if (!facturacionLi) {
        return {encontrado: false, error: 'No se encontró Facturación Electrónica expandida'};
    }
    
    // Buscar Producción dentro del submenú de Facturación Electrónica
    const submenus = facturacionLi.querySelectorAll('ul li');
    
    for (let item of submenus) {
        const enlace = item.querySelector('a');
        if (!enlace) continue;
        
        const texto = (enlace.innerText || enlace.textContent || '').trim();
        if (texto.toUpperCase() === 'PRODUCCIÓN' || texto.toUpperCase() === 'PRODUCCION') {
            // Hacer clic para expandir si tiene submenú
            if (item.classList.contains('has-sub') && !item.classList.contains('open')) {
                enlace.click();
                return {encontrado: true, texto: texto, accion: 'expandido'};
            }
            return {encontrado: true, texto: texto, accion: 'ya_expandido'};
        }
    }
    
    return {encontrado: false, error: 'No se encontró Producción'};
    """
    
    resultado = driver.execute_script(script_produccion)
    if resultado.get('encontrado'):
        print(f"   ✅ {resultado.get('texto')} ({resultado.get('accion')})")
        time.sleep(3)
    else:
        print(f"   ❌ {resultado.get('error')}")
    
    guardar_html(driver, "debug_despues_produccion")
    
    # 5. Hacer clic en "Consultas" para navegar a la página de consultas
    print("\n5. Navegando a 'Consultas'...")
    script_consultas = """
    const cssmenu = document.querySelector('#cssmenu');
    if (!cssmenu) {
        return {encontrado: false, error: 'No se encontró #cssmenu'};
    }
    
    // Buscar el enlace de Consultas (que navega a una página, no expande)
    const enlaces = cssmenu.querySelectorAll('a');
    
    for (let enlace of enlaces) {
        const texto = (enlace.innerText || enlace.textContent || '').trim();
        if (texto.toUpperCase() === 'CONSULTAS') {
            // Hacer clic en el enlace
            enlace.click();
            return {encontrado: true, texto: texto, href: enlace.href || 'sin-href'};
        }
    }
    
    // Si no se encuentra exacto, buscar parcial
    for (let enlace of enlaces) {
        const texto = (enlace.innerText || enlace.textContent || '').trim().toUpperCase();
        if (texto === 'CONSULTAS') {
            enlace.click();
            return {encontrado: true, texto: 'CONSULTAS', metodo: 'parcial'};
        }
    }
    
    return {encontrado: false, error: 'No se encontró el enlace de Consultas'};
    """
    
    resultado = driver.execute_script(script_consultas)
    if resultado.get('encontrado'):
        print(f"   ✅ Navegando a: {resultado.get('texto')}")
        if resultado.get('href'):
            print(f"      URL: {resultado.get('href')}")
    else:
        print(f"   ❌ {resultado.get('error')}")
        raise Exception("No se pudo navegar a Consultas")
    
    # 6. Esperar a que cargue la página de consultas
    print("\n6. Esperando que cargue la página de Consultas...")
    time.sleep(8)  # Esperar suficiente tiempo para que cargue la página
    guardar_html(driver, "debug_pagina_consultas")
    
    # 7. Buscar y hacer clic en "Comprobantes electrónicos emitidos" en la página cargada
    print("\n7. Buscando 'Comprobantes electrónicos emitidos' en la página...")
    
    try:
        # Buscar el enlace específico
        enlace_emitidos = driver.execute_script("""
            const enlaces = document.querySelectorAll('a');
            for (let enlace of enlaces) {
                const texto = (enlace.innerText || enlace.textContent || '').trim();
                if (texto.toUpperCase().includes('COMPROBANTES ELECTRÓNICOS EMITIDOS') || 
                    texto.toUpperCase().includes('COMPROBANTES ELECTRONICOS EMITIDOS')) {
                    return {
                        encontrado: true,
                        texto: texto,
                        onclick: enlace.getAttribute('onclick')
                    };
                }
            }
            return {encontrado: false};
        """)
        
        if enlace_emitidos.get('encontrado'):
            print(f"   ✅ Encontrado: {enlace_emitidos.get('texto')}")
            
            # Si tiene onclick con mojarra, ejecutarlo
            onclick = enlace_emitidos.get('onclick', '')
            if onclick and 'mojarra.jsfcljs' in onclick:
                print("   Ejecutando onclick JSF...")
                driver.execute_script(onclick)
            else:
                # Hacer clic normal
                driver.execute_script("""
                    const enlaces = document.querySelectorAll('a');
                    for (let enlace of enlaces) {
                        const texto = (enlace.innerText || '').trim();
                        if (texto.toUpperCase().includes('COMPROBANTES ELECTRÓNICOS EMITIDOS') || 
                            texto.toUpperCase().includes('COMPROBANTES ELECTRONICOS EMITIDOS')) {
                            enlace.click();
                            break;
                        }
                    }
                """)
            
            print("   ⏳ Esperando a que cargue la página de emitidos...")
            time.sleep(6)
            guardar_html(driver, "menu_emitidas_nuevo")
            print("   ✅ Navegación completada")
        else:
            # Buscar coincidencias para debug
            coincidencias = driver.execute_script("""
                const enlaces = document.querySelectorAll('a');
                let coincidencias = [];
                for (let el of enlaces) {
                    const texto = (el.innerText || '').trim();
                    if (texto.toUpperCase().includes('EMITIDOS') && texto.length < 60) {
                        coincidencias.push(texto);
                    }
                }
                return coincidencias.slice(0, 10);
            """)
            print(f"   ❌ No se encontró 'Comprobantes electrónicos emitidos'")
            if coincidencias:
                print(f"   Opciones con 'EMITIDOS': {coincidencias}")
            raise Exception("No se pudo encontrar el enlace")
            
    except Exception as e:
        print(f"   ❌ Error al navegar: {str(e)}")
        raise Exception("No se pudo navegar a Comprobantes electrónicos emitidos")


def detectar_tipo_pagina(driver):
    """Detecta si estamos en la página de recibidos o emitidos"""
    try:
        titulo = driver.execute_script("""
            const titulo = document.querySelector('#tituloPagina, .sri-textoTitulo');
            return titulo ? titulo.innerText : '';
        """)
        
        if 'emitidos' in titulo.lower():
            return 'emitidos'
        elif 'recibidos' in titulo.lower():
            return 'recibidos'
        else:
            # Verificar por URL
            url = driver.current_url
            if 'emitidos' in url.lower():
                return 'emitidos'
            elif 'recibidos' in url.lower():
                return 'recibidos'
            return 'desconocido'
    except:
        return 'desconocido'


def presionar_boton_consultar(driver):
    """Presiona el botón de consultar y maneja el reCAPTCHA"""
    try:
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
        
        return boton_encontrado
        
    except Exception as e:
        print(f"❌ Error al presionar botón: {str(e)}")
        return False


def filtrar_fechas_emitidos(driver, desde, hasta, directorio_descarga=None):
    """Filtra comprobantes emitidos por fecha"""
    print(f"\nFiltrando EMITIDOS desde: {desde} hasta: {hasta}")
    
    # Usar directorio por defecto si no se especifica
    if not directorio_descarga:
        directorio_descarga = "facturas_xml/emitidas"
    
    try:
        time.sleep(3)
        
        desde_partes = desde.split('/')
        desde_anio = desde_partes[2]
        desde_mes = desde_partes[1].zfill(2)  # Asegurar 2 dígitos
        desde_dia = desde_partes[0].zfill(2)  # Asegurar 2 dígitos
        
        fecha_formateada = f"{desde_dia}/{desde_mes}/{desde_anio}"
        print(f"Configurando fecha de emisión: {fecha_formateada}")
        
        # Script para llenar el campo de fecha y activar el formulario en emitidos
        script_fecha = f"""
        const resultado = {{}};
        
        // 1. Verificar que el radio button de RUC esté seleccionado
        const radioRuc = document.getElementById('frmPrincipal:opciones:0');
        if (radioRuc && !radioRuc.checked) {{
            radioRuc.click();
            resultado.radioRuc = true;
        }}
        
        // 2. "Tocar" el campo de RUC para activar el formulario
        const inputRuc = document.getElementById('frmPrincipal:txtParametro');
        if (inputRuc) {{
            const valorOriginal = inputRuc.value;
            inputRuc.value = valorOriginal + ' ';
            inputRuc.dispatchEvent(new Event('input', {{ bubbles: true }}));
            setTimeout(() => {{
                inputRuc.value = valorOriginal;
                inputRuc.dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputRuc.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}, 100);
            resultado.ruc = true;
        }}
        
        // 3. Configurar fecha usando jQuery UI Datepicker
        const inputFecha = document.getElementById('frmPrincipal:calendarFechaDesde_input');
        
        if (inputFecha) {{
            // Usar jQuery para configurar la fecha del datepicker
            if (typeof jQuery !== 'undefined' && jQuery(inputFecha).datepicker) {{
                jQuery(inputFecha).datepicker('setDate', '{fecha_formateada}');
                resultado.fecha = true;
                resultado.metodo = 'datepicker';
                console.log('Fecha configurada con datepicker:', inputFecha.value);
            }} else {{
                // Fallback: cambiar valor directamente
                inputFecha.value = '{fecha_formateada}';
                inputFecha.dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputFecha.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                // Intentar disparar evento de PrimeFaces
                if (typeof PrimeFaces !== 'undefined') {{
                    PrimeFaces.csp.trigger(inputFecha, 'input');
                    PrimeFaces.csp.trigger(inputFecha, 'change');
                }}
                
                resultado.fecha = true;
                resultado.metodo = 'directo_con_primefaces';
                console.log('Fecha configurada directamente:', inputFecha.value);
            }}
        }}
        
        return resultado;
        """
        
        resultado = driver.execute_script(script_fecha)
        print(f"Campos configurados: {resultado}")
        
        if resultado.get('fecha'):
            print(f"✅ Fecha configurada correctamente ({resultado.get('metodo')})")
        else:
            print("⚠️ No se pudo configurar la fecha")
        
        time.sleep(5)  # Esperar más tiempo para que el formulario se actualice completamente
        
        # Verificar que la fecha se haya configurado correctamente
        fecha_actual = driver.execute_script("""
            const input = document.getElementById('frmPrincipal:calendarFechaDesde_input');
            return input ? input.value : 'no encontrado';
        """)
        print(f"   Fecha actual en el campo: {fecha_actual}")
        
        # Presionar botón de consultar para EMITIDOS
        print("\n🖱️ Presionando botón Consultar para EMITIDOS...")
        
        # Usar JavaScript para hacer clic (más confiable para PrimeFaces)
        try:
            resultado_click = driver.execute_script("""
                const btn = document.getElementById('frmPrincipal:btnConsultar');
                if (btn) {
                    // Simular el evento de clic completo
                    const clickEvent = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    btn.dispatchEvent(clickEvent);
                    return {exito: true, metodo: 'js_event'};
                }
                return {exito: false};
            """)
            
            if resultado_click.get('exito'):
                print(f"   ✅ Botón presionado ({resultado_click.get('metodo')})")
            else:
                # Fallback a Selenium
                btn_consultar = driver.find_element(By.ID, "frmPrincipal:btnConsultar")
                btn_consultar.click()
                print("   ✅ Botón presionado (Selenium)")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            presionar_boton_consultar(driver)
        
        # Esperar más tiempo para la respuesta AJAX de PrimeFaces
        print("\n⏳ Esperando respuesta del servidor (10 segundos)...")
        time.sleep(10)
        
        # Verificar URL después de consultar
        url_despues = driver.current_url
        print(f"\n📍 URL después de consultar: {url_despues}")
        
        # Si no estamos en la página de resultados, intentar nuevamente
        if 'menu.jsf' in url_despues:
            print("\n⚠️ Redirigido al menú. El formulario no se procesó correctamente.")
            print("   Esto puede deberse a:")
            print("   - Validación del formulario")
            print("   - Protección anti-bot del sitio")
            print("   - Timeout de sesión")
            print("\n💡 RECOMENDACIÓN: Descargar comprobantes emitidos manualmente")
            print("   y colocar el archivo en: facturas_xml/emitidas/")
            return False
        
        # Guardar HTML para debug
        from guardar_html import guardar_html
        guardar_html(driver, "debug_despues_consultar_emitidos")
        
        # Después de filtrar, descargar el reporte (igual que en recibidos)
        print("\n📥 Descargando reporte...")
        descargar_reporte_txt(driver, directorio_descarga)
        
        return True
        
    except Exception as e:
        print(f"❌ Error al filtrar emitidos: {str(e)}")
        return False


def filtrar_fechas(driver, desde, hasta, ruc=None, directorio_descarga=None):
    """Filtra facturas por rango de fechas y descarga el reporte"""
    wait = WebDriverWait(driver, 20)
    
    # Detectar tipo de página
    tipo_pagina = detectar_tipo_pagina(driver)
    print(f"\nTipo de página detectada: {tipo_pagina}")
    
    # Si es emitidos, usar función específica
    if tipo_pagina == 'emitidos':
        return filtrar_fechas_emitidos(driver, desde, hasta, directorio_descarga)
    
    # Si es recibidos, continuar con el código existente
    try:
        time.sleep(3)
        print(f"Filtrando RECIBIDOS desde: {desde} hasta: {hasta}")
        
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
        
        # Presionar botón de consultar
        presionar_boton_consultar(driver)
        
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
