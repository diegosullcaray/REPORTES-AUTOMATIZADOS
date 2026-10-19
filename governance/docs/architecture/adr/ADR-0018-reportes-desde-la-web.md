# ADR-0018: Alta, edición y baja de reportes desde la web

- Estado: Vigente
- Fecha: 2026-10-18

## Contexto

Crear un reporte a mano son cinco pasos coordinados: el módulo `.py`, su test, y las líneas de `dominio/reportes.py`, `dominio/tablas.py` y `dominio/reglas_fecha.py`. La web lo hace en un solo gesto (**Nuevo reporte** dentro de un grupo), y también crea grupos, edita el Script de un reporte y borra reportes y grupos. Eso escribe código y registro en disco y ejecuta T-SQL contra bases reales, así que necesita reglas propias. Las auditorías de octubre ([evidencia](../../evidence/quality/auditorias-2026-10.md)) las fueron fijando; este ADR las junta.

## Decisión

**Alta (`crear_reporte.crear`).**
1. Pide solo nombre (comando), número del legado y descripción. La **base** sale del `use <base>;` del T-SQL y el servidor, de la base ([ADR-0006](./ADR-0006-conexion-es-servidor-base-por-reporte.md)); la **frecuencia** es la del grupo. Sin T-SQL se crea con `PLANTILLA_SQL` (un `select 1 as pendiente`) para completarlo en la pestaña Script.
2. El T-SQL se valida como lo hará el ejecutor: sin fechas literales (solo tokens `@@F@@`…), con al menos un token, una sola conexión, y **de solo lectura** (`rechazar_escritura`: se rechazan `INSERT`, `UPDATE`, `DELETE`, `SELECT INTO`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE` y `MERGE` salvo sobre tablas temporales `#` o variables `@`; el texto entre comillas y los comentarios no cuentan). Un reporte que necesite escribir en la base es del legado, con `escribe_en_bd` y `--confirmar-escritura`.
3. Las tablas nuevas entran al registro como `referencia / por_confirmar`: no se verifican por fecha hasta que alguien confirme su columna en `tablas.py`. El ejecutor lo dice con un `AVISO: sin control de fecha…`.
4. Mientras el SQL del lote contenga la plantilla, `ejecuciones.argumentos` rechaza ejecutarlo («Completa el T-SQL…»).

**Marca de origen.** Todo módulo creado así lleva «Creado desde la web» en su docstring (`MARCA_WEB`). Solo esos se pueden **borrar** desde la web, y la pestaña Script no deja *agregar* esa marca a otro reporte: los del legado no se eliminan.

**Edición del Script (`catalogo.guardar_script`).** Solo guarda si el código compila; si lleva la marca, su `SQL = r"""…"""` también pasa por `rechazar_escritura`. Después se descarta la copia en memoria del módulo (`catalogo.olvidar`: `lote.cache_clear()` y `sys.modules.pop`), para que la API vea el código nuevo sin reiniciar.

**Baja (`crear_reporte.eliminar`).** Solo con la marca y sin ejecuciones en cola o en curso. Quita el módulo, su test y sus líneas del registro (si algo no casa, no toca nada); las filas de `_FILAS` se conservan porque otro reporte puede usarlas, y se limpia la carpeta del grupo propio si solo queda su `__init__.py`. Un grupo solo se elimina vacío.

**Consistencia.** Alta y baja de reportes y grupos, y las etiquetas, comparten un candado (`aplicacion/exclusivo.py`, reentrante): van de a una. Si falla la escritura de algún archivo del registro, se restauran los textos originales y se borran el módulo y el test recién creados.

## Consecuencias

- Crear un reporte desde la web no puede escribir en las bases; la confirmación de escritura sigue siendo exclusiva del legado.
- La pestaña Script sigue siendo código Python arbitrario para quien tenga sesión ([SEC-011](../../security/findings.md)): el control es el acceso a la web, que escucha solo en local.
- Cada alta/baja deja archivos que se versionan: tras crear o borrar hay que correr `generar_inventario.py` y `verificar.py` antes de commitear ([runbook](../../development/runbooks/reporte-desde-la-web.md)).
- Los grupos propios viven en `catalogo/grupos/<id>` y son siempre mensuales (`crear_grupo`).
