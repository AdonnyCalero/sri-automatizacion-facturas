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


def filtrar_fechas(driver, desde, hasta):
    """
    Filtra las facturas por rango de fechas usando los selects de Periodos de emisión
    Formato esperado de fechas: DD/MM/AAAA
    """
    wait = WebDriverWait(driver, 20)
    
    try:
        time.sleep(3)
        
        # Parsear fechas DD/MM/AAAA -> año, mes
        desde_partes = desde.split('/')
        hasta_partes = hasta.split('/')
        
        desde_anio = desde_partes[2]
        desde_mes = desde_partes[1]
        hasta_anio = hasta_partes[2]
        hasta_mes = hasta_partes[1]
        
        print(f"Filtrando desde: {desde} hasta: {hasta}")
        
        # Script para seleccionar los valores en los selects
        script_fechas = f"""
        function setSelectValue(selectText, value) {{
            const selects = document.querySelectorAll('select');
            for (let select of selects) {{
                // Buscar por label cercano o texto del select
                const parent = select.closest('div, td, label');
                const parentText = parent ? (parent.innerText || parent.textContent || '') : '';
                const selectLabel = select.getAttribute('aria-label') || '';
                
                if (parentText.toLowerCase().includes(selectText.toLowerCase()) || 
                    selectLabel.toLowerCase().includes(selectText.toLowerCase())) {{
                    for (let option of select.options) {{
                        if (option.value === value || option.text === value) {{
                            select.value = option.value;
                            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                    }}
                }}
            }}
            return false;
        }}
        
        // Intentar encontrar y seleccionar los selects
        const resultado = {{}};
        
        // Buscar todos los selects primero para identificarlos
        const allSelects = document.querySelectorAll('select');
        console.log('Selects encontrados:', allSelects.length);
        
        // Estrategia 1: Seleccionar por posición (asumiendo: año, mes, día/todos)
        if (allSelects.length >= 3) {{
            // Select 0: Año desde
            for (let option of allSelects[0].options) {{
                if (option.value === '{desde_anio}' || option.text === '{desde_anio}') {{
                    allSelects[0].value = option.value;
                    allSelects[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    resultado.anioDesde = true;
                    break;
                }}
            }}
            
            // Select 1: Mes desde
            for (let option of allSelects[1].options) {{
                if (option.value === '{desde_mes}' || option.text === '{desde_mes}' || 
                    option.value === '{int(desde_mes)}' || option.text.includes('{desde_mes}')) {{
                    allSelects[1].value = option.value;
                    allSelects[1].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    resultado.mesDesde = true;
                    break;
                }}
            }}
            
            // Select 2: Día/Todos - seleccionar "Todos"
            for (let option of allSelects[2].options) {{
                if (option.text.toUpperCase().includes('TODOS') || option.value === '0' || option.value === '') {{
                    allSelects[2].value = option.value;
                    allSelects[2].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    resultado.diaDesde = true;
                    break;
                }}
            }}
        }}
        
        return resultado;
        """
        
        resultado = driver.execute_script(script_fechas)
        print(f"Selects configurados: {resultado}")
        
        time.sleep(2)
        
        # Buscar y hacer clic en el botón de consultar
        script_boton = """
        const botones = document.querySelectorAll('button, input[type="submit"], a');
        for (let btn of botones) {
            const texto = (btn.textContent || btn.value || '').toLowerCase();
            if (texto.includes('consultar') || 
                texto.includes('buscar') ||
                texto.includes('filtrar') ||
                btn.className.toLowerCase().includes('consultar')) {
                btn.click();
                return true;
            }
        }
        // Buscar por icono o clase específica
        const btnConsultar = document.querySelector('.ui-button, .btn-consultar, [id*="consultar"], [id*="Consultar"]');
        if (btnConsultar) {
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
        
        # Esperar a que carguen los resultados
        time.sleep(5)
        
    except Exception as e:
        print(f"⚠️ Error al filtrar fechas: {e}")
        import traceback
        traceback.print_exc()


def descargar_documentos(driver, descargar_xml=True, descargar_pdf=True):
    """
    Descarga los archivos XML y/o PDF de las facturas mostradas en la tabla
    Las columnas son: Documento (XML) y RIDE (PDF)
    """
    wait = WebDriverWait(driver, 20)
    total_xml = 0
    total_pdf = 0
    pagina = 1
    
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
                if (texto.includes('DOCUMENTO')) colDocumento = index;
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
                    script_xml = f"""
                    const tablas = document.querySelectorAll('table');
                    let tabla = null;
                    for (let t of tablas) {{
                        const encabezados = t.querySelectorAll('th');
                        for (let th of encabezados) {{
                            if ((th.innerText || '').toUpperCase().includes('DOCUMENTO')) {{
                                tabla = t;
                                break;
                            }}
                        }}
                        if (tabla) break;
                    }}
                    
                    if (!tabla) tabla = document.querySelector('.ui-datatable-table, .ui-table');
                    
                    if (tabla) {{
                        const filas = [...tabla.querySelectorAll('tbody tr, tr')].filter(f => f.querySelectorAll('td').length > 2);
                        if (filas[{i}]) {{
                            const celdas = filas[{i}].querySelectorAll('td');
                            const celdaDocumento = celdas[{info_tabla['colDocumento']}];
                            if (celdaDocumento) {{
                                // Buscar icono/enlace en la celda
                                const icono = celdaDocumento.querySelector('a, button, img, i, span');
                                if (icono) {{
                                    icono.click();
                                    return true;
                                }}
                            }}
                        }}
                    }}
                    return false;
                    """
                    
                    resultado = driver.execute_script(script_xml)
                    if resultado:
                        total_xml += 1
                        time.sleep(1.5)  # Esperar descarga
                
                # Descargar PDF (columna RIDE)
                if descargar_pdf and info_tabla['colRide'] >= 0:
                    script_pdf = f"""
                    const tablas = document.querySelectorAll('table');
                    let tabla = null;
                    for (let t of tablas) {{
                        const encabezados = t.querySelectorAll('th');
                        for (let th of encabezados) {{
                            if ((th.innerText || '').toUpperCase().includes('RIDE')) {{
                                tabla = t;
                                break;
                            }}
                        }}
                        if (tabla) break;
                    }}
                    
                    if (!tabla) tabla = document.querySelector('.ui-datatable-table, .ui-table');
                    
                    if (tabla) {{
                        const filas = [...tabla.querySelectorAll('tbody tr, tr')].filter(f => f.querySelectorAll('td').length > 2);
                        if (filas[{i}]) {{
                            const celdas = filas[{i}].querySelectorAll('td');
                            const celdaRide = celdas[{info_tabla['colRide']}];
                            if (celdaRide) {{
                                // Buscar icono/enlace en la celda
                                const icono = celdaRide.querySelector('a, button, img, i, span');
                                if (icono) {{
                                    icono.click();
                                    return true;
                                }}
                            }}
                        }}
                    }}
                    return false;
                    """
                    
                    resultado = driver.execute_script(script_pdf)
                    if resultado:
                        total_pdf += 1
                        time.sleep(1.5)  # Esperar descarga
                
                # Progreso cada 5 documentos
                if (total_xml + total_pdf) % 5 == 0:
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
    return {'xml': total_xml, 'pdf': total_pdf}


# Función legacy para mantener compatibilidad
def descargar_xmls(driver):
    """
    Función legacy - ahora usa descargar_documentos
    """
    resultado = descargar_documentos(driver, descargar_xml=True, descargar_pdf=False)
    return resultado['xml']
