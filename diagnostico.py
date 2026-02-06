#!/usr/bin/env python3
"""
Script de diagnóstico para ver la estructura de la tabla
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

options = Options()
options.add_experimental_option("prefs", {
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=options)

try:
    # Navegar a una página de prueba o cargar el HTML guardado
    # Por ahora, asumimos que el usuario tiene el HTML guardado
    
    print("=" * 60)
    print("DIAGNÓSTICO DE LA TABLA")
    print("=" * 60)
    
    # Script para obtener información detallada de la tabla
    script = """
    const resultado = {
        tablasEncontradas: 0,
        tablaPrincipal: null,
        filas: [],
        errores: []
    };
    
    try {
        // Buscar todas las tablas
        const tablas = document.querySelectorAll('table');
        resultado.tablasEncontradas = tablas.length;
        
        // Encontrar la tabla principal
        let tablaPrincipal = null;
        for (let tabla of tablas) {
            const encabezados = tabla.querySelectorAll('th');
            for (let th of encabezados) {
                const texto = (th.innerText || '').toUpperCase();
                if (texto.includes('DOCUMENTO') || texto.includes('RIDE')) {
                    tablaPrincipal = tabla;
                    break;
                }
            }
            if (tablaPrincipal) break;
        }
        
        if (!tablaPrincipal) {
            tablaPrincipal = document.querySelector('.ui-datatable-table, .ui-table, table.ui-datatable');
        }
        
        if (!tablaPrincipal) {
            resultado.errores.push('No se encontró tabla principal');
            return resultado;
        }
        
        // Información de la tabla
        resultado.tablaPrincipal = {
            clase: tablaPrincipal.className,
            id: tablaPrincipal.id,
            tieneTbody: !!tablaPrincipal.querySelector('tbody'),
            numTh: tablaPrincipal.querySelectorAll('th').length,
            numTr: tablaPrincipal.querySelectorAll('tr').length
        };
        
        // Obtener encabezados
        const encabezados = tablaPrincipal.querySelectorAll('th');
        const headers = [];
        encabezados.forEach((th, idx) => {
            headers.push({
                index: idx,
                texto: th.innerText.trim(),
                id: th.id
            });
        });
        resultado.headers = headers;
        
        // Obtener filas del tbody
        const tbody = tablaPrincipal.querySelector('tbody');
        if (tbody) {
            const filasTr = tbody.querySelectorAll('tr');
            resultado.tablaPrincipal.filasEnTbody = filasTr.length;
            
            // Analizar las primeras 3 filas
            for (let i = 0; i < Math.min(3, filasTr.length); i++) {
                const fila = filasTr[i];
                const celdas = fila.querySelectorAll('td');
                const filaInfo = {
                    index: i,
                    numCeldas: celdas.length,
                    celdas: []
                };
                
                // Analizar cada celda
                celdas.forEach((celda, idx) => {
                    const enlaces = celda.querySelectorAll('a');
                    const infoCelda = {
                        index: idx,
                        texto: celda.innerText.trim().substring(0, 50),
                        numEnlaces: enlaces.length,
                        enlaces: []
                    };
                    
                    enlaces.forEach(enlace => {
                        infoCelda.enlaces.push({
                            id: enlace.id,
                            href: enlace.href,
                            onclick: enlace.getAttribute('onclick'),
                            tieneImg: !!enlace.querySelector('img')
                        });
                    });
                    
                    filaInfo.celdas.push(infoCelda);
                });
                
                resultado.filas.push(filaInfo);
            }
        } else {
            resultado.errores.push('No se encontró tbody');
        }
        
    } catch(e) {
        resultado.errores.push('Error: ' + e.message);
    }
    
    return resultado;
    """
    
    resultado = driver.execute_script(script)
    
    print(f"\nTablas encontradas: {resultado['tablasEncontradas']}")
    
    if resultado['tablaPrincipal']:
        tp = resultado['tablaPrincipal']
        print(f"\nTabla Principal:")
        print(f"  - Clase: {tp['clase']}")
        print(f"  - ID: {tp['id']}")
        print(f"  - Tiene tbody: {tp['tieneTbody']}")
        print(f"  - Encabezados (th): {tp['numTh']}")
        print(f"  - Filas totales (tr): {tp['numTr']}")
        if 'filasEnTbody' in tp:
            print(f"  - Filas en tbody: {tp['filasEnTbody']}")
    
    if 'headers' in resultado:
        print(f"\nEncabezados de columnas:")
        for (const h of resultado['headers']) {
            console.log(`  [${h.index}] ${h.texto} (id: ${h.id})`);
        }
    }
    
    if (resultado['filas'].length > 0) {
        console.log(`\nAnálisis de las primeras ${resultado['filas'].length} filas:`);
        for (const fila of resultado['filas']) {
            console.log(`\nFila ${fila.index}:`);
            console.log(`  - Número de celdas: ${fila.numCeldas}`);
            for (const celda of fila.celdas) {
                console.log(`\n  Celda [${celda.index}]:`);
                console.log(`    Texto: ${celda.texto}`);
                console.log(`    Enlaces: ${celda.numEnlaces}`);
                if (celda.enlaces.length > 0) {
                    for (const enlace of celda.enlaces) {
                        console.log(`      - ID: ${enlace.id}`);
                        console.log(`        Href: ${enlace.href}`);
                        console.log(`        Onclick: ${enlace.onclick ? enlace.onclick.substring(0, 100) : 'N/A'}`);
                        console.log(`        Tiene imagen: ${enlace.tieneImg}`);
                    }
                }
            }
        }
    }
    
    if (resultado['errores'].length > 0) {
        console.log(`\n❌ Errores encontrados:`);
        for (const error of resultado['errores']) {
            console.log(`  - ${error}`);
        }
    }
    
    print("\n" + "=" * 60);
    print("FIN DEL DIAGNÓSTICO");
    print("=" * 60);
    
finally:
    driver.quit()
