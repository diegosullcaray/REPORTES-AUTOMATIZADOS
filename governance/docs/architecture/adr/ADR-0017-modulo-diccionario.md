# ADR-0017: Módulo Diccionario (diccionario de datos de los reportes MIS)

- Estado: Vigente
- Fecha: 2026-10-18

## Contexto

El repo hermano `DICCIONARIO` documenta, para cada reporte del MIS (`RCODREP`), qué procedimiento almacenado ejecuta, qué tablas usa y qué columnas de cada una; su producto es `diccionario/diccionario.json` ([contrato](../../data/diccionario.md)). Esa información responde preguntas que esta app se hace a diario: ¿qué columna de fecha tiene esta tabla? ¿qué otras tablas leen los reportes del MIS? Hasta ahora había que abrir los `.md` del otro repo a mano y lanzar sus comandos desde una consola.

## Decisión

Un módulo nuevo del monolito ([ADR-0016](./ADR-0016-monolito-modular.md)), `modulos/diccionario/`, con las cuatro capas:

| Capa | Contenido |
|---|---|
| `dominio/columnas.py` | `es_columna_fecha` (heurística por el nombre) y `PROCESOS`: la lista cerrada de procesos que se pueden lanzar |
| `aplicacion/` | `dto.py`, `puertos.py` (`Lector`, `Catalogo`, `Lanzador`) y los casos de uso `diccionario.py` (consultas y cruce con el registro de tablas) y `procesos.py` |
| `infraestructura/` | `lector.py` (lee el `diccionario.json`, lo relee solo si cambió su fecha de modificación), `catalogo_bd.py` (el catálogo de reportes desde `mod_rep.rep.RREGREP01`) y `lanzador.py` (subproceso) |
| `interfaces/web/` | vistas Django bajo `/api/diccionario/…` |

Reglas:

1. **Solo lectura.** El módulo nunca escribe `diccionario.json` ni nada del repo `DICCIONARIO` (lo único que lo cambia es un proceso lanzado a propósito, regla 3) ni nada en SQL Server.
2. **Dependencia permitida: `diccionario → reportes`** (usa `reportes.dominio.tablas`: `TABLAS` y `USO`, para el cruce). `reportes` no conoce a `diccionario`. Está en `DEPENDE` de `validar_gobernanza.py`.
3. **Procesos: lista cerrada y de a uno.** Solo `generar` (`npm run generar`), `verificar` (`npm run verificar`) y `test` (`npm test`), siempre en la carpeta del repo `DICCIONARIO`, más `bases`, que corre dentro de la API: a cada servidor del `.env` (mish, slc, rcc), a la vez y con un tope de 15 s, le pregunta quién es y con qué usuario entra (`@@SERVERNAME`, `SUSER_SNAME()`, versión) y el estado de sus bases (`sys.databases`), y las compara con las que usan los reportes (`BASES_DE`). Va escribiendo el log mientras corre. Sale con error si un servidor no conecta o una base no está `ONLINE`; una base que no aparece es solo un aviso. Reemplaza a la página «Bases de datos» de Configuración, que se retiró junto con `GET /api/servidores` y `POST /api/servidores/<n>/prueba`. El comando sale de `PROCESOS`, nunca de la petición, y se lanza sin shell. Ninguno se conecta a SQL Server. La extracción desde la base (`bd.py`) **no** se ofrece: escribe en el otro repo con credenciales y su propia guía pide revisar el diff después.
4. **Entorno mínimo para el subproceso.** `lanzador.py` pasa solo `PATH`, `PATHEXT`, `SYSTEMROOT`, `COMSPEC`, `TEMP`, `TMP`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA` y `HOME`. El repo `DICCIONARIO` es otro código y no debe ver las claves de esta API (SMTP, bases, Google, `WEB_CLAVE`). Los nombres van en mayúsculas porque en Windows Python los entrega así, y `node` no arranca sin `SYSTEMROOT` ([incidente de la auditoría](../../evidence/quality/auditorias-2026-10.md)).
5. **Uno a la vez.** La comprobación «¿hay uno en curso?» y el alta ocurren bajo el mismo candado dentro del lanzador; dos peticiones casi juntas no lanzan dos procesos. El estado y el log quedan en `data/outputs/diccionario/` (últimas 50 fichas); un proceso que quedó «ejecutando» tras reiniciar la API se muestra como error.
6. **El catálogo de reportes sale de la base.** La lista de reportes (RCODREP, descripción, procedimiento y parámetros) se lee en vivo de `mod_rep.rep.RREGREP01` (`RCODREP`, `RDESREP`, `RTPREP`, un JSON con el SP y sus parámetros), no del `diccionario.json`: esa tabla es la que usa el backend del MIS (Ant) y la que manda. Es un único `SELECT … WITH (NOLOCK)` por `core.bd` (servidor de `mod_rep` = `mish`), con 10 s de espera, caché de 60 s por proceso (también de la falla, para no esperar en cada pantalla) y sin ninguna escritura. Del `diccionario.json` se siguen tomando lo que la tabla no tiene: procedimientos, tablas, columnas, pantallas del front y hallazgos. Sin conexión (sin VPN, sin permisos, esquema distinto) se usa el catálogo del `diccionario.json` y el Resumen lo dice con el motivo; los reportes que están en la base y aún no en el diccionario (o al revés) se listan como `nuevos` / `retirados`.
7. **Dónde está el diccionario.** La carpeta `DICCIONARIO` junto a este repo, o `DICCIONARIO_DIR` en el `.env`. Si falta, la API responde 404 con esa pista.

Cada proceso tiene su **detalle** (`/diccionario/procesos/<id>`, pestañas en la URL): *General* (qué hace, qué toca, ejecutar con confirmación y la última salida), *Ejecuciones* (su historial con el log), *Script* (el script de `package.json` y el código de los archivos que ejecuta, solo los que están dentro del repo; para `bases`, las consultas y el código que las ejecuta) y *Archivos* (lo que deja: se pueden ver los de texto; solo los que declaran los patrones de `PROCESOS`, nunca una ruta libre). Las tarjetas de la lista llevan a esos detalles.

Web: grupo «Diccionario» en el menú lateral con **Resumen** (gráficos con ECharts: avance por base, calidad y lo que aporta a tus reportes), **Reportes del MIS** (una tarjeta por base de datos y, dentro, las pestañas *Procedimientos* y *Tablas que ocupa*) y **Procesos**. Los detalles de un reporte y de una tabla cuelgan de ahí. Se usa la librería `echarts` (módulos `BarChart`, ejes, tooltip, leyenda y render SVG), con los colores de los tokens `--mis-*` resueltos en el navegador (`components/grafico.tsx`).

## Consecuencias

- El cruce con el registro dice qué columnas de fecha confirmar (`por_confirmar`), qué tablas propias no tienen ficha y qué tablas ya usa el MIS que aún no usan los reportes propios: candidatas a reportes nuevos.
- La calidad que muestra la web es la del otro repo: si su `verificar` falla (hoy por enlaces rotos en `modificaciones/nueva tarea`), la pantalla de Procesos lo dice con «Con error»; no es un fallo de esta app.
- `generar` reescribe archivos de `DICCIONARIO`: se revisa su `git diff` después.
- Dependencia nueva del frontend: `echarts`. Quitar el módulo es borrar `modulos/diccionario/`, su línea en `config/` y el grupo del menú.

Runbook: [Diccionario](../../development/runbooks/diccionario.md).
