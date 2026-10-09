"""Notificaciones de la web: cuenta SMTP para los correos y webhook de Google Chat. Se guardan en el .env.

La clave SMTP y el webhook son de solo escritura: nunca se devuelven al navegador (solo si están configurados).
Rigen de inmediato: el motor lee el .env/entorno en cada envío y las ejecuciones heredan el entorno de la API.
"""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

from reportes.comun import correo
from reportes.config import ConfiguracionError

from . import entorno
from . import esquemas as e
from . import servicios

VARIABLES = {
    "smtp_host": "SMTP_HOST", "smtp_port": "SMTP_PORT", "smtp_user": "SMTP_USER", "smtp_clave": "SMTP_PASSWORD",
    "remitente_nombre": "MAIL_FROM_NAME", "correo_prueba": "CORREO_PRUEBA", "webhook": "GOOGLE_CHAT_WEBHOOK_URL",
}
_HOST = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$")
_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _env(variable: str, defecto: str = "") -> str:
    return os.getenv(variable, defecto).strip()


def leer() -> e.Notificaciones:
    try:
        destinatarios: int | None = len(correo.leer_destinatarios())
    except (OSError, ConfiguracionError, correo.CorreoError):
        destinatarios = None
    try:
        puerto = int(_env("SMTP_PORT", str(correo.PUERTO_DEFECTO)))
    except ValueError:
        puerto = correo.PUERTO_DEFECTO
    return e.Notificaciones(
        smtp_host=_env("SMTP_HOST", correo.HOST_DEFECTO), smtp_port=puerto, smtp_user=_env("SMTP_USER"),
        remitente_nombre=_env("MAIL_FROM_NAME", correo.REMITENTE_DEFECTO), correo_prueba=_env("CORREO_PRUEBA", correo.CORREO_PRUEBA_DEFECTO),
        clave_configurada=bool(_env("SMTP_PASSWORD")), webhook_configurado=bool(_env("GOOGLE_CHAT_WEBHOOK_URL")), destinatarios=destinatarios,
    )


def _validar(campo: str, valor: str) -> str:
    if not valor:
        return ""
    var = VARIABLES[campo]
    if any(c in valor for c in "\r\n#\"'"):
        raise servicios.PeticionInvalida(f"{var}: no admite saltos de línea, # ni comillas.")
    if campo == "smtp_host" and not _HOST.match(valor):
        raise servicios.PeticionInvalida(f"{var}: escribe solo el nombre del servidor (ej. smtp.gmail.com).")
    if campo == "smtp_port" and not (valor.isdigit() and 0 < int(valor) < 65536):
        raise servicios.PeticionInvalida(f"{var}: el puerto debe ser un número entre 1 y 65535.")
    if campo in {"smtp_user", "correo_prueba"} and not _CORREO.match(valor):
        raise servicios.PeticionInvalida(f"{var}: escribe un correo válido.")
    if campo == "webhook":
        url = urlparse(valor)
        if url.scheme != "https" or not (url.hostname or "").endswith(".googleapis.com"):
            raise servicios.PeticionInvalida(f"{var}: debe ser el webhook de Google Chat (una URL https de googleapis.com).")
    return valor


def guardar(p: e.PedidoNotificaciones) -> e.Notificaciones:
    """Solo se cambian los campos enviados; texto vacío quita la variable. Clave y webhook nunca se devuelven."""
    cambios = {VARIABLES[c]: _validar(c, (getattr(p, c) or "").strip()) for c in p.model_fields_set}
    if not cambios:
        raise servicios.PeticionInvalida("No hay ningún ajuste que guardar.")
    entorno.escribir(servicios.ENV, cambios)
    for variable, valor in cambios.items():
        if valor:
            os.environ[variable] = valor
        else:
            os.environ.pop(variable, None)
    return leer()


def probar(canal: str) -> e.PruebaNotificacion:
    """Correo: un mensaje solo a CORREO_PRUEBA (nunca a la lista). Chat: un aviso de prueba al espacio del webhook."""
    if canal not in {"correo", "chat"}:
        raise servicios.NoEncontrado(f"Canal desconocido: {canal}")
    try:
        cfg = correo.config_desde_env()
        if canal == "correo":
            html = "<p>Prueba de configuración de correo desde la web de reportes automatizados. Si lo recibes, la cuenta SMTP funciona.</p>"
            msg = correo.construir_mensaje(cfg, "Prueba de correo · Reportes automatizados", html, [cfg.correo_prueba])
            correo.enviar(cfg, msg, [cfg.correo_prueba])
            return e.PruebaNotificacion(ok=True, detalle=f"Correo de prueba enviado a {cfg.correo_prueba}")
        if not cfg.webhook:
            raise ConfiguracionError("Falta GOOGLE_CHAT_WEBHOOK_URL en el .env")
        correo.notificar_chat(cfg.webhook, "Prueba de configuración desde la web de reportes automatizados.")
        return e.PruebaNotificacion(ok=True, detalle="Aviso de prueba enviado al espacio de Google Chat")
    except (ConfiguracionError, correo.CorreoError) as exc:
        return e.PruebaNotificacion(ok=False, detalle=str(exc))
