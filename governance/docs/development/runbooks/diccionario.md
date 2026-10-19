# Diccionario — cómo usarlo y mantenerlo al día

Decisión y alcance: [ADR-0017](../../architecture/adr/ADR-0017-modulo-diccionario.md). Contrato del archivo que lee: [diccionario de datos](../../data/diccionario.md).

## Antes de empezar

El **catálogo de reportes** se lee en vivo de `mod_rep.rep.RREGREP01` (hace falta red/VPN al servidor `mish`; si no hay, el Resumen avisa «No pude leer…» y usa el `diccionario.json`). Lo demás (procedimientos, tablas, columnas) viene del `diccionario.json`.

1. El repo `DICCIONARIO` clonado **junto a este** (`…/DD/DICCIONARIO` y `…/DD/REPORTES-AUTOMATIZADOS`), o `DICCIONARIO_DIR` en `backend/.env` con su ruta. Sin él la web responde «No encontré el diccionario en …».
2. Para los procesos: `node` y `npm` en el `PATH` de quien arranca la API (Node 20+). Si falta, el log del proceso dice «No encuentro npm».

## Las pantallas (menú lateral › Diccionario)

| Pantalla | Para qué |
|---|---|
| **Resumen** (`/diccionario`) | Tres gráficos: *avance de la documentación* por base (validados · extraídos · pendientes), *calidad* (errores y avisos por regla) y *lo que aporta a tus reportes*: cuántas de tus tablas tienen ficha, las columnas de fecha por confirmar y las tablas que más reportes del MIS leen y los tuyos no (pulsa una barra para abrirla). Cada gráfico trae «Ver como tabla» |
| **Reportes del MIS** (`/diccionario/reportes`) | Una tarjeta por base de datos. Al entrar (`?base=`): pestaña **Procedimientos** (con los reportes que los ejecutan) y pestaña **Tablas** que ocupa (las que guarda y las que sus procedimientos leen de otras bases; filtro «viven en esta base» / «de otras») |
| Detalle de un reporte | Procedimiento, parámetros, tablas con las columnas que usa (las de fecha resaltadas), pantallas del front y hallazgos |
| Detalle de una tabla | Columnas, qué reportes del MIS la leen y **cómo la registran tus reportes** (`tablas.py`: tipo, columna de fecha, confianza) |
| **Procesos** (`/diccionario/procesos`) | Dos pestañas (`?tab=`): **Procesos** (una tarjeta por proceso, con su última ejecución; entra a uno para verlo al detalle) e **Historial** (todas las ejecuciones, con su log en vivo) |
| Detalle de un proceso (`/diccionario/procesos/<id>`) | Pestañas **General** (qué hace, ejecutar con confirmación, última salida), **Ejecuciones** (las de ese proceso), **Script** (su código) y **Archivos** (lo que genera: se abren los `.md` y `.json`) |

## Los procesos

| Proceso | Comando (en el repo `DICCIONARIO`) | Qué toca | Cuándo |
|---|---|---|---|
| Regenerar el diccionario | `npm run generar` | reescribe `diccionario/`, `errores/`, `extraccion/sql/` y `.claude/` | después de cambiar la fuente (`extraccion/fuente/`, procedimientos extraídos) |
| Verificar la calidad | `npm run verificar` | nada | antes de commitear allá; falla ante errores nuevos o algo roto |
| Probar el analizador T-SQL | `npm test` | nada | tras tocar el analizador |
| Validar las bases de datos | dentro de la API: a cada servidor del `.env` (mish, slc, rcc), a la vez, `@@SERVERNAME`/usuario/versión y el estado de cada base de `sys.databases` | nada | antes de regenerar o cuando algo no conecta; reemplaza a la antigua página Configuración › Bases de datos (retirada el 2026-10-18) |

Solo se corre uno a la vez; el botón se deshabilita y, si dos peticiones llegan juntas, la segunda recibe «Ya hay un proceso del diccionario en curso». Después de `generar`, el Resumen se actualiza solo (la API relee el archivo cuando cambia su fecha). **Revisa el `git diff` de `DICCIONARIO` después de `generar`.**

La **extracción desde SQL Server** (`python extraccion/herramientas/bd.py …`) no se lanza desde la web: se hace en una consola, siguiendo la guía de ese repo.

## Qué hacer con lo que muestra

- **Fecha por confirmar** (Resumen › lo que aporta): abre la tabla, mira la columna candidata y confírmala en `src/modulos/reportes/dominio/tablas.py` (`confianza` → `confirmada`); luego `python governance/scripts/generar_inventario.py`.
- **Tablas que el MIS usa y tú no**: candidatas para un reporte nuevo; su detalle trae las fechas disponibles para el corte.
- **Errores «nuevos»** de calidad: son del repo `DICCIONARIO` (SP o tablas que cambiaron en producción); se corrigen allá (su carpeta `errores/` dice dónde), no aquí.

### Cómo se lee «Validar las bases de datos»

El log se va escribiendo mientras corre (cada servidor aparece al terminar, hasta 15 s en total). Por servidor: `✓ mish (…): conexión correcta · 120 ms · SQL Server 15.0… · usuario …` y debajo cada base que usan los reportes (`BASES_DE`): `✓ storage` en línea, `✗ staging: OFFLINE` fuera de línea (el proceso termina con error), `AVISO appj: no aparece…` si el servidor no la muestra (sin permiso para verla o servidor vinculado: no se da por caída). Un servidor que no contesta en 15 s sale como `✗ … sin respuesta` (casi siempre VPN). La pestaña **Script** muestra las dos consultas, las bases esperadas y el código Python que las ejecuta.

## Problemas conocidos

| Síntoma | Causa | Qué hacer |
|---|---|---|
| Aviso «No pude leer `mod_rep.rep.RREGREP01`» | sin VPN o sin permiso de lectura sobre `rep.RREGREP01` | conectar la VPN y recargar (la falla se recuerda 60 s); mientras tanto se usa el `diccionario.json` |
| «N reportes están en la base y aún no en el diccionario» | alguien dio de alta un RCODREP nuevo | extraer su SP y regenerar en el repo `DICCIONARIO` (su guía) |
| El proceso termina con código 134 y `Assertion failed: ncrypto::CSPRNG` | `node` no arranca en Windows sin `SYSTEMROOT` | ya cubierto: el lanzador la conserva (en mayúsculas). Si reaparece, revisa `_ENTORNO_MINIMO` de `infraestructura/lanzador.py` |
| `Verificar` termina «Con error» | el repo `DICCIONARIO` tiene enlaces rotos (p. ej. `modificaciones/nueva tarea/variables.md`) | corregir esos enlaces en ese repo; no es un fallo de esta app |
| Gráficos vacíos o 404 | no está la carpeta `DICCIONARIO` | ver «Antes de empezar» |
