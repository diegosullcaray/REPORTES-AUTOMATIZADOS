"""Servidores MCP de la web: catálogo, estado y envío de mensajes a Google Chat.

Hoy hay uno: `google-chat` (src/mcp_chat/servidor.py). La web muestra su estado y la configuración para el cliente MCP
(sin secretos: el webhook se guarda en Notificaciones y vive solo en el .env).
"""

from __future__ import annotations

import os
import sys

from reportes.comun import correo
from reportes.config import RAIZ

from . import esquemas as e
from . import servicios

SERVIDOR_CHAT = RAIZ / "src" / "mcp_chat" / "servidor.py"
MAX_MENSAJE = 4000


def _chat() -> e.ServidorMcp:
    from mcp_chat.servidor import HERRAMIENTAS   # import diferido: el módulo carga dotenv al ejecutarse como servidor
    comando, args = "python", [str(SERVIDOR_CHAT)]
    return e.ServidorMcp(
        id="google-chat", nombre="Google Chat",
        descripcion="Permite a un asistente (Claude Code, Claude Desktop…) publicar mensajes en el espacio de Google Chat del webhook.",
        webhook_configurado=bool(os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "").strip()),
        comando=comando, args=args, python=sys.executable,
        herramientas=[e.HerramientaMcp(nombre=h["name"], descripcion=h["description"]) for h in HERRAMIENTAS],
        configuracion={"mcpServers": {"google-chat": {"command": comando, "args": args}}},
    )


def listar() -> list[e.ServidorMcp]:
    return [_chat()]


def enviar_mensaje(servidor: str, texto: str) -> e.PruebaNotificacion:
    if servidor != "google-chat":
        raise servicios.NoEncontrado(f"Servidor MCP desconocido: {servidor}")
    texto = texto.strip()
    if not texto:
        raise servicios.PeticionInvalida("Escribe el mensaje a enviar.")
    if len(texto) > MAX_MENSAJE:
        raise servicios.PeticionInvalida(f"El mensaje supera {MAX_MENSAJE} caracteres.")
    url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "").strip()
    if not url:
        return e.PruebaNotificacion(ok=False, detalle="Falta el webhook: configúralo en Configuración › Notificaciones › Google Chat.")
    try:
        correo.notificar_chat(url, texto)
    except correo.CorreoError as exc:
        return e.PruebaNotificacion(ok=False, detalle=str(exc))
    return e.PruebaNotificacion(ok=True, detalle="Mensaje enviado al espacio de Google Chat")
