# Runbook: `cartera-sin-asignar` (diario, legado «02 Cartera sin asignar»)

Reemplaza la macro `ActualizarSQL_AmbasHojas` del Excel del legado (spec original: `governance/tasks/tareasdiarias.md`).
**Conexión**: servidor `mish`, base `storage`. **Fecha**: por defecto **ayer** (`Date - 1`, también los lunes), o `FECHA_CORTE_DIARIA` del `.env`, o `--fecha-corte`.

## Flujo en dos pasos (con tu aprobación en medio)

### Paso 1 — ejecutar y enviar la PRUEBA a tu correo
```bash
python main.py cartera-sin-asignar            # (o con --fecha-corte AAAA-MM-DD)
```
1. Valida las tablas al corte (`storage.com_act.hcda001`, `sdas001`, …). Si falta alguna **no ejecuta** y deja el mensaje para Producción.
2. Ejecuta la consulta, valida los datos y genera el Excel `Cartera-Sin asignar-AAAA-MM-DD.xlsx` (hojas `DATA_MIS_v2` y `RESUMEN_v2`).
3. Genera la imagen del resumen `Reporte_Temporal_AAAA-MM-DD.jpg` (la tabla que va dentro del correo).
4. Envía **una prueba solo a `CORREO_PRUEBA`** (por defecto `diego.sullcaray@confianza.pe`) con la cuenta MIS, asunto `[PRUEBA] Reporte Sin Asignar - AAAA-MM-DD`, la imagen en el cuerpo, la firma y el Excel adjunto. Guarda un archivo de estado `estado_envio_AAAAMMDD.json`.

### Paso 2 — cuando estés conforme, enviar a todos
```bash
python main.py cartera-sin-asignar --fecha-corte AAAA-MM-DD --correo todos --conforme
```
- Envía **el mismo Excel y la misma imagen de la prueba aprobada** a toda la lista `data/inputs/correos_cartera_sin_asignar.txt` (un solo correo con todos en «Para», como la macro), asunto `Reporte Sin Asignar - AAAA-MM-DD`.
- **No consulta de nuevo la base.**
- Avisa al espacio de Google Chat (webhook) con fecha, archivo, destinatarios y hora.
- Se niega si no pasaste `--conforme`, si no hubo prueba para esa fecha, o si ya se envió a todos (`--reenviar` lo permite).

Otras opciones: `--correo no` (solo Excel e imagen, sin enviar nada) · `--solo-verificar` (solo tablas) · `--forzar` · `--sin-verificar`.

## Configuración (`.env`, nunca en el código)
| Variable | Para qué |
|---|---|
| `SMTP_USER`, `SMTP_PASSWORD` | cuenta MIS (`mis@confianza.pe`) y su **contraseña de aplicación** de Gmail |
| `SMTP_HOST`, `SMTP_PORT` | `smtp.gmail.com`, `465` (por defecto) |
| `MAIL_FROM_NAME` | «Sistemas de Información de Gestión» |
| `CORREO_PRUEBA` | quién recibe la prueba |
| `LOGO_PATH` | logo de la firma (opcional; sin él, la firma va sin logo) |
| `GOOGLE_CHAT_WEBHOOK_URL` | aviso al espacio de Google Chat (opcional) |
| `CORREOS_SIN_ASIGNAR_ARCHIVO` | otra lista de destinatarios (opcional) |

La lista de destinatarios (76 correos, tomada de la hoja `CORREOS` del Excel original) se edita en `data/inputs/correos_cartera_sin_asignar.txt`: un correo por línea, `#` para comentarios; los repetidos (sin distinguir mayúsculas) se envían una vez.

## Si algo falla
| Mensaje | Qué hacer |
|---|---|
| `Falta SMTP_USER y SMTP_PASSWORD` | completa la cuenta MIS en tu `.env`; el Excel ya se generó |
| `rechazó la cuenta MIS` | la contraseña de aplicación no es válida o fue revocada: pide una nueva |
| `No hay una prueba enviada para …` | ejecuta el paso 1 para esa fecha |
| `Ya se envió a todos el …` | usa `--reenviar` solo si de verdad quieres repetirlo |
| `No se pudo avisar a Google Chat` | solo es un aviso; el correo ya salió |

## Seguridad
La contraseña de la cuenta MIS y el webhook **no** van en código ni documentos: el archivo `governance/tasks/tareasdiarias.md` los traía en texto plano y se ocultaron ([SEC-004](../../security/findings.md)); hay que **rotarlos**.
