# Automatización SRI - Descarga de Facturas

Este proyecto automatiza la descarga de facturas electrónicas del SRI (Servicio de Rentas Internas) de Ecuador, tanto las recibidas como las emitidas, y genera un archivo Excel con toda la información.

## Características

- Inicio de sesión automático en el SRI
- Descarga de facturas recibidas y emitidas
- Filtrado por rango de fechas
- Descarga automática de archivos XML
- Generación de archivo Excel con todos los datos
- Manejo de paginación para grandes volúmenes de facturas

## Requisitos

- Python 3.8 o superior
- Google Chrome instalado
- ChromeDriver (se instala automáticamente con webdriver-manager)

## Instalación

1. Clonar o descargar este repositorio

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar credenciales:
   - Copiar `config.example.py` a `config.py`
   - Editar `config.py` con tus credenciales del SRI:

```python
RUC = "TU_RUC_AQUI"
CLAVE = "TU_CLAVE_AQUI"
FECHA_DESDE = "01/01/2024"
FECHA_HASTA = "31/12/2024"
```

## Uso

### Forma 1: Ejecución Directa (Recomendada) ✅

**Esta es la forma más confiable.** Simplemente haz doble clic en:
```
ejecutar.bat
```

O ejecuta en terminal:
```bash
python main.py
```

El script hará todo automáticamente:
- Abrirá Chrome
- Descargará facturas recibidas y emitidas
- Generará los archivos Excel

### Forma 2: Interfaz Web (Frontend + Backend)

**Nota:** Esta opción es más visual pero el reCAPTCHA del SRI requiere que el script se ejecute directamente con el navegador visible.

Para usar la interfaz web:
```bash
# Terminal 1 - Backend
python api.py

# Terminal 2 - Frontend
npm run dev
```

Luego abre: http://localhost:3001

**Recomendación:** Usa la Forma 1 para descargas reales.

---

## Resultado

Los archivos se descargarán en:
- `facturas_xml/recibidas/` - Facturas recibidas
- `facturas_xml/emitidas/` - Facturas emitidas
- `facturas_recibidas.xlsx` - Excel con recibidas
- `facturas_emitidas.xlsx` - Excel con emitidas

## Estructura del Proyecto

```
sri_automatizacionv2/
├── main.py                 # Script principal
├── login_sri.py           # Módulo de login
├── descargar_facturas.py  # Módulo de descarga de facturas
├── generar_excel.py       # Módulo de generación de Excel
├── procesar_xml.py        # Módulo de procesamiento de XMLs
├── guardar_html.py        # Utilidad para debug (guarda HTML)
├── config.py              # Configuración (credenciales)
├── config.example.py      # Ejemplo de configuración
├── requirements.txt       # Dependencias
└── facturas_xml/          # Carpeta de descargas
    ├── recibidas/
    └── emitidas/
```

## Notas Importantes

- **Captcha**: El SRI requiere resolver un captcha visual. El script espera 12 segundos después del login para que lo resuelvas manualmente.
- **Rango de fechas**: Configura el rango en `config.py` usando el formato DD/MM/AAAA.
- **Chrome visible**: El navegador se ejecuta en modo visible para que puedas interactuar con el captcha.
- **Archivos de debug**: Los HTMLs de cada paso se guardan en `debug/html/` para diagnóstico.

## Solución de Problemas

### Error: No se encuentra ChromeDriver
Asegúrate de tener Google Chrome instalado. El `webdriver-manager` debería instalar el ChromeDriver automáticamente.

### Error al filtrar fechas
El sitio del SRI puede cambiar. Si hay errores, revisa los archivos HTML de debug en `debug/html/` para entender la estructura actual de la página.

### No se descargan los XMLs
Verifica que Chrome tenga permisos para descargar archivos en las rutas configuradas. Las descargas van directamente a las carpetas `facturas_xml/recibidas` y `facturas_xml/emitidas`.

## Columnas del Excel Generado

El archivo `facturas_sri.xlsx` contiene las siguientes columnas:
- **tipo**: RECIBIDA o EMITIDA
- **fecha**: Fecha de emisión
- **razon_social**: Razón social del emisor/receptor
- **ruc**: RUC del emisor/receptor
- **subtotal**: Total sin impuestos
- **iva**: Valor del IVA
- **total**: Importe total

## Seguridad

⚠️ **IMPORTANTE**: 
- Nunca subas el archivo `config.py` con tus credenciales reales a repositorios públicos
- El archivo `config.py` está en `.gitignore` para evitar subirlo por accidente
- Usa siempre `config.example.py` como plantilla

## Licencia

Este proyecto es de uso libre. Úsalo bajo tu propia responsabilidad.

## Autor

Desarrollado para automatizar procesos con el SRI de Ecuador.
