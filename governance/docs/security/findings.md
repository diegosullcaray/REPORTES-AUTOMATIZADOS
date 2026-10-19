# Hallazgos

| ID | Severidad | Hallazgo | Estado |
|---|---|---|---|
| SEC-001 | **Crítica** | Contraseñas en texto plano en el legado: usuario `master` (escritura) en el script de CMG Mora, y un usuario SQL de lectura en los scripts de Bancarizados y Extranjeros. Siguen en `docs/LEGADO/` y en el historial de git | Abierto |
| SEC-002 | Alta | `cmg_mora` usa una cuenta con privilegios amplios para operaciones puntuales | Abierto |
| SEC-003 | Media | Cachés `.pkl` y TXT de salida con datos reales dentro de `docs/LEGADO/` (versionados) | Abierto |
| SEC-004 | **Crítica** | `governance/tasks/tareasdiarias.md` (subido al remoto) traía en texto plano la contraseña de aplicación de la cuenta de correo `mis@confianza.pe` y la clave+token del webhook de Google Chat (copiados de la macro del legado). Ya están en el historial de git; es probable que también estén dentro del VBA de `Cartera-Sin asignar-base.xlsm` | Abierto (valores ocultos en el archivo; **rotar** la contraseña de aplicación y regenerar el webhook) |
| SEC-005 | Alta | La web (Next.js) escuchaba en todas las interfaces de red: cualquiera en la red llegaba al login, sin HTTPS, y con la clave a la pestaña Script (ejecuta Python) | **Cerrado**: `iniciar.py` la arranca con `-H 127.0.0.1` (la API ya iba a `127.0.0.1`) |
| SEC-006 | Alta | Un reporte creado en la web aceptaba T-SQL de escritura (`DELETE`, `TRUNCATE`, `DROP`…) y se ejecutaba sin la confirmación `--confirmar-escritura` | **Cerrado**: `rechazar_escritura` al crear y al guardar el Script ([ADR-0018](../architecture/adr/ADR-0018-reportes-desde-la-web.md)) |
| SEC-007 | Media | Cambiar la contraseña no cerraba las sesiones abiertas: la cookie se firmaba solo con `SESION_SECRETO` | **Cerrado**: la firma incluye `WEB_CLAVE`; al cambiarla las cookies viejas dejan de valer |
| SEC-008 | Media | El servidor MCP de envío mandaba correo y mensajes a cualquier dirección, saltándose «prueba → conforme» | **Cerrado**: solo envía al dominio de `USER_GOOGLE_EMAIL` o a `CORREO_PRUEBA` (y a espacios `spaces/…`) |
| SEC-009 | Media | Los procesos del Diccionario (`npm`/`node` de otro repo) heredaban el entorno completo de la API: SMTP, bases, Google, `WEB_CLAVE` | **Cerrado**: entorno mínimo ([ADR-0017](../architecture/adr/ADR-0017-modulo-diccionario.md)) |
| SEC-010 | Baja | La API key de Gemini viajaba en la URL (`?key=`) y quedaba en registros del proxy | **Cerrado**: va en la cabecera `x-goog-api-key` |
| SEC-011 | Media | La pestaña Script guarda código Python que luego ejecuta la API: quien tenga sesión ejecuta código en el equipo, con sus credenciales de BD | **Aceptado**: el control es el acceso (login, 5 intentos por usuario, cookie firmada, solo local); git guarda la versión anterior |
| SEC-012 | Baja | «Modelos» de la configuración de IA hace una petición desde el servidor a la URL que escribe quien tenga sesión (puede apuntar a la red interna) | **Aceptado** mientras la API sea solo local |

Los valores no se reproducen en esta documentación.
