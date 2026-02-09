# Manual para consultar comprobantes electrónicos emitidos

## Proceso paso a paso:

1. **Iniciar sesión** en https://srienlinea.sri.gob.ec

2. **Navegar al menú:**
   - Facturación electrónica → Producción → Consultas → Comprobantes electrónicos emitidos

3. **En el formulario de búsqueda:**
   - Dejar seleccionado "Ruc/Cédula/Pasaporte"
   - El campo RUC ya debe estar llenado con tu número
   - Cambiar la "Fecha emisión" a la fecha deseada (formato: DD/MM/AAAA)
   - Dejar los demás campos como están:
     - Estado autorización: Autorizados
     - Tipo de comprobante: Factura
     - Establecimiento: Todos
     - Punto de emisión: (vacío o 001)

4. **Presionar el botón "Consultar"**

5. **Si hay resultados:**
   - Aparecerá una tabla con los comprobantes
   - Presionar el botón "Descargar reporte" o "Exportar Txt"
   - El archivo se descargará en formato TXT

## Problemas comunes:

### Error: "No existen datos para los parámetros ingresados"
- Significa que no hay comprobantes emitidos para esa fecha
- Probar con una fecha diferente donde sí hayas emitido facturas

### Error: "La fecha ingresada debe ser menor a la fecha actual"
- La fecha debe ser anterior al día de hoy
- No puedes consultar comprobantes de fechas futuras

### La página vuelve al menú después de consultar
- Puede ser un problema temporal del sitio
- Intentar nuevamente en unos minutos
- Verificar que la sesión no haya expirado

## URLs importantes:
- Página de menú: https://srienlinea.sri.gob.ec/comprobantes-electronicos-internet/pages/consultas/menu.jsf
- Página de emitidos: https://srienlinea.sri.gob.ec/comprobantes-electronicos-internet/pages/consultas/recuperarComprobantes.jsf
