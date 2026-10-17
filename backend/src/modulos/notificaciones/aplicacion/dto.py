"""Contratos del módulo de notificaciones (correo SMTP y webhook de Google Chat). Solo forma de los datos: sin lógica."""

from __future__ import annotations

from pydantic import BaseModel


class Notificaciones(BaseModel):
    """Correo (SMTP) y Google Chat. La clave y el webhook nunca se devuelven: solo si están configurados."""

    smtp_host: str
    smtp_port: int
    smtp_user: str
    remitente_nombre: str
    correo_prueba: str
    clave_configurada: bool
    webhook_configurado: bool
    destinatarios: int | None


class PedidoNotificaciones(BaseModel):
    """Solo se cambian los campos enviados; texto vacío = quitar la variable del .env."""

    smtp_host: str | None = None
    smtp_port: str | None = None
    smtp_user: str | None = None
    smtp_clave: str | None = None
    remitente_nombre: str | None = None
    correo_prueba: str | None = None
    webhook: str | None = None
