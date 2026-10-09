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
