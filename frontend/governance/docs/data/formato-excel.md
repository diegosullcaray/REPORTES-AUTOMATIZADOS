# Formato Excel de las salidas

Las salidas copian el formato de los Excel del legado. **No llevan hoja de control ni metadatos**: el libro contiene solo los datos del reporte (la verificación de tablas y los avisos se muestran en pantalla). Código: `src/reportes/comun/excel.py` ([ADR-0009](../architecture/adr/ADR-0009-formato-excel-del-legado.md)).

## Qué se pudo analizar (y qué no)
En `docs/LEGADO` solo hay **un Excel real**: `Cartera-Sin asignar-base.xlsm` (más 3 imágenes `Reporte_Temporal_*.jpg` de su salida). Los demás Excel que se entregaban solo existen como **nombre de adjunto** en los correos (PDF) y como pasos en las `NOTAS.docx`. Por eso:

| Fuente | Qué aporta |
|---|---|
| `Cartera-Sin asignar-base.xlsm` | formato completo de `cartera-sin-asignar` (hojas, columnas, estilos, resumen) |
| Correos PDF (adjuntos) | **nombre de archivo** de cada reporte |
| `NOTAS.docx` | nombres de hoja de algunos reportes y la regla «copiar el resultado con cabeceras» |
| Resto de reportes | cabeceras = nombres de columna del SQL; estilo de tabla del único Excel real |

## Formato común (todas las hojas de datos)
- Fila 1 = encabezados (nombres de columna del SQL, tal como los devuelve la consulta); datos desde la fila 2, desde la columna A.
- Los datos van como **Tabla de Excel** con estilo `TableStyleMedium2` (el de `DATA_MIS_v2`), con filtros; anchos de columna ajustados al contenido.
- Fechas sin hora cuando todas son medianoche. Columnas repetidas o sin nombre se renombran (`a_2`, `Columna`).
- Un resultado sin filas deja solo los encabezados (sin Tabla).
- Si un reporte devuelve varios resultados, cada uno es una hoja (`Datos`, `Datos_2`… salvo que el reporte nombre sus hojas).

## `cartera-sin-asignar` (formato completo, del Excel del legado)
| Hoja | Contenido |
|---|---|
| `DATA_MIS_v2` | Tabla con 11 columnas: `NIVEL`, `Asesor_Operativo`, `Cuenta_Cliente`, `Nom_Cliente`, `Operacion`, `Saldo_Capital`, `Grupo`, `Territorio`, `Corredor`, `Agencia_Cli`, `Unidad_Negocio` (orden por territorio, corredor, agencia) |
| `RESUMEN_v2` | Resumen tipo tabla dinámica en `B2:C…`: encabezados «TERRITORIO POR CLIENTE» / «SALDO CARTERA - MIS»; filas por `NIVEL → Grupo → Territorio → Corredor → Agencia_Cli` con sangría por nivel (0 a 4), suma de `Saldo_Capital` por nivel, valores nulos como «(en blanco)», formato `"S/" #,##0.00` y fila final «Total general». Colores de la imagen `Reporte_Temporal.jpg` (encabezado azul marino, niveles superiores azul claro, hojas sin relleno, bordes finos) |

Una prueba compara el resumen generado con el `RESUMEN_v2` del Excel original calculado desde su `DATA_MIS_v2`: **mismas 66 filas, mismas sangrías y mismas sumas**; en el orden de agencias hermanas el legado tiene un orden manual de la tabla dinámica y aquí es alfabético.

No se replican las hojas ocultas del legado: `FILTRO` (parámetro de fecha de la consulta de Excel) y `CORREOS` / `Hoja1` (listas de correos del envío por Outlook).

## `saca-tu-garra` (según `governance/tasks/tarea.md`)
Solo estas 5 columnas, en este orden y con estos encabezados:

| Encabezado | Columna del SQL | Regla |
|---|---|---|
| Usuario | `HASEOPER` | — |
| Var. Saldo Vigente | `VAR_VIGENTE` | si el valor es 0 → `-` |
| Productividad | `PRODUCTIVDAD` (así se llama en el SQL heredado; se acepta también `PRODUCTIVIDAD`) | si el valor es 0 → `-` |
| Efectividad -30 a 0 | `RatioRecuperacion0_30` | si el valor es 0 (o nulo) → `NULL` |
| Efectividad 1 a 30 | `RatioRecuperacion1_30` | si el valor es 0 (o nulo) → `NULL` |

## `fondeo-estable` (según `governance/tasks/tarea.md`)
| Encabezado | Columna del SQL | Formato |
|---|---|---|
| FECHA | `FECHA` | `dd/mm/aaaa` (p. ej. `30/09/2026`) |
| Matriz | `RDESMAT` | — |
| Saldo Fondeo Estable | `HSALFESI` | — |

`heredados-pdm`: pendiente de definir su formato.

Si una columna esperada no viene en el resultado, el reporte se detiene con un error que nombra la columna y las que sí llegaron.

## Nombres de archivo (de los adjuntos históricos)
Tokens: `{AAAA-MM-DD}` `{AAAAMMDD}` `{AAAAMM}` `{AAAA}` `{AA}` `{MES}` (Junio) `{mes3}` (jun) `{MES3}` (JUN).

| Comando | Archivo | Origen |
|---|---|---|
| `desembolsos-por-canal` | `Desembolsos_canal_{AAAAMMDD}.xlsx` | adjunto histórico |
| `michael-captaciones`, `michael-castigos` | `Datos Cierre {MES} {AA}.xlsx` (libro compartido: hojas `Captaciones` y `Castigos`) | adjunto histórico + NOTAS |
| `saca-tu-garra` | `Base Saca tu Garra_{AAAAMMDD}.xlsx` | adjunto histórico |
| `fondeo-estable` | `Saldo_FondeoEstable_{AAAAMMDD}.xlsx` | adjunto histórico |
| `heredados-pdm` | `PDM Heredado {MES} {AA}.xlsx` | adjunto histórico |
| `tapp-saldo-medio-territorio` | `SaldoMedio_TPPSTOCK_TPPMES_{AAAAMM}.xlsx` | adjunto histórico (`…_2023-2025`) |
| `clientes-jovenes` | `Clientes_jóvenes_{mes3}{AA}.xlsx` | adjunto histórico |
| `productos-verdes` | `7. Productos_verdes_{mes3}{AA}.xlsx` | adjunto histórico |
| `bancarizados` | `clientes_nuevos_bancarizados_exclusivos_{MES3}{AA}.xlsx` | adjunto histórico |
| `clientes-extranjeros` | `ClientesExtranjeros {MES3} {AAAA}-TIPODOC.xlsx` | adjunto histórico |
| `indicadores-clientes` | `Info para Finanzas {MES3}{AA}.xlsx` | adjunto histórico |
| `cartera-sin-asignar` | `Cartera-Sin asignar-{AAAA-MM-DD}.xlsx` (+ `Reporte_Temporal_{AAAA-MM-DD}.jpg`) | nombre que ponía la macro al adjunto |
| `giovanni-cartera-agro` | `Cartera Vigente Agro_{AAAAMMDD}.xlsx`; hojas `Saldo vigente`, `Saldo vigente (cierre anterior)`, `Clientes` | NOTAS («Saldo vigente» con 2 resultados y «Clientes») |
| `giovanni-captaciones`, `giovanni-seguros`, `saldo-medio-vigente` | nombre convencional (`… _{AAAAMMDD}`) | sin adjunto histórico |
| resto | `Comando_{AAAAMMDD}.xlsx` | convención |

`saldo-medio-vigente`: hojas `Saldo medio mes` y `Saldo diario`; `contratacion-electronica`: `CE habilitados` y `CE desembolsados`.

## Pendiente (necesita los Excel originales)
Para igualar el resto de reportes al detalle (orden y nombre exacto de columnas, hojas auxiliares, tablas dinámicas, formatos numéricos, colores) hacen falta los Excel entregados: `Desembolsos_canal_20260630.xlsx`, `Datos Cierre Junio 26.xlsx`, `Base Saca tu Garra_20260630.xlsx`, `Saldo_FondeoEstable_20260630.xlsx`, `PDM Heredado Junio 26.xlsx`, `SaldoMedio_TPPSTOCK_TPPMES_2023-2025.xlsx`, `Clientes_jóvenes_jul26.xlsx`, `7. Productos_verdes_jul26.xlsx`, `clientes_nuevos_bancarizados_exclusivos_JUL26.xlsx`, `ClientesExtranjeros JUL 2026-TIPODOC.xlsx`, `Info para Finanzas JUL26.xlsx`. Con ellos se declaran las hojas (`hojas=`), resúmenes (`resumenes=`) y formatos de cada reporte.
- Los nombres de hoja de varios reportes siguen siendo `Datos` / `Datos_2` hasta tener esos archivos.
- `cartera-sin-asignar` sí genera la imagen del resumen (`Reporte_Temporal_<fecha>.jpg`, mismo aspecto que la del legado) y la envía por correo ([runbook](../development/runbooks/cartera-sin-asignar.md)); el resto de reportes se entrega a mano.
