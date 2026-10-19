# Plan de remediación

| ID | Acción | Responsable | Estado |
|---|---|---|---|
| SEC-001 | Rotar las contraseñas expuestas; después, si el repo es compartido, purgar el historial (`git filter-repo`) | Admin BD + Seguridad | Pendiente |
| SEC-001 | Código nuevo sin literales (regla automática) | Desarrollo | Hecho |
| SEC-002 | Crear usuario dedicado para `CMGMora_Recaudo` con permisos mínimos | Admin BD | Pendiente |
| SEC-003 | Retirar `*.pkl` y salidas reales de `docs/LEGADO/` del repo | Desarrollo | Pendiente |
| SEC-004 | Rotar la contraseña de aplicación de `mis@confianza.pe` y regenerar el webhook de Google Chat; en el código ambos solo se leen de `.env` (`SMTP_PASSWORD`, `GOOGLE_CHAT_WEBHOOK_URL`) | Seguridad + dueño de la cuenta | Pendiente |
| SEC-005 | Web solo en `127.0.0.1`; si algún día se comparte en red: HTTPS y hash de la clave antes de abrir el puerto | Desarrollo | Hecho (solo local) |
| SEC-006 | T-SQL de solo lectura en reportes de la web; escribir en una base se hace con un reporte del legado | Desarrollo | Hecho |
| SEC-007 | Firmar la cookie con la clave web | Desarrollo | Hecho |
| SEC-008 | Restringir el servidor MCP de envío a la organización y al correo de prueba | Desarrollo | Hecho |
| SEC-009 | Entorno mínimo para los procesos del repo `DICCIONARIO` | Desarrollo | Hecho |
| SEC-010 | Clave de Gemini en cabecera | Desarrollo | Hecho |
| SEC-011 | Si la web se comparte con más personas: sacar la edición del Script de la web o exigir otro rol | Desarrollo + Seguridad | Aceptado (un solo usuario, local) |
