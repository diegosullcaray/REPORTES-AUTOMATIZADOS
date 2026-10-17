"""API pública del módulo de notificaciones para los demás módulos: correo corporativo (cuenta MIS) y aviso al webhook de Google Chat.

Los demás módulos no usan los puertos de notificaciones: llaman a estas funciones. Los fallos son `ErrorIntegracion`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from modulos.notificaciones.aplicacion.puertos import puertos


def config_desde_env() -> Any:
    return puertos().correo.config_desde_env()


def leer_destinatarios(ruta: Path | None = None) -> list[str]:
    return puertos().correo.leer_destinatarios(ruta)


def construir_mensaje(cfg: Any, asunto: str, html: str, destinatarios: list[str], **opciones: Any) -> Any:
    return puertos().correo.construir_mensaje(cfg, asunto, html, destinatarios, **opciones)


def enviar(cfg: Any, msg: Any, destinatarios: list[str]) -> None:
    puertos().correo.enviar(cfg, msg, destinatarios)


def notificar_chat(url: str, texto: str) -> None:
    puertos().correo.notificar_chat(url, texto)
