# Auditorías de código — octubre 2026

Cinco pasadas de revisión (corrección, seguridad, carga, pruebas, velocidad y código sobrante) sobre el repo, hechas el 2026-10-18 con la skill `ponytail-audit`. Cada hallazgo tenía un caso concreto; lo que sigue es su estado. Los de seguridad tienen además su ficha en [findings](../../security/findings.md); las reglas que dejaron están en [ADR-0018](../../architecture/adr/ADR-0018-reportes-desde-la-web.md) y [ADR-0017](../../architecture/adr/ADR-0017-modulo-diccionario.md).

Estado de las compuertas al cierre de las correcciones: `python governance/scripts/verificar.py` en verde (cero hallazgos nuevos, inventario al día, 454 pruebas); `tsc`, `eslint`, `next build` y las pruebas del frontend en verde.

## 1 · Repo completo (alta/baja de reportes, sesión, ejecuciones)

| Hallazgo | Estado |
|---|---|
| La web escuchaba en toda la red | Cerrado — SEC-005 |
| Reporte de la web con T-SQL de escritura sin confirmación | Cerrado — SEC-006 |
| Plantilla sin completar generaba un Excel con una fila inútil | Cerrado — la ejecución se rechaza mientras exista `select 1 as pendiente` |
| Cambiar la contraseña no cerraba las sesiones | Cerrado — SEC-007 |
| Alta/baja podía dejar el registro roto o pisarse | Cerrado — candado + restauración (`aplicacion/exclusivo.py`) |
| Borrar un reporte con ejecución en curso dejaba la cola trabada | Cerrado — se rechaza el borrado |
| La marca «Creado desde la web» se podía copiar a un reporte del legado | Cerrado — el Script no deja agregarla |
| Cada consulta del historial leía todos los JSON | Cerrado — caché por fecha de modificación (`cola_ejecuciones._cache`) |
| Carpetas vacías tras borrar reportes de un grupo propio | Cerrado |

## 2 · Google, MCP, IA, correo, verificación de tablas

| Hallazgo | Estado |
|---|---|
| Tras editar el Script la API seguía con el módulo viejo (y con la plantilla) | Cerrado — `catalogo.olvidar` |
| La pestaña «Conectar» daba una ruta MCP que ya no existe y `python` global (sin dependencias) | Cerrado — `sys.executable` y la ruta bajo `modulos/` |
| Un reporte de la web con tablas nuevas corría sin control de fecha y sin aviso | Cerrado — `AVISO: sin control de fecha…` |
| Documentos con rutas anteriores al monolito modular | Cerrado |
| El servidor MCP de envío escribía a cualquier destino | Cerrado — SEC-008 |
| El estado «enviado a todos» se guardaba después de enviar | Cerrado — se guarda antes y se revierte si falla |
| `eliminar` fallaba si el módulo ya no estaba en disco | Cerrado |
| Clave de Gemini en la URL | Cerrado — SEC-010 |

## 3 y 4 · Módulo Diccionario

| Hallazgo | Estado |
|---|---|
| Dos clics rápidos lanzaban dos procesos a la vez | Cerrado — comprobación y alta bajo un candado |
| El proceso heredaba todos los secretos de la API | Cerrado — SEC-009 |
| El módulo no figuraba en los documentos | Cerrado — ADR-0017, runbook y contrato de datos |
| Lectura del estado a medias mientras se reescribe; historial sin límite | Cerrado — lectura bajo candado; últimas 50 fichas |
| Hallazgos de un reporte por texto parcial (`SEL_EFEC_01` ≈ `SEL_EFEC_011`) | Cerrado — palabra completa |
| Los tres procesos fallaban en Windows (código 134) | Cerrado — ver [incidente](./incidents.md) |
| `npm run verificar` del repo `DICCIONARIO` termina con error (enlaces rotos de `modificaciones/nueva tarea`) | **Retirado** (2026-10-18): la app ya no usa el repo `DICCIONARIO` |
| `generar` no se probó de punta a punta desde la web | **Abierto** — correrlo una vez y revisar el `git diff` de ese repo |

## 5 · Resumen con gráficos

| Hallazgo | Estado |
|---|---|
| «Avance» usa números absolutos: `mod_rep` (259) tapa a las demás bases | **Abierto** — graficar el porcentaje de cada base |
| Las etiquetas de los trozos chicos se pisan | **Abierto** |
| Un nombre largo de regla se corta por la izquierda | **Abierto** |
| Código sin uso tras quitar las tarjetas (`Indicador`, `generado`/`carpeta` del resumen, `?nivel=`) | Cerrado — borrado, junto con los campos de `InfoServidor` que solo usaba la página «Bases de datos» |
| El tooltip es blanco en tema oscuro; la agrupación de los gráficos no tiene prueba | **Abierto** |

No se revisó: el SQL de los reportes de `catalogo/`, `cmg-mora`, el dibujo del Excel, la subida de adjuntos a Chat, el tema oscuro de los gráficos ni la web con sesión iniciada en un navegador.
