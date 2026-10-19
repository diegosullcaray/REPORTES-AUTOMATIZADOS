# Diccionario de datos de los reportes MIS (contrato del archivo)

El diccionario documenta qué procedimiento almacenado (SP) ejecuta cada reporte del MIS (`RCODREP`), qué tablas usa y qué columnas. Lo **genera esta app desde SQL Server** (proceso «Generar el diccionario desde la base», [ADR-0017](../architecture/adr/ADR-0017-modulo-diccionario.md)) y el resto de la app solo lo lee.

**Archivo:** `data/outputs/diccionario/generado/diccionario.json` (no versionado; se reemplaza entero y de forma atómica en cada generación).

## De dónde sale cada cosa

| Dato | Fuente |
|---|---|
| **Catálogo de reportes** (código, descripción, procedimiento, parámetros) | `mod_rep.rep.RREGREP01` en vivo: `RCODREP`, `RDESREP` y `RTPREP` (JSON `{"name": "<base>.<esquema>.<SP>", "params": [{"order": n, "name": "…"}]}`). Un `RTPREP` ilegible deja el reporte sin procedimiento. Sin conexión: `reportes[]` del diccionario guardado |
| Procedimientos, tablas, columnas y hallazgos | metadatos de SQL Server (`sys.dm_sql_referenced_entities`, `sys.sql_expression_dependencies`, `sys.parameters`, `INFORMATION_SCHEMA`) más el análisis estático del código de cada SP (`sys.sql_modules`, `dominio/tsql.py`), de cada base |

## Qué contiene el `diccionario.json`

| Clave | Campos que usa la app |
|---|---|
| `reportes[]` | `codigo` (RCODREP), `descripcion`, `procedimiento` (`base.esquema.nombre`), `parametros[]` |
| `procedimientos[]` | `nombre`, `base`, `estado`, `reportes[]`, `parametros[]` (`nombre`, `tipo`, `porDefecto`, `salida`), `resultados[][]`, `invoca[]`, `tablas[]` (`nombre`, `usos[]`, `columnas[]` con `nombre` y `confianza`) |
| `tablas[]` | `nombre` (`base.esquema.tabla`), `base`, `tipo`, `existe`, `descripcion`, `ficha`, `columnas[]` (`nombre`, `tipo`, `aceptaNulos`, `confianza`, `procedimientos[]`) |
| `hallazgos[]` | `nivel` (`error`/`aviso`/`info`), `regla` (ver ADR-0017), `origen` (`produccion`/`analisis`), `objeto`, `detalle` |

Valores que la web interpreta: `estado` de un SP = `validado` · `extraido` · `pendiente` (un reporte con SP en el catálogo que el diccionario aún no tiene se muestra «sin extraer», y uno sin SP, «sin procedimiento»); `confianza` de una columna = `confirmada` (la ven el motor y el análisis del código) · `motor` · `exacta` (el código la califica con tabla o alias) · `estructura` (solo la tabla real la desempata) · `inferida` (el código, sin calificar, con una sola tabla posible). `resultados[]` de un SP son las columnas de sus SELECT finales (del análisis del código).

## Cómo se cruza con este proyecto

El nombre de una tabla se compara **sin distinguir mayúsculas** con el registro de [`dominio/tablas.py`](./tables-inventory.md) (`TABLAS`, `USO`):

| Cruce | Resultado |
|---|---|
| tabla del registro con ficha | cobertura («25 de 74 tablas tuyas están en el diccionario») |
| tabla del registro `por_confirmar` (o sin columna de fecha siendo `historica`/`stock`) con columnas de aspecto fecha en el diccionario | **fecha por confirmar**: se listan las candidatas |
| columna de fecha registrada que ningún SP del diccionario usa | aviso para verificar que exista |
| tabla del diccionario que existe y no está en el registro | **candidata** para un reporte nuevo, ordenada por cuántos reportes del MIS la leen |

«Columna de fecha» es una **heurística por el nombre** (`fec`, `fch`, `date`, `periodo`, `dia`): sugiere, no decide. Confirmarla es trabajo de quien conoce la tabla ([stewardship](./stewardship.md)).

## Lo que la app no hace

- No inventa significado: `descripcion` de una tabla o columna es `null` hasta que alguien la documente allá, y la web lo dice.
- No escribe el archivo ni corrige hallazgos: los errores de producción se reportan al dueño del SP.
- No ejecuta ningún SP ni escribe en SQL Server: su única consulta es el `SELECT … WITH (NOLOCK)` de `rep.RREGREP01`.
