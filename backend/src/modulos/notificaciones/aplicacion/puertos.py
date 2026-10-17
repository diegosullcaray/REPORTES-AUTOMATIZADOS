"""Puertos del módulo de notificaciones: correo corporativo (cuenta MIS) y aviso al webhook de Google Chat."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from core.puertos import Registro


class CorreoSMTP(Protocol):
    PUERTO_DEFECTO: int
    HOST_DEFECTO: str

    def config_desde_env(self) -> Any: ...
    def leer_destinatarios(self, ruta: Path | None = None) -> list[str]: ...
    def construir_mensaje(self, cfg: Any, asunto: str, html: str, destinatarios: list[str], **opciones: Any) -> Any: ...
    def enviar(self, cfg: Any, msg: Any, destinatarios: list[str]) -> None: ...
    def notificar_chat(self, url: str, texto: str) -> None: ...


@dataclass
class Puertos:
    correo: CorreoSMTP


puertos: Registro[Puertos] = Registro("notificaciones")
