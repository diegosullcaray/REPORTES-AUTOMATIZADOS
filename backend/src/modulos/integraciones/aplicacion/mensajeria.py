"""API pública del módulo de integraciones para los demás módulos: enviar por Gmail y Google Chat con la cuenta autorizada.

Los demás módulos no usan los puertos de integraciones: llaman a estas funciones. Los fallos son `ErrorIntegracion`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from modulos.integraciones.aplicacion.puertos import puertos


def token_de_acceso() -> str:
    return puertos().google.token_de_acceso()


def firma_gmail(token: str) -> str:
    return puertos().google.firma_gmail(token)


def armar_correo(para: list[str], cc: list[str], asunto: str, texto: str, firma_html: str = "", adjuntos: list[Path] | None = None) -> Any:
    return puertos().google.armar_correo(para, cc, asunto, texto, firma_html, adjuntos)


def enviar_mensaje(token: str, msg: Any) -> str:
    return puertos().google.enviar_mensaje(token, msg)


def enviar_chat(token: str, para: str, texto: str, adjuntos: list[Path] | None = None) -> str:
    return puertos().google.enviar_chat(token, para, texto, adjuntos)
