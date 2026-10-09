# ADR-0009: Salidas con el formato Excel del legado, sin hoja de control

- Estado: Vigente · Fecha: 2026-10-06

## Contexto
La primera versión exportaba con pandas: hojas con nombres genéricos (`Resultado_N`) y una hoja `Control` (corte, filas, estado de tablas). Esa hoja no existía en ningún entregable del legado y el usuario no la quiere. Además los archivos se nombraban distinto de los adjuntos históricos, y el único Excel real del legado (`Cartera-Sin asignar-base.xlsm`) trae un formato definido: tabla `TableStyleMedium2` y un resumen jerárquico (tabla dinámica) con formato de moneda.

## Decisión
- Se elimina la hoja `Control`: el libro solo tiene los datos. La verificación de tablas, el corte y los avisos se muestran en pantalla.
- `comun/excel.py` escribe los datos como Tabla de Excel (`TableStyleMedium2`) y calcula resúmenes jerárquicos (`Resumen`) con sangría, suma por nivel, moneda `"S/" #,##0.00` y «Total general».
- `ReporteLote` declara `archivo` (nombre con tokens de fecha, tomado de los adjuntos históricos), `hojas` (nombre de cada resultado), `resumenes` y `libro_compartido`.
- `cartera-sin-asignar` reproduce `DATA_MIS_v2` + `RESUMEN_v2`; una prueba lo compara con el Excel original.
- Los 3 reportes con CLI propia (bancarizados, extranjeros, indicadores) conservan su exportador y adoptan el nombre de archivo histórico.

## Consecuencias
- Sin hoja de control se pierde la trazabilidad dentro del archivo; queda en la salida de consola y en los avisos. Si hiciera falta, sería un archivo aparte, no una hoja.
- Para igualar el resto de reportes al detalle hacen falta sus Excel originales ([pendiente](../../data/formato-excel.md#pendiente-necesita-los-excel-originales)).
