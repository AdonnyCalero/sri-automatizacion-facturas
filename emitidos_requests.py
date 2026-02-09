"""
Consulta de comprobantes emitidos usando requests directamente
Esto evita problemas de Selenium con formularios complejos
"""
import requests
import time
from urllib.parse import urlencode

def consultar_emitidos_requests(session, fecha_desde, ruc, directorio_descarga="facturas_xml/emitidas"):
    """
    Consulta comprobantes emitidos usando requests directamente
    """
    print(f"\n📡 Consultando EMITIDOS vía Requests para fecha: {fecha_desde}")
    
    try:
        # URL base
        base_url = "https://srienlinea.sri.gob.ec"
        
        # Primero, obtener la página de recuperarComprobantes para obtener ViewState
        url_formulario = f"{base_url}/comprobantes-electronicos-internet/pages/consultas/recuperarComprobantes.jsf"
        
        print("   1. Obteniendo formulario...")
        response = session.get(url_formulario, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ Error al obtener formulario: {response.status_code}")
            return False
        
        # Extraer ViewState del HTML
        import re
        viewstate_match = re.search(r'id="javax\.faces\.ViewState"[^>]*value="([^"]+)"', response.text)
        if not viewstate_match:
            print("   ❌ No se encontró ViewState")
            return False
        
        viewstate = viewstate_match.group(1)
        print(f"   ✅ ViewState obtenido")
        
        # Preparar datos del formulario para consultar
        # Nota: Estos son los campos típicos de PrimeFaces
        data = {
            "frmPrincipal": "frmPrincipal",
            "frmPrincipal:opciones": "ruc",  # Opción RUC
            "frmPrincipal:txtParametro": ruc,
            "frmPrincipal:calendarFechaDesde_input": fecha_desde,
            "frmPrincipal:cmbEstadoAutorizacion": "AUT",  # Autorizados
            "frmPrincipal:cmbTipoComprobante": "1",  # Factura
            "frmPrincipal:cmbEstablecimiento": "",  # Todos
            "frmPrincipal:txtPuntoEmision": "",
            "frmPrincipal:btnConsultar": "frmPrincipal:btnConsultar",
            "javax.faces.ViewState": viewstate
        }
        
        print("   2. Enviando consulta...")
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': url_formulario,
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = session.post(url_formulario, data=data, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ Error en consulta: {response.status_code}")
            return False
        
        print(f"   ✅ Consulta enviada. Respuesta: {len(response.text)} bytes")
        
        # Verificar si hay resultados
        if "No existen datos" in response.text or "No se encontraron" in response.text:
            print("   ⚠️ No se encontraron comprobantes para la fecha indicada")
            return False
        
        # Ahora intentar descargar el reporte
        print("   3. Descargando reporte...")
        
        # Preparar datos para descarga
        data_descarga = {
            "frmPrincipal": "frmPrincipal",
            "frmPrincipal:lnkTxtlistado": "frmPrincipal:lnkTxtlistado",
            "javax.faces.ViewState": viewstate
        }
        
        response_txt = session.post(url_formulario, data=data_descarga, headers=headers, timeout=30)
        
        if response_txt.status_code == 200:
            content_type = response_txt.headers.get('Content-Type', '')
            
            # Verificar si es texto plano o application/txt
            if any(t in content_type for t in ['text/plain', 'application/txt', 'text/txt']) or \
               response_txt.text.startswith('Clave') or \
               'RUC_EMISOR' in response_txt.text:
                # Guardar archivo
                import os
                os.makedirs(directorio_descarga, exist_ok=True)
                
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"reporte_emitidos_{timestamp}.txt"
                ruta_archivo = os.path.join(directorio_descarga, nombre_archivo)
                
                with open(ruta_archivo, 'wb') as f:
                    f.write(response_txt.content)
                
                print(f"   ✅ Reporte descargado: {nombre_archivo}")
                print(f"   📁 Tamaño: {len(response_txt.content)} bytes")
                return True
            else:
                print(f"   ⚠️ La respuesta no es TXT: {content_type}")
                return False
        else:
            print(f"   ❌ Error en descarga: {response_txt.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False
