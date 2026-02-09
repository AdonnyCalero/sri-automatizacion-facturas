@echo off
echo ========================================
echo SRI AUTOMATIZACION - Ejecucion Directa
echo ========================================
echo.
echo Este ejecutara el script de descarga de facturas
echo.
pause

cd /d "%~dp0"
echo.
echo [1/3] Iniciando proceso...
python main.py

echo.
echo [2/3] Verificando descargas...
if exist "facturas_xml\recibidas\*.txt" (
    echo [OK] Facturas recibidas descargadas
) else (
    echo [ADVERTENCIA] No se encontraron facturas recibidas
)

if exist "facturas_xml\emitidas\*.txt" (
    echo [OK] Facturas emitidas descargadas
) else (
    echo [ADVERTENCIA] No se encontraron facturas emitidas
)

echo.
echo [3/3] Generando Excel...
python -c "from generar_excel import generar_excel; generar_excel()"

echo.
echo ========================================
echo PROCESO COMPLETADO
echo ========================================
echo.
echo Los archivos estan en:
echo - facturas_xml\recibidas\
echo - facturas_xml\emitidas\
echo - facturas_recibidas.xlsx
echo - facturas_emitidas.xlsx
echo.
pause
