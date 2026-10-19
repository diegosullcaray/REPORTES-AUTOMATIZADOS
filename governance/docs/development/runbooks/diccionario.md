# Diccionario — cómo usarlo y mantenerlo al día

Decisión y alcance: [ADR-0017](../../architecture/adr/ADR-0017-modulo-diccionario.md). Contrato del archivo: [diccionario de datos](../../data/diccionario.md).

## Antes de empezar

No hace falta ningún otro repo ni `node`. Necesitas red/VPN a los servidores (`mish`, y los demás de las bases que usan los reportes) y que la cuenta del `.env` pueda leer `mod_rep.rep.RREGREP01` y los metadatos y el código de los procedimientos de las bases (`VIEW DEFINITION`).

1. Abre **Diccionario › Procesos › «Generar el diccionario desde la base»** y pulsa Generar (hasta un par de minutos). Se guarda en `data/outputs/diccionario/generado/diccionario.json`.
2. Mientras no lo generes, la web muestra solo el catálogo de reportes (se lee en vivo de `mod_rep.rep.RREGREP01`) y un aviso para generarlo.

## Las pantallas (menú lateral › Diccionario)

| Pantalla | Para qué |
|---|---|
| **Resumen** (`/diccionario`) | Tres gráficos: *avance de la documentación* por base (validados · extraídos · pendientes), *calidad* (errores y avisos por regla) y *lo que aporta a tus reportes*: cuántas de tus tablas tienen ficha, las columnas de fecha por confirmar y las tablas que más reportes del MIS leen y los tuyos no (pulsa una barra para abrirla). Cada gráfico trae «Ver como tabla» |
| **Reportes del MIS** (`/diccionario/reportes`) | Una tarjeta por base de datos. Al entrar (`?base=`): pestaña **Procedimientos** (con los reportes que los ejecutan) y pestaña **Tablas** que ocupa (las que guarda y las que sus procedimientos leen de otras bases; filtro «viven en esta base» / «de otras») |
| Detalle de un reporte | Procedimiento, parámetros, tablas con las columnas que usa (las de fecha resaltadas) y hallazgos |
| Detalle de una tabla | Columnas, qué reportes del MIS la leen y **cómo la registran tus reportes** (`tablas.py`: tipo, columna de fecha, confianza) |
| **Procesos** (`/diccionario/procesos`) | Dos pestañas (`?tab=`): **Procesos** (una tarjeta por proceso, con su última ejecución; entra a uno para verlo al detalle) e **Historial** (todas las ejecuciones, con su log en vivo) |
| Detalle de un proceso (`/diccionario/procesos/<id>`) | Pestañas **General** (qué hace, ejecutar con confirmación, última salida), **Ejecuciones** (las de ese proceso), y **Script** (las consultas y el código que ejecuta) |

## Los procesos

| Proceso | Qué hace | Qué toca | Cuándo |
|---|---|---|---|
| Generar el diccionario desde la base | consultas de solo lectura a `mod_rep.rep.RREGREP01` y a las bases (dentro de la API; hasta un par de minutos) | `data/outputs/diccionario/generado/diccionario.json` | la primera vez, o cuando cambien procedimientos, tablas o reportes |
| Validar las bases de datos | a cada servidor del `.env` (mish, slc, rcc), a la vez, `@@SERVERNAME`/usuario/versión y el estado de cada base de `sys.databases` | nada | antes de generar o cuando algo no conecta; reemplaza a la antigua página Configuración › Bases de datos |

Solo se corre uno a la vez; el botón se deshabilita y, si dos peticiones llegan juntas, la segunda recibe «Ya hay un proceso del diccionario en curso». Al terminar «Generar», las pantallas muestran lo nuevo en la siguiente consulta (la API relee el archivo cuando cambia su fecha).

### Cómo se lee el log de «Generar»

`▶` inicia un paso y `✓` lo termina (entre ellos «Analizando el código de N procedimientos»); `✗ base: …` es una base que no contestó (se sigue con las demás) y `AVISO` una base cuya estructura o cuyo código no se pudo leer (el diccionario sale igual, con lo que dice el motor). Si una base dice «rechazó el inicio de sesión», la cuenta del `.env` no tiene acceso a esa base: pídelo al administrador del servidor; sus procedimientos quedan «pendiente». Si ninguna contesta no se guarda nada. La generación tiene un tope de 10 minutos en total (`PRESUPUESTO` en `construir.py`): pasado el tiempo deja de pedir bases (`✗ Tiempo agotado`), y guarda lo que ya contestó si alguna respondió.

## Qué hacer con lo que muestra

- **Fecha por confirmar** (Resumen › lo que aporta): abre la tabla, mira la columna candidata y confírmala en `src/modulos/reportes/dominio/tablas.py` (`confianza` → `confirmada`); luego `python governance/scripts/generar_inventario.py`.
- **Tablas que el MIS usa y tú no**: candidatas para un reporte nuevo; su detalle trae las fechas disponibles para el corte.
- **Calidad del código**: `parametros-de-mas`/`parametros-faltantes` (el catálogo envía distinta cantidad de parámetros que declara el SP: el reporte falla al ejecutarse), `columna-inexistente` (el código usa una columna que la tabla real no tiene), `sql-dinamico` (hay tablas que nadie ve: revisar a mano), `columna-sin-resolver` (columna sin calificar con varias tablas posibles) y las de nivel `info` (orientativas).
- **Errores de calidad**: `sp-inexistente` y `tabla-inexistente` pueden ser reales o un permiso que falta (la cuenta no los ve); `objeto-no-resuelto` es un aviso: el motor no pudo decir qué es (otra base, sinónimo).

### Cómo se lee «Validar las bases de datos»

El log se va escribiendo mientras corre (cada servidor aparece al terminar, hasta 15 s en total). Por servidor: `✓ mish (…): conexión correcta · 120 ms · SQL Server 15.0… · usuario …` y debajo cada base que usan los reportes (`BASES_DE`): `✓ storage` en línea, `✗ staging: OFFLINE` fuera de línea (el proceso termina con error), `AVISO appj: no aparece…` si el servidor no la muestra (sin permiso para verla o servidor vinculado: no se da por caída). Un servidor que no contesta en 15 s sale como `✗ … sin respuesta` (casi siempre VPN). La pestaña **Script** muestra las dos consultas, las bases esperadas y el código Python que las ejecuta.

## Problemas conocidos

| Síntoma | Causa | Qué hacer |
|---|---|---|
| Aviso «No pude leer `mod_rep.rep.RREGREP01`» | sin VPN o sin permiso de lectura sobre `rep.RREGREP01` | conectar la VPN y recargar (la falla se recuerda 60 s); mientras tanto se usa el diccionario guardado |
| «N reportes están en la base y aún no en el diccionario» | alguien dio de alta un RCODREP nuevo | ejecutar «Generar el diccionario desde la base» |
| El Resumen dice «Todavía no hay detalle de tablas ni columnas» | aún no se generó el diccionario | Procesos › Generar el diccionario desde la base |
