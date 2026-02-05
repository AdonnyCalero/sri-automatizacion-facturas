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
    Filtra las facturas por rango de fechas en el SRI
    """
    wait = WebDriverWait(driver, 20)
    
    try:
        # Esperar a que los campos de fecha estén disponibles
        # Los IDs pueden variar, se usan selectores flexibles
        time.sleep(3)
        
        # Buscar campos de fecha usando JavaScript para mayor flexibilidad
        script_fechas = f"""
        // Función para encontrar input de fecha por placeholder o label
        function findDateInput(labelText) {{
            const labels = document.querySelectorAll('label');
            for (let label of labels) {{
                if (label.textContent.toLowerCase().includes(labelText)) {{
                    const input = label.querySelector('input') || 
                                 label.parentElement.querySelector('input') ||
                                 document.getElementById(label.getAttribute('for'));
                    if (input && input.type === 'text') return input;
                }}
            }}
            // Buscar por placeholder
            const inputs = document.querySelectorAll('input[type="text"]');
            for (let input of inputs) {{
                if (input.placeholder && input.placeholder.toLowerCase().includes(labelText)) {{
                    return input;
                }}
            }}
            return null;
        }}
        
        const fechaDesde = findDateInput('desde') || findDateInput('from');
        const fechaHasta = findDateInput('hasta') || findDateInput('to');
        
        if (fechaDesde) {{
            fechaDesde.value = '{desde}';
            fechaDesde.dispatchEvent(new Event('input', {{ bubbles: true }}));
            fechaDesde.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
        
        if (fechaHasta) {{
            fechaHasta.value = '{hasta}';
            fechaHasta.dispatchEvent(new Event('input', {{ bubbles: true }}));
            fechaHasta.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
        
        return {{ desde: !!fechaDesde, hasta: !!fechaHasta }};
        """
        
        resultado = driver.execute_script(script_fechas)
        print(f"Campos de fecha encontrados: {resultado}")
        
        # Buscar y hacer clic en el botón de consultar/buscar
        script_boton = """
        const botones = document.querySelectorAll('button, input[type="submit"]');
        for (let btn of botones) {
            const texto = btn.textContent || btn.value || '';
            if (texto.toLowerCase().includes('consultar') || 
                texto.toLowerCase().includes('buscar') ||
                texto.toLowerCase().includes('filtrar')) {
                btn.click();
                return true;
            }
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
        # No lanzar excepción para continuar con la ejecución


def descargar_xmls(driver):
    """
    Descarga los archivos XML de las facturas mostradas en la tabla
    """
    wait = WebDriverWait(driver, 20)
    total_descargados = 0
    pagina = 1
    
    while True:
        print(f"📄 Procesando página {pagina}...")
        time.sleep(3)
        
        try:
            # Buscar todos los botones de descarga en la página actual
            script_descargas = """
            const botonesDescarga = [];
            const filas = document.querySelectorAll('table tr, .ui-datatable-data tr, .data-table tr');
            
            filas.forEach((fila, index) => {
                // Buscar botones o enlaces de descarga en cada fila
                const botones = fila.querySelectorAll('button, a, img');
                botones.forEach(btn => {
                    const onclick = btn.getAttribute('onclick') || '';
                    const title = btn.getAttribute('title') || '';
                    const alt = btn.getAttribute('alt') || '';
                    
                    // Buscar indicadores de descarga XML
                    if (onclick.includes('xml') || onclick.includes('XML') ||
                        title.toLowerCase().includes('xml') || 
                        alt.toLowerCase().includes('xml') ||
                        btn.className.toLowerCase().includes('xml')) {
                        botonesDescarga.push({
                            index: index,
                            element: btn
                        });
                    }
                });
            });
            
            return botonesDescarga.length;
            """
            
            cantidad_botones = driver.execute_script(script_descargas)
            print(f"   Encontrados {cantidad_botones} botones de descarga")
            
            if cantidad_botones == 0:
                print("   No hay más facturas para descargar")
                break
            
            # Descargar cada XML haciendo clic en los botones
            for i in range(cantidad_botones):
                script_click = f"""
                const filas = document.querySelectorAll('table tr, .ui-datatable-data tr, .data-table tr');
                let count = 0;
                for (let fila of filas) {{
                    const botones = fila.querySelectorAll('button, a, img');
                    for (let btn of botones) {{
                        const onclick = btn.getAttribute('onclick') || '';
                        const title = btn.getAttribute('title') || '';
                        const alt = btn.getAttribute('alt') || '';
                        
                        if (onclick.includes('xml') || onclick.includes('XML') ||
                            title.toLowerCase().includes('xml') || 
                            alt.toLowerCase().includes('xml') ||
                            btn.className.toLowerCase().includes('xml')) {{
                            if (count === {i}) {{
                                btn.click();
                                return true;
                            }}
                            count++;
                        }}
                    }}
                }}
                return false;
                """
                
                resultado = driver.execute_script(script_click)
                if resultado:
                    total_descargados += 1
                    time.sleep(1.5)  # Esperar entre descargas
                
                if total_descargados % 10 == 0:
                    print(f"   Descargados: {total_descargados}")
            
            # Verificar si hay siguiente página
            script_siguiente = """
            const botonesPagina = document.querySelectorAll('button, a, span');
            for (let btn of botonesPagina) {
                const texto = btn.textContent || '';
                if ((texto.includes('>') || texto.includes('Siguiente') || 
                     texto.includes('Next')) && !btn.disabled) {
                    btn.click();
                    return true;
                }
            }
            // Buscar por clase común de paginación
            const nextBtn = document.querySelector('.ui-paginator-next:not(.ui-state-disabled)');
            if (nextBtn) {
                nextBtn.click();
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
            print(f"⚠️ Error al descargar XMLs: {e}")
            break
    
    print(f"✅ Total de XMLs descargados: {total_descargados}")
