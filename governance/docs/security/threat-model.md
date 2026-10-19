# Modelo de amenazas

| Activo | Amenaza | Control |
|---|---|---|
| Cuenta de correo MIS y webhook de Google Chat | filtración por macros/documentos; envío masivo no deseado | solo `.env`; prueba a un correo antes de enviar a la lista; `--conforme` obligatorio; no reenviar sin `--reenviar` |
| Credenciales de BD | filtración vía repositorio | solo `.env`; regla `secretos-en-codigo` |
| Servidor `rcc` / base `DW_Raw_v2` (escritura; hoy con usuario `master`) | ejecución accidental o dos veces | usuario dedicado de mínimo privilegio; abortos por validación |
| Datos de clientes en `data/outputs/` | fuga por git o correo | `data/outputs/*` ignorado; clasificación [restringido/confidencial](../data/classification.md) |
| SQL dinámico (`PROV_PROY_<fecha>`) | inyección | la fecha se genera con `strftime` de una `date`, no de texto libre |
| Acceso a la web y a la API | uso sin autenticación; fuerza bruta | `WEB_USUARIO`/`WEB_CLAVE` del `.env` (sin ellas nadie entra); cookie firmada `HttpOnly` `SameSite=Strict`; 5 intentos por usuario cada 5 min; API solo en `127.0.0.1` ([ADR-0012](../architecture/adr/ADR-0012-acceso-a-la-web-y-ajustes-editables.md)) |
| `.env` editado desde la web | inyección de variables (saltos de línea, `#`), pérdida del archivo, fuga de secretos al navegador | solo claves permitidas; valores validados sin saltos de línea, `#` ni comillas; reemplazo atómico; clave SMTP, webhook y clave web de solo escritura |
| Clave de la web en texto plano en el `.env` | lectura del archivo por otro usuario del equipo | riesgo aceptado mientras la API sea solo local; hash + TLS antes de exponerla en red |
| Web y API accesibles desde la red | acceso de otro equipo al login y al editor de Script | la web escucha solo en `127.0.0.1` (`iniciar.py`, `-H 127.0.0.1`); la API también; ver SEC-005 |
| Sesión abierta tras cambiar la contraseña | uso de una cookie robada hasta 8 h | la cookie se firma con `SESION_SECRETO` **y** `WEB_CLAVE`: cambiar la clave invalida las anteriores |
| Reportes creados y editados desde la web | T-SQL que escribe o borra en bases reales; código Python arbitrario | el T-SQL pasa por `rechazar_escritura` (solo lectura salvo `#temporales`); la marca «Creado desde la web» no se puede copiar a un reporte del legado; el Script exige sesión ([ADR-0018](../architecture/adr/ADR-0018-reportes-desde-la-web.md)); riesgo aceptado SEC-011 |
| Servidor MCP de envío (`google-envio`) | un agente de IA o un texto malicioso manda correos en nombre de la cuenta | solo destinatarios del dominio de la cuenta o `CORREO_PRUEBA`; el envío a listas sigue siendo prueba → conforme en la web |
| Código de los SP (`sys.sql_modules`) leído para analizarlo | una credencial embebida en un SP acaba en el diccionario, el log o el repo | solo se guarda el análisis (nombres de tablas, columnas, parámetros), nunca el texto; el log no lo repite; `data/outputs/` no se versiona |
| Procesos del Diccionario (generar y validar) | una petición que lance algo distinto o dos procesos a la vez | lista cerrada en `PROCESOS`, corren dentro de la API sin subprocesos ni shell, uno a la vez con candado ([ADR-0017](../architecture/adr/ADR-0017-modulo-diccionario.md)) |
| Consultas del Diccionario a las bases (`RREGREP01`, dependencias, parámetros y estructura) | bloquear la tabla que usa el backend del MIS; escribir o ejecutar un SP por error; inyección por un nombre de SP leído de la base | solo `SELECT` de catálogos y metadatos (`NOLOCK` en `RREGREP01`), sin `EXEC` de SP de reporte; los nombres van como parámetros `?`; esperas acotadas; las credenciales de cada servidor del `.env` (o Windows) |
| Edición simultánea del registro (reportes, grupos, etiquetas) | archivos del registro a medio escribir o pisados | candado único (`aplicacion/exclusivo.py`) y restauración de los textos originales si falla una escritura |
