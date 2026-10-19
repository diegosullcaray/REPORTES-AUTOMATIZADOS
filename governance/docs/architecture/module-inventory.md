# Inventario de módulos

> **Generado** por `governance/scripts/generar_inventario.py`. No editar a mano: `python governance/scripts/generar_inventario.py`.

## Conexiones (3 servidores)

El `.env` define **servidores**; la **base de datos la elige cada reporte** (`base=` en su `ReporteLote`, o su propio `USE` / nombres de 3 partes).

| Conexión | Servidor (defecto) | Autenticación | Variables `.env` |
|---|---|---|---|
| `mish` | MISHWBDDES01 | Windows (o SQL si hay USER/PASSWORD) | `MISH_SERVER`, `MISH_USER`, `MISH_PASSWORD` |
| `slc` | 172.24.2.213 | Windows (o SQL si hay USER/PASSWORD) | `SLC_SERVER`, `SLC_USER`, `SLC_PASSWORD` |
| `rcc` | 172.20.0.70 | SQL (USER/PASSWORD) | `RCC_SERVER`, `RCC_USER`, `RCC_PASSWORD` |

## Reportes ejecutables (21)

| Responsable / Nº | Comando | Frecuencia | Servidor | Base de datos | Módulo | Qué hace |
|---|---|---|---|---|---|---|
| Diarias 02 | `cartera-sin-asignar` | diaria | mish | storage | `modulos.reportes.catalogo.diarios.r02_cartera_sin_asignar` | Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación |
| Diarias 04.1 | `cmg-mora` | diaria | rcc | propia (ver módulo) | `modulos.reportes.catalogo.diarios.r04_1_cmg_mora` | Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0) |
| Piero 01 | `desembolsos-por-canal` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r01_desembolsos_por_canal` | Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT) |
| Piero 02 | `fondeo-estable` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r02_fondeo_estable` | Estadística de tramo / Fondeo estable (Eddy Martínez) |
| Piero 03 | `heredados-pdm` | mensual | slc | slc | `modulos.reportes.catalogo.mensuales.piero.r03_heredados_pdm` | Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar |
| Piero 04.1 | `contratacion-electronica` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r04_1_contratacion_electronica` | Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto) |
| Piero 04.2 | `clientes-rurales-migrantes` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r04_2_clientes_rurales_migrantes` | Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres |
| Piero 05.1 | `giovanni-captaciones` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r05_1_giovanni_captaciones` | Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones |
| Piero 05.2 | `giovanni-seguros` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r05_2_giovanni_seguros` | Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar» |
| Piero 05.3 | `giovanni-cartera-agro` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r05_3_giovanni_cartera_agro` | Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior) |
| Piero 06 | `saca-tu-garra` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r06_saca_tu_garra` | Saca tu garra (Giancarlos): entregar 8:00–8:30 AM |
| Piero 07 | `saldo-medio-vigente` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r07_saldo_medio_vigente` | Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios |
| Piero 08 | `tapp-saldo-medio-territorio` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r08_tapp_saldo_medio_territorio` | TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy) |
| Piero 09.1 | `michael-captaciones` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r09_1_michael_captaciones` | Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos) |
| Piero 09.2 | `michael-castigos` | mensual | mish | storage | `modulos.reportes.catalogo.mensuales.piero.r09_2_michael_castigos` | Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos) |
| Erick 01 | `productos-verdes` | mensual | slc | slc | `modulos.reportes.catalogo.mensuales.erick.r01_productos_verdes` | Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas |
| Erick 02 | `clientes-jovenes` | mensual | slc | slc | `modulos.reportes.catalogo.mensuales.erick.r02_clientes_jovenes` | Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años |
| Erick 03.1 | `bancarizados` | mensual | rcc, slc | propia (ver módulo) | `modulos.reportes.catalogo.mensuales.erick.r03_1_bancarizados` | Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio |
| Erick 03.2 | `bancarizados-producto` | mensual | slc | propia (ver módulo) | `modulos.reportes.catalogo.mensuales.erick.r03_2_bancarizados_producto` | Bancarizados por producto (clientes nuevos con desembolso) |
| Erick 03.3 | `clientes-extranjeros` | mensual | slc, rcc | propia (ver módulo) | `modulos.reportes.catalogo.mensuales.erick.r03_3_clientes_extranjeros` | Clientes por nacionalidad: créditos, pasivos y seguros |
| Erick 03.4 | `indicadores-clientes` | mensual | slc | propia (ver módulo) | `modulos.reportes.catalogo.mensuales.erick.r03_4_indicadores_clientes` | Indicadores de clientes para el Directorio |

## Módulos y capas

Monolito modular: cada módulo de negocio tiene sus capas (`dominio` ← `aplicacion` ← `infraestructura` / `interfaces`) y solo usa el dominio y la aplicación de los módulos de los que depende; la regla `arquitectura-capas` lo exige. `config/` es la raíz de composición y el proyecto Django.

### `core/` — Núcleo compartido (bd, entorno, configuración, puertos, errores, HTTP)

| Módulo | Qué hace |
|---|---|
| `core/bd.py` | Acceso único a los 3 servidores (mish, slc, rcc). Cada llamada puede pedir su base de datos con `base=` |
| `core/configuracion.py` | Configuración (infraestructura): rutas del proyecto, `.env` y conexión a los 3 servidores SQL Server |
| `core/dto.py` | Contratos compartidos por todos los módulos. Solo forma de los datos: sin lógica |
| `core/entorno.py` | Adaptador del puerto de entorno: variables del `.env` y del proceso, carpetas de datos y corte configurado |
| `core/excepciones.py` | Errores de negocio compartidos por todas las capas (el dominio no depende de ninguna librería ni de la infraestructura) |
| `core/fechas.py` | Lo mínimo de fechas que comparten el núcleo (variables del .env) y el módulo de reportes: AAAA-MM-DD y la fecha de corte escrita en el .env |
| `core/http.py` | Utilidades HTTP de la interfaz web: respuestas JSON, lectura validada del cuerpo y de la consulta, y errores con su código |
| `core/puertos.py` | Puertos del núcleo (base de datos y entorno) y el registro de adaptadores que usa cada módulo |
| `core/servidores.py` | Dónde vive cada base de datos: conocimiento del negocio (qué servidor de los 3 aloja cada base), sin credenciales ni conexiones |

### `config/` — Proyecto Django y raíz de composición

| Módulo | Qué hace |
|---|---|
| `config/composicion.py` | Raíz de composición: crea los adaptadores reales de cada módulo y los conecta a sus puertos |
| `config/middleware.py` | Middleware de la API: sesión obligatoria y traducción de errores de los casos de uso a códigos HTTP |
| `config/settings.py` | Ajustes de Django para la API de la web: sin base de datos, sin sesiones de Django (la sesión es nuestra cookie firmada) y sin plantillas |
| `config/urls.py` | Rutas de la API: cada módulo aporta las suyas (`modulos/<módulo>/interfaces/web/urls.py`) bajo /api |
| `config/wsgi.py` | Punto de entrada WSGI de la API: conecta los adaptadores, crea la aplicación de Django y arranca la cola de ejecuciones |

### `modulos/reportes/` — Catálogo, ejecución, verificación de tablas, archivos, validación masiva y ejecuciones; incluye los reportes del legado (`catalogo/`).

**`dominio/`**

| Módulo | Qué hace |
|---|---|
| `modulos/reportes/dominio/archivos.py` | Qué archivos de la carpeta de un reporte son entregables y de qué tipo son (para la vista previa y las descargas) |
| `modulos/reportes/dominio/fechas.py` | Fechas de corte y tokens que se sustituyen en el T-SQL de cada reporte (reglas puras: no leen el .env) |
| `modulos/reportes/dominio/formato_excel.py` | Cómo sale un resultado en el Excel del legado: descripción de columnas y de hojas de resumen (sin escribir ningún archivo) |
| `modulos/reportes/dominio/reglas_fecha.py` | Cómo usa cada reporte la fecha de corte en cada tabla: qué columna se compara y con qué condición |
| `modulos/reportes/dominio/reportes.py` | Catálogo de reportes ejecutables: comando -> módulo, responsable, número del legado, servidor(es) y carpeta de salida |
| `modulos/reportes/dominio/tablas.py` | Registro de TABLAS: qué tabla usa cada reporte, en qué base vive y cómo saber si está al día |
| `modulos/reportes/dominio/verificacion.py` | ¿Están las tablas de un reporte al día para el corte? Estados, causas legibles y mensaje para pedir la actualización a Producción |

**`aplicacion/`**

| Módulo | Qué hace |
|---|---|
| `modulos/reportes/aplicacion/casos_uso/archivos.py` | Archivos generados por cada reporte: listado, descarga segura y vista previa (Excel y texto) |
| `modulos/reportes/aplicacion/casos_uso/catalogo.py` | Catálogo de reportes: qué hay, cómo se describe cada uno, su fecha de corte y a quién se le entrega su archivo |
| `modulos/reportes/aplicacion/casos_uso/correo_reporte.py` | Correo de los archivos generados de un reporte, con la cuenta de Google autorizada (API de Gmail) y su firma |
| `modulos/reportes/aplicacion/casos_uso/crear_reporte.py` | Alta de un reporte desde la web: escribe su módulo, su test y su registro, y lo deja disponible sin reiniciar |
| `modulos/reportes/aplicacion/casos_uso/ejecuciones.py` | Ejecuciones: valida el pedido con las reglas del reporte, arma los argumentos de `main.py` y consulta/gestiona el historial |
| `modulos/reportes/aplicacion/casos_uso/etiquetas.py` | Etiquetas (como los «tags» de Dokploy): un nombre y un color (#rrggbb) que se pegan a los grupos de reportes para organizarlos |
| `modulos/reportes/aplicacion/casos_uso/validacion.py` | Historial de la validación masiva de tablas (una ficha por verificación) y envío por Google Chat del mensaje para actualizarlas |
| `modulos/reportes/aplicacion/casos_uso/verificacion.py` | Verificación de tablas al corte y solicitud a Producción (por reporte y masiva por responsable) |
| `modulos/reportes/aplicacion/columnas.py` | Aplica el formato de columnas de un reporte (orden, encabezados y reemplazo de 0/nulos) a un resultado |
| `modulos/reportes/aplicacion/cortes.py` | Fecha de corte de un reporte: argumento > .env > día anterior (la regla es del dominio; el .env se lee por el puerto) |
| `modulos/reportes/aplicacion/dto.py` | Contratos del módulo de reportes (entrada y salida). Solo forma de los datos: sin lógica |
| `modulos/reportes/aplicacion/ejecucion.py` | Ejecutor común de reportes (caso de uso): conexión -> validación de tablas y fechas -> consulta -> validación de datos -> Excel |
| `modulos/reportes/aplicacion/exclusivo.py` | Candado del registro editable (reportes, grupos y etiquetas): cada operación lee y reescribe archivos, así que van de a una |
| `modulos/reportes/aplicacion/nuevo_reporte.py` | Alta de un reporte desde la web: validación y texto de lo que se escribe (módulo, test y líneas de registro). Sin disco ni estado |
| `modulos/reportes/aplicacion/puertos.py` | Puertos del módulo de reportes: lo que necesita del mundo exterior (Excel, cola de ejecuciones, historial de validación, lectura de archivos) |
| `modulos/reportes/aplicacion/rutas.py` | Dónde deja cada reporte sus archivos |
| `modulos/reportes/aplicacion/verificacion.py` | ¿Están las tablas de un reporte al día para el corte? Solo hace SELECT MAX(<col_fecha>) / comprueba existencia; no modifica nada |

**`infraestructura/`**

| Módulo | Qué hace |
|---|---|
| `modulos/reportes/infraestructura/cola_ejecuciones.py` | Cola de ejecuciones: un reporte a la vez, como subproceso de `main.py` (mismos códigos de salida y mensajes que la consola) |
| `modulos/reportes/infraestructura/entregas/chat.py` | Entrega de archivos generados por Google Chat (mensaje directo con adjunto), con la cuenta de Google autorizada en la web |
| `modulos/reportes/infraestructura/entregas/correo_resumen.py` | Entrega por correo del resumen diario (legado: macro `ActualizarSQL_AmbasHojas` de «Cartera-Sin asignar-base.xlsm») |
| `modulos/reportes/infraestructura/etiquetas.py` | Etiquetas de los grupos de /reportes en disco: data/outputs/etiquetas.json (no versionado) |
| `modulos/reportes/infraestructura/excel.py` | Formato Excel de las salidas, copiado del legado (Cartera-Sin asignar-base.xlsm) |
| `modulos/reportes/infraestructura/historial_validacion.py` | Fichas del historial de validación en disco: data/outputs/validaciones/<grupo>/<id>.json (no versionadas) |
| `modulos/reportes/infraestructura/imagen.py` | Imagen JPG del resumen jerárquico (el `Reporte_Temporal.jpg` que el legado pegaba en el cuerpo del correo) |
| `modulos/reportes/infraestructura/lector_archivos.py` | Lectura de archivos generados para la vista previa (Excel con openpyxl) |

**`interfaces/`**

| Módulo | Qué hace |
|---|---|
| `modulos/reportes/interfaces/cli/principal.py` | Consola: `python main.py <comando>`. Traduce la línea de comandos a casos de uso y reportes |
| `modulos/reportes/interfaces/cli/tablas.py` | Subcomandos de `main.py`: tablas, solicitud-actualizacion |
| `modulos/reportes/interfaces/web/apps.py` | — |
| `modulos/reportes/interfaces/web/urls.py` | Rutas del módulo de reportes (catálogo, validación de tablas y ejecuciones) |
| `modulos/reportes/interfaces/web/vistas/ejecuciones.py` | Ejecuciones: encolar un reporte, ver el historial y eliminar ejecuciones |
| `modulos/reportes/interfaces/web/vistas/firma.py` | Firma de Gmail para el correo de los archivos de un reporte |
| `modulos/reportes/interfaces/web/vistas/reportes.py` | Catálogo de reportes, su detalle, verificación de tablas, archivos generados y envío por correo o Chat |
| `modulos/reportes/interfaces/web/vistas/validacion.py` | Validación masiva de las tablas de los reportes mensuales de un responsable (Piero / Erick): verificar, historial y mensaje por Chat |

**`catalogo/`**: 21 módulos (ver «Reportes ejecutables»).

### `modulos/notificaciones/` — Correo corporativo (SMTP) y aviso al webhook de Google Chat.

**`dominio/`**

| Módulo | Qué hace |
|---|---|
| `modulos/notificaciones/dominio/entregas.py` | A quién se entregan los archivos de un reporte: nombres de las variables del .env y validación de correos |

**`aplicacion/`**

| Módulo | Qué hace |
|---|---|
| `modulos/notificaciones/aplicacion/casos_uso/notificaciones.py` | Notificaciones de la web: cuenta SMTP para los correos y webhook de Google Chat. Se guardan en el .env |
| `modulos/notificaciones/aplicacion/correo.py` | API pública del módulo de notificaciones para los demás módulos: correo corporativo (cuenta MIS) y aviso al webhook de Google Chat |
| `modulos/notificaciones/aplicacion/destinatarios.py` | Listas de correos de entrega (Chat, correo, validación): viven en el .env; el valor lo da el puerto de entorno |
| `modulos/notificaciones/aplicacion/dto.py` | Contratos del módulo de notificaciones (correo SMTP y webhook de Google Chat). Solo forma de los datos: sin lógica |
| `modulos/notificaciones/aplicacion/puertos.py` | Puertos del módulo de notificaciones: correo corporativo (cuenta MIS) y aviso al webhook de Google Chat |

**`infraestructura/`**

| Módulo | Qué hace |
|---|---|
| `modulos/notificaciones/infraestructura/correo_smtp.py` | Envío de correos con la cuenta MIS (SMTP de Gmail) y aviso al webhook de Google Chat |

**`interfaces/`**

| Módulo | Qué hace |
|---|---|
| `modulos/notificaciones/interfaces/web/apps.py` | — |
| `modulos/notificaciones/interfaces/web/urls.py` | Rutas del módulo de notificaciones |
| `modulos/notificaciones/interfaces/web/vistas/notificaciones.py` | Notificaciones: cuenta SMTP del correo y webhook de Google Chat, con su prueba de envío |

### `modulos/integraciones/` — Google Workspace: autorización OAuth, Gmail, Chat y servidor MCP.

**`aplicacion/`**

| Módulo | Qué hace |
|---|---|
| `modulos/integraciones/aplicacion/casos_uso/google.py` | MCP de Google Workspace desde la web: cliente OAuth, autorización con código, servidores MCP oficiales y pruebas |
| `modulos/integraciones/aplicacion/casos_uso/herramientas_envio.py` | Herramientas MCP propias para ENVIAR: correo por Gmail y mensajes de Google Chat a contactos o espacios |
| `modulos/integraciones/aplicacion/casos_uso/ia.py` | Conexiones con proveedores de IA por API key (como «AI» en Settings de Dokploy), guardadas en el .env |
| `modulos/integraciones/aplicacion/dto.py` | Contratos del módulo de integraciones (Google Workspace y MCP). Solo forma de los datos: sin lógica |
| `modulos/integraciones/aplicacion/mensajeria.py` | API pública del módulo de integraciones para los demás módulos: enviar por Gmail y Google Chat con la cuenta autorizada |
| `modulos/integraciones/aplicacion/puertos.py` | Puertos del módulo de integraciones: Google con OAuth de usuario (Gmail, Chat y servidores MCP oficiales). Los fallos son `ErrorIntegracion` |

**`infraestructura/`**

| Módulo | Qué hace |
|---|---|
| `modulos/integraciones/infraestructura/google/cliente.py` | Google Workspace con OAuth de usuario: servidores MCP oficiales de Google (Drive, Gmail, Docs, Sheets, Slides, Chat) |
| `modulos/integraciones/infraestructura/ia/cliente.py` | Proveedores de IA con API key (OpenAI, Anthropic, Gemini, Mistral, OpenRouter, Ollama o cualquier endpoint compatible con OpenAI) |

**`interfaces/`**

| Módulo | Qué hace |
|---|---|
| `modulos/integraciones/interfaces/mcp/servidor.py` | Servidor MCP propio (stdio) para ENVIAR: correo por Gmail y mensajes de Google Chat a contactos o espacios |
| `modulos/integraciones/interfaces/web/apps.py` | — |
| `modulos/integraciones/interfaces/web/urls.py` | Rutas del módulo de integraciones (Google Workspace y MCP) |
| `modulos/integraciones/interfaces/web/vistas/google.py` | MCP de Google Workspace: cliente OAuth, autorización, servidores MCP oficiales y envío directo |
| `modulos/integraciones/interfaces/web/vistas/ia.py` | Conexiones con proveedores de IA por API key |

### `modulos/diccionario/` — Diccionario de datos de los reportes MIS (repo DICCIONARIO): reportes, tablas, columnas, calidad y procesos.

**`dominio/`**

| Módulo | Qué hace |
|---|---|
| `modulos/diccionario/dominio/columnas.py` | Reglas puras del diccionario: qué columnas parecen de fecha y qué procesos del repo DICCIONARIO se pueden lanzar desde la web |

**`aplicacion/`**

| Módulo | Qué hace |
|---|---|
| `modulos/diccionario/aplicacion/casos_uso/diccionario.py` | Consultas al diccionario de datos de los reportes MIS: resumen, reportes, tablas, calidad y lo que aporta a los reportes propios |
| `modulos/diccionario/aplicacion/casos_uso/procesos.py` | Procesos del repo DICCIONARIO que se lanzan desde la web (regenerar, verificar, probar): lista cerrada, uno a la vez, con su historial y log |
| `modulos/diccionario/aplicacion/dto.py` | Contratos del módulo diccionario: lo que la web ve del diccionario de datos de los reportes MIS. Solo forma de los datos |
| `modulos/diccionario/aplicacion/puertos.py` | Puertos del módulo diccionario: la lectura del diccionario.json y el lanzador de procesos del repo DICCIONARIO |

**`infraestructura/`**

| Módulo | Qué hace |
|---|---|
| `modulos/diccionario/infraestructura/lanzador.py` | Lanza los procesos del repo DICCIONARIO como subproceso (sin shell), uno a la vez, y deja su estado y log en data/outputs/diccionario/ |
| `modulos/diccionario/infraestructura/lector.py` | Lee el diccionario.json del repo DICCIONARIO (carpeta hermana de REPORTES-AUTOMATIZADOS, o `DICCIONARIO_DIR` del .env) |

**`interfaces/`**

| Módulo | Qué hace |
|---|---|
| `modulos/diccionario/interfaces/web/apps.py` | — |
| `modulos/diccionario/interfaces/web/urls.py` | Rutas del módulo diccionario |
| `modulos/diccionario/interfaces/web/vistas/diccionario.py` | Diccionario de datos de los reportes MIS: resumen, reportes, tablas, calidad, lo que aporta a los reportes propios y sus procesos |

### `modulos/sistema/` — Sesión, cuenta, perfil, ajustes y servidores SQL editables desde la web.

**`aplicacion/`**

| Módulo | Qué hace |
|---|---|
| `modulos/sistema/aplicacion/casos_uso/configuracion.py` | Configuración editable desde la web (cortes, carpetas, driver), cuenta de acceso, servidores de bases de datos y perfil |
| `modulos/sistema/aplicacion/casos_uso/sesion.py` | Inicio de sesión con usuario y clave del .env, y cookie firmada |
| `modulos/sistema/aplicacion/dto.py` | Contratos del módulo de sistema (sesión, cuenta, ajustes y servidores). Solo forma de los datos: sin lógica |

**`interfaces/`**

| Módulo | Qué hace |
|---|---|
| `modulos/sistema/interfaces/web/apps.py` | — |
| `modulos/sistema/interfaces/web/urls.py` | Rutas del módulo de sistema (sesión, cuenta, perfil, ajustes y servidores) |
| `modulos/sistema/interfaces/web/vistas/configuracion.py` | Ajustes generales, perfil y bases de datos (servidores SQL Server) editables desde la web |
| `modulos/sistema/interfaces/web/vistas/sesion.py` | Inicio y cierre de sesión, y cambio de usuario o contraseña (credenciales en el .env) |


## Pruebas (63 archivos)

Reflejan los módulos: `tests/core`, `tests/config` y `tests/modulos/<módulo>/<capa>`.

- `tests/config/test_api.py`
- `tests/config/test_composicion.py`
- `tests/config/test_middleware.py`
- `tests/core/test_bd.py`
- `tests/core/test_configuracion.py`
- `tests/core/test_entorno.py`
- `tests/core/test_excepciones.py`
- `tests/core/test_http.py`
- `tests/core/test_puertos.py`
- `tests/core/test_servidores.py`
- `tests/modulos/diccionario/aplicacion/casos_uso/test_diccionario.py`
- `tests/modulos/diccionario/aplicacion/casos_uso/test_procesos.py`
- `tests/modulos/diccionario/dominio/test_columnas.py`
- `tests/modulos/diccionario/infraestructura/test_lanzador.py`
- `tests/modulos/diccionario/infraestructura/test_lector.py`
- `tests/modulos/integraciones/aplicacion/casos_uso/test_google.py`
- `tests/modulos/integraciones/aplicacion/casos_uso/test_herramientas_envio.py`
- `tests/modulos/integraciones/aplicacion/casos_uso/test_ia.py`
- `tests/modulos/integraciones/aplicacion/test_mensajeria.py`
- `tests/modulos/integraciones/infraestructura/google/test_cliente.py`
- `tests/modulos/integraciones/infraestructura/ia/test_cliente.py`
- `tests/modulos/integraciones/interfaces/mcp/test_servidor.py`
- `tests/modulos/notificaciones/aplicacion/casos_uso/test_notificaciones.py`
- `tests/modulos/notificaciones/aplicacion/test_correo.py`
- `tests/modulos/notificaciones/aplicacion/test_destinatarios.py`
- `tests/modulos/notificaciones/dominio/test_entregas.py`
- `tests/modulos/notificaciones/infraestructura/test_correo_smtp.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_archivos.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_catalogo.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_correo_reporte.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_crear_reporte.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_ejecuciones.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_etiquetas.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_validacion.py`
- `tests/modulos/reportes/aplicacion/casos_uso/test_verificacion.py`
- `tests/modulos/reportes/aplicacion/test_columnas.py`
- `tests/modulos/reportes/aplicacion/test_cortes.py`
- `tests/modulos/reportes/aplicacion/test_dto.py`
- `tests/modulos/reportes/aplicacion/test_ejecucion.py`
- `tests/modulos/reportes/aplicacion/test_exclusivo.py`
- `tests/modulos/reportes/aplicacion/test_nuevo_reporte.py`
- `tests/modulos/reportes/aplicacion/test_rutas.py`
- `tests/modulos/reportes/aplicacion/test_verificacion.py`
- `tests/modulos/reportes/catalogo/test_formatos_reportes.py`
- `tests/modulos/reportes/catalogo/test_r04_1_cmg_mora.py`
- `tests/modulos/reportes/catalogo/test_reportes_lote.py`
- `tests/modulos/reportes/dominio/test_fechas.py`
- `tests/modulos/reportes/dominio/test_formato_excel.py`
- `tests/modulos/reportes/dominio/test_reglas_fecha.py`
- `tests/modulos/reportes/dominio/test_reportes.py`
- `tests/modulos/reportes/dominio/test_tablas.py`
- `tests/modulos/reportes/infraestructura/entregas/test_chat.py`
- `tests/modulos/reportes/infraestructura/entregas/test_correo_resumen.py`
- `tests/modulos/reportes/infraestructura/test_cola_ejecuciones.py`
- `tests/modulos/reportes/infraestructura/test_excel.py`
- `tests/modulos/reportes/infraestructura/test_historial_validacion.py`
- `tests/modulos/reportes/infraestructura/test_imagen.py`
- `tests/modulos/reportes/infraestructura/test_lector_archivos.py`
- `tests/modulos/reportes/interfaces/cli/test_principal.py`
- `tests/modulos/reportes/interfaces/cli/test_tablas.py`
- `tests/modulos/sistema/aplicacion/casos_uso/test_configuracion.py`
- `tests/modulos/sistema/aplicacion/casos_uso/test_sesion.py`
- `tests/test_validar_gobernanza.py`
