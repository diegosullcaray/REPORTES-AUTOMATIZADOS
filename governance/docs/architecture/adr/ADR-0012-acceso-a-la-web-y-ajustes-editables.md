# ADR-0012: Acceso a la web con credenciales del `.env` y ajustes editables

- Estado: Vigente
- Fecha: 2026-10-08
- Sustituye: el punto 6 de [ADR-0011](./ADR-0011-interfaz-web.md) («no hay login»)

## Contexto

La web ejecuta reportes que escriben en bases de datos y envían correos. Sin autenticación, cualquiera que llegue a
`localhost:3000` (o a la API) podía hacerlo. Además, cambiar un corte, una carpeta o la cuenta de correo obligaba a editar
el `.env` a mano y reiniciar.

## Decisión

1. **Inicio de sesión con usuario y clave del `.env`** (`WEB_USUARIO`, `WEB_CLAVE`). Si falta alguna, **nadie entra**. Se probó
   y descartó validar contra la cuenta de Windows (`LogonUser`): depende del entorno y de la pertenencia a un dominio.
2. **Cookie de sesión firmada** (HMAC con `SESION_SECRETO`; sin él, un secreto por arranque), `HttpOnly`, `SameSite=Strict`,
   8 horas. **Toda `/api` exige sesión** salvo iniciar sesión y consultarla (middleware en `app.py`). `proxy.ts` del
   frontend solo redirige a `/login` si no hay cookie; la firma la valida siempre la API.
3. **Límite de intentos**: 5 fallos por usuario cada 5 minutos (429). Comparación de credenciales en tiempo constante.
4. **Ajustes editables desde la web**, con edición acotada del `.env` (`src/api/entorno.py`): solo se cambian las claves
   enviadas, el resto del archivo (secretos incluidos) queda intacto y el reemplazo es atómico.
   - Configuración: `FECHA_CORTE_MENSUAL`, `FECHA_CORTE_DIARIA` (rigen en la próxima ejecución, porque la API actualiza su
     entorno y las ejecuciones lo heredan), `REPORTES_DIR_INPUTS`, `REPORTES_DIR_OUTPUTS`, `DB_ODBC_DRIVER` (al reiniciar la API).
   - Notificaciones: `SMTP_*`, `MAIL_FROM_NAME`, `CORREO_PRUEBA`, `GOOGLE_CHAT_WEBHOOK_URL` (rigen en el próximo envío).
   - Cuenta: `WEB_USUARIO` y `WEB_CLAVE`, siempre con la contraseña actual.
5. **Secretos de solo escritura**: la clave SMTP, el webhook y la clave web **nunca** se devuelven al navegador (solo si están
   configurados). Los valores se validan (formato, rango, sin saltos de línea, `#` ni comillas) antes de escribir.
6. **Pruebas con alcance mínimo**: la prueba de correo llega solo a `CORREO_PRUEBA` (regla 8 de `AGENTS.md`); la de
   Google Chat pide confirmación porque publica en un espacio compartido.
7. **Validación masiva de tablas** (`/validacion`): una sección por responsable (Piero, Erick) con sus reportes mensuales;
   cada tabla distinta se consulta una sola vez y se genera **un único mensaje** para Producción. Reemplaza la pestaña de
   validación que había en cada reporte.

## Consecuencias

- Los secretos siguen solo en el `.env` ([ADR-0002](./ADR-0002-secretos-solo-en-env.md)); la web es otro modo de editarlo, no otro almacén.
- La clave web queda en texto plano en el `.env`, igual que las contraseñas de las bases. Es un riesgo aceptado mientras la
  API escuche solo en `127.0.0.1`; exponerla en red requiere TLS, hash de la clave y otro ADR.
- Cambiar el `.env` por la web no actualiza otros procesos ya iniciados (p. ej. una consola abierta).
- Los reportes diarios ya no tienen verificación de tablas en la web (siguen con `tablas <reporte> --verificar` y con la
  que hace el propio reporte al ejecutar).
