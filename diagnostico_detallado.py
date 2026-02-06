#!/usr/bin/env python3
"""
Script de diagnóstico detallado para analizar la estructura de la tabla
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys

# Leer el HTML guardado
html_path = "debug/html/03_recibidas_filtradas_20260206_121815.html"

options = Options()
options.add_experimental_option("prefs", {
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=options)

try:
    # Cargar el archivo HTML local
    driver.get(f"file:///{html_path}")
    time.sleep(2)
    
    print("=" * 80)
    print("DIAGNÓSTICO DETALLADO DE LA TABLA")
    print("=" * 80)
    
    # Script de diagnóstico completo
    script = """
    const resultado = {
        tablas: [],
        errores: []
    };
    
    try {
        // Buscar todas las tablas
        const todasLasTablas = document.querySelectorAll('table');
        
        todasLasTablas.forEach((tabla, idx) => {
            const infoTabla = {
                indice: idx,
                id: tabla.id,
                clase: tabla.className,
                tieneThead: !!tabla.querySelector('thead'),
                tieneTbody: !!tabla.querySelector('tbody'),
                numTrDirectos: tabla.querySelectorAll(':scope > tr').length,
                numTrTotal: tabla.querySelectorAll('tr').length,
                filas: []
            };
            
            // Obtener todas las filas de esta tabla específica
            const todasFilas = tabla.querySelectorAll('tr');
            
            // Analizar las primeras 5 filas
            for (let i = 0; i < Math.min(5, todasFilas.length); i++) {
                const fila = todasFilas[i];
                const celdas = fila.querySelectorAll('td, th');
                const infoFila = {
                    index: i,
                    esTh: celdas.length > 0 && celdas[0].tagName === 'TH',
                    numCeldas: celdas.length,
                    celdas: []
                };
                
                // Analizar cada celda
                celdas.forEach((celda, j) => {
                    const enlaces = celda.querySelectorAll('a');
                    const infoCelda = {
                        index: j,
                        tag: celda.tagName,
                        esHeader: celda.tagName === 'TH',
                        texto: celda.innerText.trim().substring(0, 30),
                        numEnlaces: enlaces.length,
                        enlaces: []
                    };
                    
                    enlaces.forEach(enlace => {
                        infoCelda.enlaces.push({
                            id: enlace.id,
                            href: enlace.href,
                            onclick: enlace.getAttribute('onclick'),
                            img: enlace.querySelector('img') ? 'Sí' : 'No'
                        });
                    });
                    
                    infoFila.celdas.push(infoCelda);
                });
                
                infoTabla.filas.push(infoFila);
            }
            
            resultado.tablas.push(infoTabla);
        });
        
    } catch(e) {
        resultado.errores.push(e.message);
    }
    
    return resultado;
    """
    
    resultado = driver.execute_script(script)
    
    print(f"\nTotal de tablas encontradas: {len(resultado['tablas'])}\n")
    
    for tabla in resultado['tablas']:
        print(f"\n{'='*80}")
        print(f"TABLA #{tabla['indice']}")
        print(f"{'='*80}")
        print(f"ID: {tabla['id']}")
        print(f"Clase: {tabla['clase']}")
        print(f"Tiene thead: {tabla['tieneThead']}")
        print(f"Tiene tbody: {tabla['tieneTbody']}")
        print(f"Filas tr directas (> tr): {tabla['numTrDirectos']}")
        print(f"Total filas tr: {tabla['numTrTotal']}")
        
        if tabla['filas']:
            print(f"\nPrimeras filas:")
            for fila in tabla['filas']:
                tipo = "HEADER" if fila['esTh'] else "DATA"
                print(f"\n  [{fila['index']}] {tipo} - {fila['numCeldas']} celdas")
                
                for celda in fila['celdas']:
                    tipo_celda = "TH" if celda['esHeader'] else "TD"
                    print(f"    [{celda['index']}] {tipo_celda}: '{celda['texto']}' - {celda['numEnlaces']} enlaces")
                    
                    for enlace in celda['enlaces']:
                        print(f"      → ID: {enlace['id']}, Img: {enlace['img']}")
    
    if resultado['errores']:
        print(f"\n❌ Errores:")
        for error in resultado['errores']:
            print(f"  - {error}")
    
    print("\n" + "=" * 80)
    
finally:
    driver.quit()
