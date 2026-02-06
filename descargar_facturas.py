from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import requests
from urllib.parse import urljoin, urlparse
from guardar_html import guardar_html


def descargar_archivo_con_sesion(driver, url, directorio, nombre_archivo=None):
    """
    Descarga un archivo usando las cookies de sesión del driver de Selenium
    """
    try:
        # Obtener cookies del driver
        cookies = driver.get_cookies()
        
        # Crear sesión de requests
        session = requests.Session()
        
        # Agregar cookies a la sesión
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        # Headers para simular navegador
        headers = {
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': driver.current_url
        }
        
        # Descargar archivo
        response = session.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Si no se proporcionó nombre, intentar obtenerlo del Content-Disposition
        if not nombre_archivo:
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                nombre_archivo = content_disposition.split('filename=')[1].strip('"\'')
            else:
                # Usar el nombre de la URL
                nombre_archivo = os.path.basename(urlparse(url).path) or 'archivo_descargado'
        
        # Asegurar extensión
        if not nombre_archivo.endswith(('.xml', '.pdf')):
            content_type = response.headers.get('Content-Type', '')
            if 'xml' in content_type:
                nombre_archivo += '.xml'
            elif 'pdf' in content_type:
                nombre_archivo += '.pdf'
        
        # Guardar archivo
        ruta_completa = os.path.join(directorio, nombre_archivo)
        
        # Si el archivo ya existe, agregar número
        contador = 1
        nombre_base, extension = os.path.splitext(ruta_completa)
        while os.path.exists(ruta_completa):
            ruta_completa = f"{nombre_base}_{contador}{extension}"
            contador += 1
        
        with open(ruta_completa, 'wb') as f:
            f.write(response.content)
        
        print(f"   ✓ Descargado: {os.path.basename(ruta_completa)}")
        return True
        
    except Exception as e:
        print(f"   ✗ Error descargando {url}: {str(e)[:50]}")
        return False


def verificar_descarga(directorio, timeout=10):
    """
    Espera a que aparezca un nuevo archivo en el directorio de descargas
    Retorna True si se detecta un nuevo archivo, False en caso contrario
    """
    tiempo_inicio = time.time()
    archivos_antes = set(os.listdir(directorio)) if os.path.exists(directorio) else set()
    
    while time.time() - tiempo_inicio < timeout:
        time.sleep(0.5)
        if os.path.exists(directorio):
            archivos_despues = set(os.listdir(directorio))
            archivos_nuevos = archivos_despues - archivos_antes
            # Filtrar archivos temporales de descarga (.crdownload, .tmp)
            archivos_nuevos = [f for f in archivos_nuevos if not f.endswith(('.crdownload', '.tmp'))]
            if archivos_nuevos:
                return True
    return False


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


def ir_a_comprobantes(driver, tipo):
    if tipo == "RECIBIDAS":
        submenu_texto = "Comprobantes electrónicos recibidos"
    else:
        submenu_texto = "Comprobantes electrónicos emitidos"

    # 1. Abrir el menú hamburguesa primero
    print("Abriendo menú hamburguesa...")
    script_menu = """
    const menuBtn = document.getElementById('sri-menu');
    if (menuBtn) {
        menuBtn.click();
        return true;
    }
    // Buscar por clase alternativa
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
        time.sleep(3)  # Esperar a que se abra el menú
    else:
        print("⚠️ No se pudo abrir el menú, intentando continuar...")

    # 2. Buscar y hacer clic en "FACTURACIÓN ELECTRÓNICA"
    print("Buscando FACTURACIÓN ELECTRÓNICA...")
    script_facturacion = """
    // Buscar el texto "FACTURACIÓN ELECTRÓNICA" o "Facturación Electrónica"
    const elementos = [...document.querySelectorAll('span, a, div, li')];
    const facturacion = elementos.find(el => {
        const texto = el.innerText || el.textContent || '';
        return texto.toUpperCase().includes('FACTURACIÓN ELECTRÓNICA');
    });
    
    if (facturacion) {
        // Si tiene un padre clickable, hacer clic en el padre
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
        // Si no encontramos clickable, hacer clic directo
        facturacion.click();
        return true;
    }
    return false;
    """
    
    facturacion_encontrada = driver.execute_script(script_facturacion)
    if facturacion_encontrada:
        print("✅ FACTURACIÓN ELECTRÓNICA desplegada")
        time.sleep(2)  # Esperar a que se despliegue el submenú
    else:
        print("⚠️ No se encontró FACTURACIÓN ELECTRÓNICA")

    # 3. Buscar y hacer clic en el submenú correspondiente
    print(f"Buscando submenú: {submenu_texto}...")
    script = f"""
    // Buscar en spans
    const spans = [...document.querySelectorAll('span')];
    const target = spans.find(s => s.innerText.includes('{submenu_texto}'));
    if (target) {{
        target.click();
        return true;
    }}
    
    // Buscar en enlaces <a>
    const links = [...document.querySelectorAll('a')];
    const linkTarget = links.find(a => a.innerText.includes('{submenu_texto}'));
    if (linkTarget) {{
        linkTarget.click();
        return true;
    }}
    
    // Buscar en elementos con clase de menú
    const menuItems = [...document.querySelectorAll('.w3-bar-item, .menu-item, .ui-menuitem, .ui-panelmenu-content')];
    const menuTarget = menuItems.find(item => item.innerText.includes('{submenu_texto}'));
    if (menuTarget) {{
        menuTarget.click();
        return true;
    }}
    
    // Buscar texto parcial
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
    """
    Filtra las facturas por rango de fechas usando los campos del formulario
    Formato esperado de fechas: DD/MM/AAAA
    """
    wait = WebDriverWait(driver, 20)
    
    try:
        time.sleep(3)
        
        print(f"Filtrando desde: {desde} hasta: {hasta}")
        
        # Parsear fechas DD/MM/AAAA -> año, mes
        desde_partes = desde.split('/')
        desde_anio = desde_partes[2]
        desde_mes = desde_partes[1]
        
        # Función para obtener texto del mes
        def obtener_nombre_mes(numero_mes):
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            return meses[int(numero_mes) - 1] if numero_mes.isdigit() else meses[0]
        
        mes_nombre = obtener_nombre_mes(desde_mes)
        print(f"Configurando fecha: {desde_anio} - {mes_nombre} - Todos")
        
        # Script simplificado para seleccionar por posición
        script_formulario = f"""
        const resultado = {{}};
        
        // 1. Llenar campo RUC si se proporcionó
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
        
        // 2. Seleccionar los 3 selects de período por posición
        const allSelects = document.querySelectorAll('select');
        console.log('Total de selects encontrados:', allSelects.length);
        
        // Buscar selects relacionados con período de emisión
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
        
        // Si no encontramos por texto, usamos los primeros 3 selects
        if (periodoSelects.length === 0) {{
            periodoSelects = Array.from(allSelects).slice(0, 3);
        }}
        
        // Select 1: Año
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
        
        // Select 2: Mes
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
        
        // Select 3: Todos
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
        
        // 3. Seleccionar tipo de comprobante (Factura)
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
        
        # Esperar un momento para que el reCAPTCHA cargue
        print("⏳ Esperando a que el reCAPTCHA esté listo...")
        time.sleep(3)
        
        # Buscar y hacer clic en el botón de consultar
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
                // Verificar que el botón esté visible y habilitado
                if (btn.offsetParent !== null && !btn.disabled) {
                    console.log('Botón encontrado:', btn);
                    btn.click();
                    return true;
                }
            }
        }
        
        // Buscar por ID o clases específicas
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
            print("📝 Puede ser necesario resolver el reCAPTCHA manualmente")
        
        # Esperar a que carguen los resultados o a que se pueda resolver el reCAPTCHA
        time.sleep(5)
        
        # Verificar si hay un reCAPTCHA que requiere atención
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
        
    except Exception as e:
        print(f"⚠️ Error al filtrar fechas: {e}")
        import traceback
        traceback.print_exc()


def extraer_urls_descarga(driver, fila_idx, col_idx):
    """
    Extrae las URLs de descarga de una fila específica
    """
    script = f"""
    const tablas = document.querySelectorAll('table');
    let tabla = null;
    for (let t of tablas) {{
        const encabezados = t.querySelectorAll('th');
        for (let th of encabezados) {{
            const texto = (th.innerText || '').toUpperCase();
            if (texto.includes('DOCUMENTO') || texto.includes('RIDE')) {{
                tabla = t;
                break;
            }}
        }}
        if (tabla) break;
    }}
    
    if (!tabla) tabla = document.querySelector('.ui-datatable-table, .ui-table');
    
    if (tabla) {{
        const filas = [...tabla.querySelectorAll('tbody tr, tr')].filter(f => f.querySelectorAll('td').length > 2);
        if (filas[{fila_idx}]) {{
            const celdas = filas[{fila_idx}].querySelectorAll('td');
            const celda = celdas[{col_idx}];
            if (celda) {{
                const enlaces = celda.querySelectorAll('a');
                const urls = [];
                for (let enlace of enlaces) {{
                    let url = enlace.getAttribute('href') || '';
                    const onclick = enlace.getAttribute('onclick') || '';
                    
                    // Si no hay href, intentar extraer de onclick
                    if (!url && onclick) {{
                        // Buscar patrones como: window.open('url'), location.href='url', etc.
                        const match = onclick.match(/['"`]([^'"`]*\.(?:xml|pdf))['"`]/i);
                        if (match) url = match[1];
                    }}
                    
                    if (url) {{
                        urls.push({{
                            url: url,
                            title: enlace.title || '',
                            text: enlace.textContent || ''
                        }});
                    }}
                }}
                return urls;
            }}
        }}
    }}
    return [];
    """
    return driver.execute_script(script)


def descargar_documentos(driver, descargar_xml=True, descargar_pdf=True, directorio_descarga=None):
    """
    Descarga los archivos XML y/o PDF de las facturas mostradas en la tabla
    Usa requests con las cookies de sesión para evitar errores de descarga
    """
    wait = WebDriverWait(driver, 20)
    total_xml = 0
    total_pdf = 0
    total_xml_fallidos = 0
    total_pdf_fallidos = 0
    pagina = 1
    
    # Obtener directorio de descarga actual del driver
    if not directorio_descarga:
        directorio_descarga = "facturas_xml/recibidas"  # Default
    
    # Asegurar que el directorio existe
    os.makedirs(directorio_descarga, exist_ok=True)
    
    while True:
        print(f"📄 Procesando página {pagina}...")
        time.sleep(3)
        
        try:
            # Encontrar todas las filas de la tabla
            script_filas = """
            // Buscar la tabla principal
            const tablas = document.querySelectorAll('table');
            let tablaPrincipal = null;
            
            for (let tabla of tablas) {
                // Buscar tabla que tenga encabezados Documento o RIDE
                const encabezados = tabla.querySelectorAll('th, td');
                for (let th of encabezados) {
                    const texto = (th.innerText || th.textContent || '').toUpperCase();
                    if (texto.includes('DOCUMENTO') || texto.includes('RIDE')) {
                        tablaPrincipal = tabla;
                        break;
                    }
                }
                if (tablaPrincipal) break;
            }
            
            if (!tablaPrincipal) {
                // Intentar con clases comunes de PrimeFaces
                tablaPrincipal = document.querySelector('.ui-datatable-table, .ui-table, .data-table');
            }
            
            if (!tablaPrincipal) return { filas: 0, encabezados: [] };
            
            // Obtener índices de columnas
            const encabezados = tablaPrincipal.querySelectorAll('th');
            let colDocumento = -1;
            let colRide = -1;
            
            encabezados.forEach((th, index) => {
                const texto = (th.innerText || th.textContent || '').toUpperCase();
                // Buscar DOCUMENTO pero excluir DOCUMENTOS RELACIONADOS
                if (texto.includes('DOCUMENTO') && !texto.includes('RELACIONADOS')) colDocumento = index;
                if (texto.includes('RIDE')) colRide = index;
            });
            
            // Contar filas de datos (excluyendo encabezado)
            const filas = tablaPrincipal.querySelectorAll('tbody tr, tr');
            const filasDatos = [...filas].filter(fila => {
                const celdas = fila.querySelectorAll('td');
                return celdas.length > 2; // Es una fila de datos, no encabezado
            });
            
            return {
                filas: filasDatos.length,
                colDocumento: colDocumento,
                colRide: colRide
            };
            """
            
            info_tabla = driver.execute_script(script_filas)
            print(f"   Filas encontradas: {info_tabla['filas']}, Col Documento: {info_tabla['colDocumento']}, Col RIDE: {info_tabla['colRide']}")
            
            if info_tabla['filas'] == 0:
                print("   No hay más facturas para descargar")
                break
            
            # Descargar documentos fila por fila
            for i in range(info_tabla['filas']):
                # Descargar XML (columna Documento)
                if descargar_xml and info_tabla['colDocumento'] >= 0:
                    urls_xml = extraer_urls_descarga(driver, i, info_tabla['colDocumento'])
                    
                    # Buscar URL que parezca ser XML
                    url_xml = None
                    for url_info in urls_xml:
                        if 'xml' in url_info['url'].lower() or 'xml' in url_info['title'].lower():
                            url_xml = url_info['url']
                            break
                    # Si no encontramos específicamente XML, usar la primera URL
                    if not url_xml and urls_xml:
                        url_xml = urls_xml[0]['url']
                    
                    if url_xml:
                        # Completar URL si es relativa
                        if not url_xml.startswith('http'):
                            url_xml = urljoin(driver.current_url, url_xml)
                        
                        # Descargar usando sesión
                        if descargar_archivo_con_sesion(driver, url_xml, directorio_descarga, f"factura_{pagina}_{i+1}.xml"):
                            total_xml += 1
                        else:
                            total_xml_fallidos += 1
                            print(f"   ⚠️ XML fila {i+1} no se descargó correctamente")
                    else:
                        total_xml_fallidos += 1
                        print(f"   ⚠️ No se encontró URL de XML en fila {i+1}")
                    
                    time.sleep(1)  # Pausa entre descargas
                
                # Descargar PDF (columna RIDE)
                if descargar_pdf and info_tabla['colRide'] >= 0:
                    urls_pdf = extraer_urls_descarga(driver, i, info_tabla['colRide'])
                    
                    # Buscar URL que parezca ser PDF/RIDE
                    url_pdf = None
                    for url_info in urls_pdf:
                        if any(x in url_info['url'].lower() for x in ['pdf', 'ride']) or \
                           any(x in url_info['title'].lower() for x in ['pdf', 'ride']):
                            url_pdf = url_info['url']
                            break
                    # Si no encontramos específicamente PDF, usar la primera URL
                    if not url_pdf and urls_pdf:
                        url_pdf = urls_pdf[0]['url']
                    
                    if url_pdf:
                        # Completar URL si es relativa
                        if not url_pdf.startswith('http'):
                            url_pdf = urljoin(driver.current_url, url_pdf)
                        
                        # Descargar usando sesión
                        if descargar_archivo_con_sesion(driver, url_pdf, directorio_descarga, f"factura_{pagina}_{i+1}.pdf"):
                            total_pdf += 1
                        else:
                            total_pdf_fallidos += 1
                            print(f"   ⚠️ PDF fila {i+1} no se descargó correctamente")
                    else:
                        total_pdf_fallidos += 1
                        print(f"   ⚠️ No se encontró URL de PDF en fila {i+1}")
                    
                    time.sleep(1)  # Pausa entre descargas
                
                # Progreso cada 5 documentos
                if (total_xml + total_pdf) % 5 == 0 and (total_xml + total_pdf) > 0:
                    print(f"   Progreso - XMLs: {total_xml}, PDFs: {total_pdf}")
            
            # Verificar si hay siguiente página
            script_siguiente = """
            // Buscar botón de siguiente página
            const botonesPagina = document.querySelectorAll('button, a, span');
            for (let btn of botonesPagina) {
                const texto = (btn.textContent || '').toLowerCase();
                if ((texto.includes('>') || texto.includes('siguiente') || 
                     texto.includes('next') || texto.includes('»')) && 
                     !btn.disabled && !btn.className.includes('disabled')) {
                    btn.click();
                    return true;
                }
            }
            // Buscar por clase común de paginación PrimeFaces
            const nextBtn = document.querySelector('.ui-paginator-next:not(.ui-state-disabled)');
            if (nextBtn) {
                nextBtn.click();
                return true;
            }
            // Buscar por icono de flecha
            const nextIcon = document.querySelector('.ui-icon-seek-next, .fa-forward, .fa-step-forward');
            if (nextIcon) {
                nextIcon.click();
                return true;
            }
            return false;
            """
            
            hay_siguiente = driver.execute_script(script_siguiente)
            
            if not hay_siguiente:
                print("   No hay más páginas")
                break
            
            pagina += 1
            time.sleep(3)
            
        except Exception as e:
            print(f"⚠️ Error al descargar documentos: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print(f"✅ Descarga completada - XMLs: {total_xml}, PDFs: {total_pdf}")
    if total_xml_fallidos > 0 or total_pdf_fallidos > 0:
        print(f"❌ Fallidos - XMLs: {total_xml_fallidos}, PDFs: {total_pdf_fallidos}")
    return {'xml': total_xml, 'pdf': total_pdf}


# Función legacy para mantener compatibilidad
def descargar_xmls(driver):
    """
    Función legacy - ahora usa descargar_documentos
    """
    resultado = descargar_documentos(driver, descargar_xml=True, descargar_pdf=False)
    return resultado['xml']
