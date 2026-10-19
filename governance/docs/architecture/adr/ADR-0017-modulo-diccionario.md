# ADR-0017: Módulo Diccionario (diccionario de datos de los reportes MIS)

- Estado: Vigente
- Fecha: 2026-10-18

## Contexto

Cada reporte del MIS (`RCODREP`) ejecuta un procedimiento almacenado que usa tablas y columnas. Esa información responde preguntas que esta app se hace a diario: ¿qué columna de fecha tiene esta tabla? ¿qué otras tablas leen los reportes del MIS? Antes salía de un repo hermano (`DICCIONARIO`) que había que clonar y cuyos comandos se lanzaban desde una consola. **Desde 2026-10-18 esta app no depende de ese repo**: genera su propio diccionario desde SQL Server y tiene sus propios procesos ([contrato](../../data/diccionario.md)).

## Decisión

Un módulo nuevo del monolito ([ADR-0016](./ADR-0016-monolito-modular.md)), `modulos/diccionario/`, con las cuatro capas:

| Capa | Contenido |
|---|---|
| `dominio/` | `columnas.py` (`es_columna_fecha`, heurística por el nombre, y `PROCESOS`: la lista cerrada), `tsql.py` (el analizador estático del código de un SP) y `armado.py` (`armar`: función pura que junta lo que responde SQL Server y el análisis del código en el diccionario) |
| `aplicacion/` | `dto.py`, `puertos.py` (`Lector`, `Catalogo`, `Generador`, `Lanzador`) y los casos de uso `diccionario.py` (consultas y cruce con el registro de tablas), `construir.py` (generar el diccionario) y `procesos.py` |
| `infraestructura/` | `lector.py` (guarda y lee el diccionario; lo relee solo si cambió su fecha), `catalogo_bd.py` (el catálogo desde `mod_rep.rep.RREGREP01`), `generador_bd.py` (las consultas de metadatos a cada base) y `lanzador.py` (estado y log de cada proceso) |
| `interfaces/web/` | vistas Django bajo `/api/diccionario/…` |

Reglas:

1. **Solo lectura de la base.** El módulo nunca escribe nada en SQL Server. Lo único que escribe es el diccionario, en `data/outputs/diccionario/generado/diccionario.json`, con reemplazo atómico.
2. **Dependencia permitida: `diccionario → reportes`** (usa `reportes.dominio.tablas`: `TABLAS` y `USO`, para el cruce). `reportes` no conoce a `diccionario`. Está en `DEPENDE` de `validar_gobernanza.py`.
3. **Procesos propios: lista cerrada y de a uno.** Solo `construir` (generar el diccionario) y `bases` (validar las bases). Corren dentro de la API, sin subprocesos ni shell; el proceso sale de `PROCESOS`, nunca de la petición. `bases` le pregunta a cada servidor del `.env` (mish, slc, rcc), a la vez y con un tope de 15 s, quién es y con qué usuario entra (`@@SERVERNAME`, `SUSER_SNAME()`, versión) y el estado de sus bases (`sys.databases`), y las compara con las que usan los reportes (`BASES_DE`). Sale con error si un servidor no conecta o una base no está `ONLINE`; una base que no aparece es solo un aviso. Reemplaza a la página «Bases de datos» de Configuración.
4. **Uno a la vez.** La comprobación «¿hay uno en curso?» y el alta ocurren bajo el mismo candado dentro del lanzador; dos peticiones casi juntas no lanzan dos procesos. El estado y el log (que se escribe mientras corre) quedan en `data/outputs/diccionario/` (últimas 50 fichas); un proceso que quedó «ejecutando» tras reiniciar la API se muestra como error.
5. **El catálogo de reportes sale de la base.** La lista de reportes (RCODREP, descripción, procedimiento y parámetros) se lee en vivo de `mod_rep.rep.RREGREP01` (`RCODREP`, `RDESREP`, `RTPREP`, un JSON con el SP y sus parámetros): esa tabla es la que usa el backend del MIS (Ant) y la que manda. Es un único `SELECT … WITH (NOLOCK)` por `core.bd` (servidor de `mod_rep` = `mish`), con 10 s de espera, caché de 60 s por proceso (también de la falla) y sin ninguna escritura. Los nombres se leen sin corchetes. Si más de la mitad de las filas no trae procedimiento se trata como error (cambió el formato). Sin conexión se usan los reportes del diccionario guardado y el Resumen lo dice con el motivo; los que están en la base y aún no en el diccionario (o al revés) se listan como `nuevos` / `retirados`.
6. **Generar desde la base (`construir`).** Por cada base de SP del catálogo corre consultas de solo lectura: `sys.dm_sql_referenced_entities` y `sys.sql_expression_dependencies` (qué tabla y columna toca cada SP y si lee o escribe), `sys.parameters` (parámetros), `sys.sql_modules` (el **código** de cada SP) y, por cada base de las tablas halladas, `INFORMATION_SCHEMA` (tipo, nulos y existencia real). Los nombres viajan como parámetros `?`, nunca pegados al texto. Una base que no contesta se avisa y no impide generar las demás; si ninguna contesta, no se guarda nada y queda el diccionario anterior. **Análisis del código** (`dominio/tsql.py`, un port del analizador del repo DICCIONARIO, verificado contra sus 269 procedimientos con cero diferencias): lee el texto de cada SP y saca tablas con su operación, columnas (`exacta` si van calificadas, `inferida` si hay una sola tabla), SP invocados, columnas que devuelve, parámetros con su valor por defecto y SQL dinámico. El **motor manda y el análisis complementa**: una columna vista por los dos queda `confirmada`; donde el motor no llega (el SP no compila contra el esquema actual) el análisis aporta las tablas y columnas. El código **no se guarda**: solo su análisis, y ni el log ni el diccionario lo repiten (un SP puede traer una credencial embebida). **Límites:** el análisis es una heurística y no ve el SQL dinámico (se avisa con `sql-dinamico`); una cuenta sin `VIEW DEFINITION` ve como inexistente lo que no puede ver (los mensajes lo dicen) y recibe el código vacío, así que ese SP queda sin análisis. Estados de un SP: `validado` (el motor resolvió columnas), `extraido` (existe, pero el motor no llegó a las columnas), `pendiente` (no existe o su base no contestó) y `sin extraer` (está en el catálogo y el diccionario aún no lo tiene). Reglas de calidad: `sp-inexistente`, `tabla-inexistente`, `columna-inexistente`, `parametros-de-mas`, `parametros-faltantes` (error); `motor-con-error`, `esquema-distinto`, `sql-dinamico`, `columna-sin-resolver`, `columna-inferida-inexistente`, `discrepancia-motor` (aviso); `tabla-de-trabajo`, `parametro-nombre-distinto`, `analisis-aproximado`, `varios-resultados` (info).
7. **Sin diccionario guardado la web igual funciona** con solo el catálogo de reportes y un aviso para generarlo.

Cada proceso tiene su **detalle** (`/diccionario/procesos/<id>`, pestañas en la URL): *General* (qué hace, qué toca, ejecutar con confirmación y la última salida), *Ejecuciones* (su historial con el log) y *Script* (las consultas SQL, el analizador y el código Python que ejecuta). Las tarjetas de la lista llevan a esos detalles.

Web: grupo «Diccionario» en el menú lateral con **Resumen** (gráficos con ECharts: avance por base, calidad y lo que aporta a tus reportes), **Reportes del MIS** (una tarjeta por base de datos y, dentro, las pestañas *Procedimientos* y *Tablas que ocupa*) y **Procesos**. Los detalles de un reporte y de una tabla cuelgan de ahí. Se usa la librería `echarts` (módulos `BarChart`, ejes, tooltip, leyenda y render SVG), con los colores de los tokens `--mis-*` resueltos en el navegador (`components/grafico.tsx`).

## Consecuencias

- El cruce con el registro dice qué columnas de fecha confirmar (`por_confirmar`), qué tablas propias no tienen ficha y qué tablas ya usa el MIS que aún no usan los reportes propios: candidatas a reportes nuevos.
- La calidad sale de los metadatos de SQL Server y del análisis del código: sirve para encontrar procedimientos, tablas o columnas rotos y parámetros que no cuadran; es una heurística, no un compilador.
- Las consultas se probaron con datos de prueba y se afinan con la primera ejecución real (ver los avisos `objeto-no-resuelto`).
- Dependencia nueva del frontend: `echarts`. Quitar el módulo es borrar `modulos/diccionario/`, su línea en `config/` y el grupo del menú.

Runbook: [Diccionario](../../development/runbooks/diccionario.md).
