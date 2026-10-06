"""Envío de correos con la cuenta MIS (SMTP de Gmail) y aviso al webhook de Google Chat.

Todas las credenciales salen del `.env` (nunca del código): SMTP_USER, SMTP_PASSWORD, GOOGLE_CHAT_WEBHOOK_URL, etc.
"""

from __future__ import annotations

import json
import mimetypes
import os
import smtplib
import urllib.error
import urllib.request
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from ..config import RAIZ, ConfiguracionError

DESTINATARIOS_DEFECTO = RAIZ / "data" / "inputs" / "correos_cartera_sin_asignar.txt"


class CorreoError(RuntimeError):
    """No se pudo enviar el correo o el aviso."""


@dataclass(frozen=True)
class ConfigCorreo:
    host: str
    puerto: int
    usuario: str
    clave: str
    remitente_nombre: str
    correo_prueba: str
    logo: Path | None
    webhook: str | None

    @property
    def remitente(self) -> str:
        return formataddr((self.remitente_nombre, os.getenv("MAIL_FROM") or self.usuario))


def config_desde_env() -> ConfigCorreo:
    usuario, clave = os.getenv("SMTP_USER", "").strip(), os.getenv("SMTP_PASSWORD", "").strip()
    if not usuario or not clave:
        raise ConfiguracionError("Falta SMTP_USER y SMTP_PASSWORD en el .env (cuenta MIS para enviar correos)")
    try:
        puerto = int(os.getenv("SMTP_PORT", "465"))
    except ValueError as exc:
        raise ConfiguracionError("SMTP_PORT en el .env debe ser un número (465 por defecto)") from exc
    return ConfigCorreo(
        host=os.getenv("SMTP_HOST", "smtp.gmail.com").strip(), puerto=puerto, usuario=usuario, clave=clave,
        remitente_nombre=os.getenv("MAIL_FROM_NAME", "Sistemas de Información de Gestión").strip(),
        correo_prueba=os.getenv("CORREO_PRUEBA", "diego.sullcaray@confianza.pe").strip(),
        logo=Path(os.environ["LOGO_PATH"]) if os.getenv("LOGO_PATH", "").strip() else None,   # opcional: logo de la firma
        webhook=(os.getenv("GOOGLE_CHAT_WEBHOOK_URL") or "").strip() or None,
    )


def leer_destinatarios(ruta: Path | None = None) -> list[str]:
    """Un correo por línea (sin duplicados —sin distinguir mayúsculas—, sin líneas vacías ni comentarios `#`)."""
    ruta = ruta or Path(os.getenv("CORREOS_SIN_ASIGNAR_ARCHIVO", DESTINATARIOS_DEFECTO))
    if not ruta.exists():
        raise ConfiguracionError(f"No existe la lista de destinatarios: {ruta} (un correo por línea)")
    vistos: dict[str, str] = {}   # clave en minúsculas -> dirección tal como se escribió la primera vez
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0].strip()
        if linea:
            vistos.setdefault(linea.lower(), linea)
    if not vistos:
        raise ConfiguracionError(f"La lista de destinatarios está vacía: {ruta}")
    return list(vistos.values())


def construir_mensaje(cfg: ConfigCorreo, asunto: str, html: str, destinatarios: list[str], *, en_linea: dict[str, Path] | None = None,
                      adjuntos: list[Path] | None = None) -> EmailMessage:
    """HTML con imágenes incrustadas (`<img src='cid:nombre'>`) y archivos adjuntos."""
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = cfg.remitente, ", ".join(destinatarios), asunto
    msg.set_content("Este correo requiere un cliente que muestre HTML.")
    msg.add_alternative(html, subtype="html")
    cuerpo_html = msg.get_payload()[1]
    for cid, ruta in (en_linea or {}).items():
        tipo, _ = mimetypes.guess_type(ruta.name)
        principal, _, sub = (tipo or "image/jpeg").partition("/")
        cuerpo_html.add_related(ruta.read_bytes(), maintype=principal, subtype=sub, cid=f"<{cid}>", filename=ruta.name)
    for ruta in adjuntos or []:
        tipo, _ = mimetypes.guess_type(ruta.name)
        principal, _, sub = (tipo or "application/octet-stream").partition("/")
        msg.add_attachment(ruta.read_bytes(), maintype=principal, subtype=sub, filename=ruta.name)
    return msg


def enviar(cfg: ConfigCorreo, msg: EmailMessage, destinatarios: list[str]) -> None:
    try:
        with smtplib.SMTP_SSL(cfg.host, cfg.puerto, timeout=60) as smtp:
            smtp.login(cfg.usuario, cfg.clave)
            smtp.send_message(msg, from_addr=cfg.usuario, to_addrs=destinatarios)
    except smtplib.SMTPAuthenticationError as exc:
        raise CorreoError("El servidor de correo rechazó la cuenta MIS (usuario o contraseña de aplicación inválidos)") from exc
    except (smtplib.SMTPException, OSError) as exc:
        raise CorreoError(f"No se pudo enviar el correo ({type(exc).__name__}): {str(exc)[:200]}") from exc


def notificar_chat(url: str, texto: str) -> None:
    """Aviso al espacio de Google Chat (webhook entrante)."""
    datos = json.dumps({"text": texto}).encode("utf-8")
    req = urllib.request.Request(url, data=datos, headers={"Content-Type": "application/json; charset=UTF-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 - URL del .env, https
            if resp.status != 200:
                raise CorreoError(f"Google Chat respondió {resp.status}")
    except (urllib.error.URLError, OSError) as exc:
        raise CorreoError(f"No se pudo avisar a Google Chat ({type(exc).__name__})") from exc
