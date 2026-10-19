# Diccionario de datos de los reportes MIS (contrato del archivo)

El repo hermano `DICCIONARIO` documenta qué procedimiento almacenado (SP) ejecuta cada reporte del MIS (`RCODREP`), qué tablas usa y qué columnas. Esta app **solo lo lee**, desde el módulo `diccionario` ([ADR-0017](../architecture/adr/ADR-0017-modulo-diccionario.md)). La fuente de verdad es ese repo (su AGENTS.md: gana la fuente; lo derivado se regenera, no se edita).

**Archivo:** `<DICCIONARIO_DIR>/diccionario/diccionario.json` (por defecto, la carpeta `DICCIONARIO` junto a este repo). Se genera con `npm run generar` en ese repo.

## De dónde sale cada cosa

| Dato | Fuente |
|---|---|
| **Catálogo de reportes** (código, descripción, procedimiento, parámetros) | `mod_rep.rep.RREGREP01` en vivo: `RCODREP`, `RDESREP` y `RTPREP` (JSON `{"name": "<base>.<esquema>.<SP>", "params": [{"order": n, "name": "…"}]}`). Un `RTPREP` ilegible deja el reporte sin procedimiento. Sin conexión: `reportes[]` del `diccionario.json` |
| Procedimientos, tablas, columnas, hallazgos y pantallas del front (`front[]`) | `diccionario.json` |

## Qué se consume del `diccionario.json`

| Clave | Campos que usa la app |
|---|---|
| `reportes[]` | `codigo` (RCODREP), `descripcion`, `procedimiento` (`base.esquema.nombre`), `parametros[]`, `front[]` (pantallas de MIS-angular-front que lo piden) |
| `procedimientos[]` | `nombre`, `base`, `estado`, `reportes[]`, `parametros[]` (`nombre`, `tipo`, `porDefecto`, `salida`), `resultados[][]`, `invoca[]`, `tablas[]` (`nombre`, `usos[]`, `columnas[]` con `nombre` y `confianza`) |
| `tablas[]` | `nombre` (`base.esquema.tabla`), `base`, `tipo`, `existe`, `descripcion`, `ficha`, `columnas[]` (`nombre`, `tipo`, `aceptaNulos`, `confianza`, `procedimientos[]`) |
| `hallazgos[]` | `nivel` (`error`/`aviso`/`info`), `regla`, `origen` (`produccion`/`catalogo`/`analisis`), `objeto`, `detalle`, `enLineaBase` |

Valores que la web interpreta: `estado` de un SP = `validado` · `extraido` · `pendiente` (un reporte cuyo SP no está en la lista se muestra «sin procedimiento»); `confianza` de una columna = `exacta` · `confirmada` · `motor` · `inferida`; un hallazgo `enLineaBase: false` de nivel `error` es un **error nuevo**.

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
