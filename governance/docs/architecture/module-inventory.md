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
| Diarias 02 | `cartera-sin-asignar` | diaria | mish | storage | `reportes.diarios.r02_cartera_sin_asignar` | Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación |
| Diarias 04.1 | `cmg-mora` | diaria | rcc | propia (ver módulo) | `reportes.diarios.r04_1_cmg_mora` | Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0) |
| Piero 01 | `desembolsos-por-canal` | mensual | mish | storage | `reportes.mensuales.piero.r01_desembolsos_por_canal` | Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT) |
| Piero 02 | `fondeo-estable` | mensual | mish | storage | `reportes.mensuales.piero.r02_fondeo_estable` | Estadística de tramo / Fondeo estable (Eddy Martínez) |
| Piero 03 | `heredados-pdm` | mensual | slc | slc | `reportes.mensuales.piero.r03_heredados_pdm` | Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar |
| Piero 04.1 | `contratacion-electronica` | mensual | mish | storage | `reportes.mensuales.piero.r04_1_contratacion_electronica` | Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto) |
| Piero 04.2 | `clientes-rurales-migrantes` | mensual | mish | storage | `reportes.mensuales.piero.r04_2_clientes_rurales_migrantes` | Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres |
| Piero 05.1 | `giovanni-captaciones` | mensual | mish | storage | `reportes.mensuales.piero.r05_1_giovanni_captaciones` | Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones |
| Piero 05.2 | `giovanni-seguros` | mensual | mish | storage | `reportes.mensuales.piero.r05_2_giovanni_seguros` | Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar» |
| Piero 05.3 | `giovanni-cartera-agro` | mensual | mish | storage | `reportes.mensuales.piero.r05_3_giovanni_cartera_agro` | Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior) |
| Piero 06 | `saca-tu-garra` | mensual | mish | storage | `reportes.mensuales.piero.r06_saca_tu_garra` | Saca tu garra (Giancarlos): entregar 8:00–8:30 AM |
| Piero 07 | `saldo-medio-vigente` | mensual | mish | storage | `reportes.mensuales.piero.r07_saldo_medio_vigente` | Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios |
| Piero 08 | `tapp-saldo-medio-territorio` | mensual | mish | storage | `reportes.mensuales.piero.r08_tapp_saldo_medio_territorio` | TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy) |
| Piero 09.1 | `michael-captaciones` | mensual | mish | storage | `reportes.mensuales.piero.r09_1_michael_captaciones` | Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos) |
| Piero 09.2 | `michael-castigos` | mensual | mish | storage | `reportes.mensuales.piero.r09_2_michael_castigos` | Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos) |
| Erick 01 | `productos-verdes` | mensual | slc | slc | `reportes.mensuales.erick.r01_productos_verdes` | Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas |
| Erick 02 | `clientes-jovenes` | mensual | slc | slc | `reportes.mensuales.erick.r02_clientes_jovenes` | Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años |
| Erick 03.1 | `bancarizados` | mensual | rcc, slc | propia (ver módulo) | `reportes.mensuales.erick.r03_1_bancarizados` | Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio |
| Erick 03.2 | `bancarizados-producto` | mensual | slc | propia (ver módulo) | `reportes.mensuales.erick.r03_2_bancarizados_producto` | Bancarizados por producto (clientes nuevos con desembolso) |
| Erick 03.3 | `clientes-extranjeros` | mensual | slc, rcc | propia (ver módulo) | `reportes.mensuales.erick.r03_3_clientes_extranjeros` | Clientes por nacionalidad: créditos, pasivos y seguros |
| Erick 03.4 | `indicadores-clientes` | mensual | slc | propia (ver módulo) | `reportes.mensuales.erick.r03_4_indicadores_clientes` | Indicadores de clientes para el Directorio |

## Capas y módulos

La dependencia apunta solo hacia adentro (`dominio` ← `aplicacion` ← `infraestructura` / `interfaces`); la regla `arquitectura-capas` lo exige. `composicion.py` es la raíz de composición: conecta los adaptadores a los puertos al arrancar.

### `dominio/` — Reglas puras del negocio: reportes, tablas, fechas de corte, verificación. Sin I/O ni frameworks.

| Módulo | Qué hace |
|---|---|
| `dominio/archivos.py` | Qué archivos de la carpeta de un reporte son entregables y de qué tipo son (para la vista previa y las descargas) |
| `dominio/entregas.py` | A quién se entregan los archivos de un reporte: nombres de las variables del .env y validación de correos |
| `dominio/errores.py` | Errores de negocio compartidos por todas las capas (el dominio no depende de ninguna librería ni de la infraestructura) |
| `dominio/fechas.py` | Fechas de corte y tokens que se sustituyen en el T-SQL de cada reporte (reglas puras: no leen el .env) |
| `dominio/formato_excel.py` | Cómo sale un resultado en el Excel del legado: descripción de columnas y de hojas de resumen (sin escribir ningún archivo) |
| `dominio/reglas_fecha.py` | Cómo usa cada reporte la fecha de corte en cada tabla: qué columna se compara y con qué condición |
| `dominio/reportes.py` | Catálogo de reportes ejecutables: comando -> módulo, responsable, número del legado, servidor(es) y carpeta de salida |
| `dominio/servidores.py` | Dónde vive cada base de datos: conocimiento del negocio (qué servidor de los 3 aloja cada base), sin credenciales ni conexiones |
| `dominio/tablas.py` | Registro de TABLAS: qué tabla usa cada reporte, en qué base vive y cómo saber si está al día |
| `dominio/verificacion.py` | ¿Están las tablas de un reporte al día para el corte? Estados, causas legibles y mensaje para pedir la actualización a Producción |

### `aplicacion/` — Casos de uso, puertos (interfaces hacia afuera) y contratos (`dto.py`). Depende solo del dominio.

| Módulo | Qué hace |
|---|---|
| `aplicacion/casos_uso/archivos.py` | Archivos generados por cada reporte: listado, descarga segura y vista previa (Excel y texto) |
| `aplicacion/casos_uso/catalogo.py` | Catálogo de reportes: qué hay, cómo se describe cada uno, su fecha de corte y a quién se le entrega su archivo |
| `aplicacion/casos_uso/configuracion.py` | Configuración editable desde la web (cortes, carpetas, driver), cuenta de acceso, servidores de bases de datos y perfil |
| `aplicacion/casos_uso/correo_reporte.py` | Correo de los archivos generados de un reporte, con la cuenta de Google autorizada (API de Gmail) y su firma |
| `aplicacion/casos_uso/ejecuciones.py` | Ejecuciones: valida el pedido con las reglas del reporte, arma los argumentos de `main.py` y consulta/gestiona el historial |
| `aplicacion/casos_uso/google.py` | MCP de Google Workspace desde la web: cliente OAuth, autorización con código, servidores MCP oficiales y pruebas |
| `aplicacion/casos_uso/herramientas_envio.py` | Herramientas MCP propias para ENVIAR: correo por Gmail y mensajes de Google Chat a contactos o espacios |
| `aplicacion/casos_uso/notificaciones.py` | Notificaciones de la web: cuenta SMTP para los correos y webhook de Google Chat. Se guardan en el .env |
| `aplicacion/casos_uso/sesion.py` | Inicio de sesión con usuario y clave del .env, y cookie firmada |
| `aplicacion/casos_uso/validacion.py` | Historial de la validación masiva de tablas (una ficha por verificación) y envío por Google Chat del mensaje para actualizarlas |
| `aplicacion/casos_uso/verificacion.py` | Verificación de tablas al corte y solicitud a Producción (por reporte y masiva por responsable) |
| `aplicacion/columnas.py` | Aplica el formato de columnas de un reporte (orden, encabezados y reemplazo de 0/nulos) a un resultado |
| `aplicacion/cortes.py` | Fecha de corte de un reporte: argumento > .env > día anterior (la regla es del dominio; el .env se lee por el puerto) |
| `aplicacion/destinatarios.py` | Listas de correos de entrega (Chat, correo, validación): viven en el .env; el valor lo da el puerto de entorno |
| `aplicacion/dto.py` | Contratos HTTP (entrada y salida) de la API. Solo forma de los datos: sin lógica |
| `aplicacion/ejecucion.py` | Ejecutor común de reportes (caso de uso): conexión -> validación de tablas y fechas -> consulta -> validación de datos -> Excel |
| `aplicacion/errores.py` | Errores de los casos de uso: la capa HTTP los traduce a 422 y 404, la consola a un mensaje |
| `aplicacion/puertos.py` | Puertos: lo que la aplicación necesita del mundo exterior, como interfaces (Protocol) sin nombrar ninguna librería de I/O |
| `aplicacion/rutas.py` | Dónde deja cada reporte sus archivos |
| `aplicacion/verificacion.py` | ¿Están las tablas de un reporte al día para el corte? Solo hace SELECT MAX(<col_fecha>) / comprueba existencia; no modifica nada |

### `infraestructura/` — Adaptadores de los puertos: bases de datos, Excel, correo, Google, `.env`, cola de ejecuciones.

| Módulo | Qué hace |
|---|---|
| `infraestructura/bd.py` | Acceso único a los 3 servidores (mish, slc, rcc). Cada llamada puede pedir su base de datos con `base=` |
| `infraestructura/cola_ejecuciones.py` | Cola de ejecuciones: un reporte a la vez, como subproceso de `main.py` (mismos códigos de salida y mensajes que la consola) |
| `infraestructura/configuracion.py` | Configuración (infraestructura): rutas del proyecto, `.env` y conexión a los 3 servidores SQL Server |
| `infraestructura/correo_smtp.py` | Envío de correos con la cuenta MIS (SMTP de Gmail) y aviso al webhook de Google Chat |
| `infraestructura/entorno.py` | Adaptador del puerto de entorno: variables del `.env` y del proceso, carpetas de datos y corte configurado |
| `infraestructura/entregas/chat.py` | Entrega de archivos generados por Google Chat (mensaje directo con adjunto), con la cuenta de Google autorizada en la web |
| `infraestructura/entregas/correo_resumen.py` | Entrega por correo del resumen diario (legado: macro `ActualizarSQL_AmbasHojas` de «Cartera-Sin asignar-base.xlsm») |
| `infraestructura/excel.py` | Formato Excel de las salidas, copiado del legado (Cartera-Sin asignar-base.xlsm) |
| `infraestructura/google/cliente.py` | Google Workspace con OAuth de usuario: servidores MCP oficiales de Google (Drive, Gmail, Docs, Sheets, Slides, Chat) |
| `infraestructura/historial_validacion.py` | Fichas del historial de validación en disco: data/outputs/validaciones/<grupo>/<id>.json (no versionadas) |
| `infraestructura/imagen.py` | Imagen JPG del resumen jerárquico (el `Reporte_Temporal.jpg` que el legado pegaba en el cuerpo del correo) |
| `infraestructura/lector_archivos.py` | Lectura de archivos generados para la vista previa (Excel con openpyxl) |

### `interfaces/` — Entradas: API HTTP (Django, una app por tema), consola (`main.py`) y servidor MCP. Solo traducen al caso de uso.

| Módulo | Qué hace |
|---|---|
| `interfaces/cli/principal.py` | Consola: `python main.py <comando>`. Traduce la línea de comandos a casos de uso y reportes |
| `interfaces/cli/tablas.py` | Subcomandos de `main.py`: tablas, solicitud-actualizacion |
| `interfaces/mcp/servidor.py` | Servidor MCP propio (stdio) para ENVIAR: correo por Gmail y mensajes de Google Chat a contactos o espacios |
| `interfaces/web/apps/configuracion/apps.py` | — |
| `interfaces/web/apps/configuracion/urls.py` | — |
| `interfaces/web/apps/configuracion/views.py` | Configuración editable desde la web: perfil, ajustes generales, bases de datos y notificaciones (correo y Google Chat) |
| `interfaces/web/apps/ejecuciones/apps.py` | — |
| `interfaces/web/apps/ejecuciones/urls.py` | — |
| `interfaces/web/apps/ejecuciones/views.py` | Ejecuciones: encolar un reporte, ver el historial y eliminar ejecuciones |
| `interfaces/web/apps/google/apps.py` | — |
| `interfaces/web/apps/google/urls.py` | — |
| `interfaces/web/apps/google/views.py` | MCP de Google Workspace: cliente OAuth, autorización, servidores MCP oficiales, envío directo y firma de Gmail |
| `interfaces/web/apps/reportes/apps.py` | — |
| `interfaces/web/apps/reportes/urls.py` | — |
| `interfaces/web/apps/reportes/views.py` | Catálogo de reportes, su detalle, verificación de tablas, archivos generados y envío por correo o Chat |
| `interfaces/web/apps/sesion/apps.py` | — |
| `interfaces/web/apps/sesion/urls.py` | — |
| `interfaces/web/apps/sesion/views.py` | Inicio y cierre de sesión, y cambio de usuario o contraseña (credenciales en el .env) |
| `interfaces/web/apps/validacion/apps.py` | — |
| `interfaces/web/apps/validacion/urls.py` | — |
| `interfaces/web/apps/validacion/views.py` | Validación masiva de las tablas de los reportes mensuales de un responsable (Piero / Erick): verificar, historial y mensaje por Chat |
| `interfaces/web/http.py` | Utilidades HTTP de la interfaz web: respuestas JSON, lectura validada del cuerpo y de la consulta, y errores con su código |
| `interfaces/web/middleware.py` | Middleware de la API: sesión obligatoria y traducción de errores de los casos de uso a códigos HTTP |
| `interfaces/web/settings.py` | Ajustes de Django para la API de la web: sin base de datos, sin sesiones de Django (la sesión es nuestra cookie firmada) y sin plantillas |
| `interfaces/web/urls.py` | Rutas de la API: cada app de `apps/` aporta las suyas bajo /api |
| `interfaces/web/wsgi.py` | Punto de entrada WSGI de la API: conecta los adaptadores, crea la aplicación de Django y arranca la cola de ejecuciones |

### `reportes/` — Un módulo por reporte del legado (T-SQL y formato de salida); se ejecutan con el ejecutor común.

21 módulos (ver «Reportes ejecutables»).


## Pruebas (51 archivos)

Reflejan las capas: `tests/dominio`, `tests/aplicacion`, `tests/infraestructura`, `tests/interfaces` y `tests/reportes`.

- `tests/aplicacion/casos_uso/test_archivos.py`
- `tests/aplicacion/casos_uso/test_catalogo.py`
- `tests/aplicacion/casos_uso/test_configuracion.py`
- `tests/aplicacion/casos_uso/test_correo_reporte.py`
- `tests/aplicacion/casos_uso/test_ejecuciones.py`
- `tests/aplicacion/casos_uso/test_google.py`
- `tests/aplicacion/casos_uso/test_herramientas_envio.py`
- `tests/aplicacion/casos_uso/test_notificaciones.py`
- `tests/aplicacion/casos_uso/test_sesion.py`
- `tests/aplicacion/casos_uso/test_validacion.py`
- `tests/aplicacion/casos_uso/test_verificacion.py`
- `tests/aplicacion/test_columnas.py`
- `tests/aplicacion/test_cortes.py`
- `tests/aplicacion/test_destinatarios.py`
- `tests/aplicacion/test_dto.py`
- `tests/aplicacion/test_ejecucion.py`
- `tests/aplicacion/test_errores.py`
- `tests/aplicacion/test_puertos.py`
- `tests/aplicacion/test_rutas.py`
- `tests/aplicacion/test_verificacion.py`
- `tests/dominio/test_entregas.py`
- `tests/dominio/test_errores.py`
- `tests/dominio/test_fechas.py`
- `tests/dominio/test_formato_excel.py`
- `tests/dominio/test_reglas_fecha.py`
- `tests/dominio/test_reportes.py`
- `tests/dominio/test_servidores.py`
- `tests/dominio/test_tablas.py`
- `tests/infraestructura/entregas/test_chat.py`
- `tests/infraestructura/entregas/test_correo_resumen.py`
- `tests/infraestructura/google/test_cliente.py`
- `tests/infraestructura/test_bd.py`
- `tests/infraestructura/test_cola_ejecuciones.py`
- `tests/infraestructura/test_configuracion.py`
- `tests/infraestructura/test_correo_smtp.py`
- `tests/infraestructura/test_entorno.py`
- `tests/infraestructura/test_excel.py`
- `tests/infraestructura/test_historial_validacion.py`
- `tests/infraestructura/test_imagen.py`
- `tests/infraestructura/test_lector_archivos.py`
- `tests/interfaces/cli/test_principal.py`
- `tests/interfaces/cli/test_tablas.py`
- `tests/interfaces/mcp/test_servidor.py`
- `tests/interfaces/web/test_api.py`
- `tests/interfaces/web/test_http.py`
- `tests/interfaces/web/test_middleware.py`
- `tests/reportes/test_formatos_reportes.py`
- `tests/reportes/test_r04_1_cmg_mora.py`
- `tests/reportes/test_reportes_lote.py`
- `tests/test_composicion.py`
- `tests/test_validar_gobernanza.py`
