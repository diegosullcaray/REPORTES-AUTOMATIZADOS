"""Servidor MCP (stdio) para enviar mensajes a Google Chat con el webhook del .env.

Lo lanza el cliente MCP (Claude Code, Claude Desktop…): `python backend/src/mcp_chat/servidor.py`.
Protocolo mínimo de MCP sobre JSON-RPC, un mensaje por línea. El webhook sale solo del .env y nunca se devuelve ni se registra.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

from reportes.comun import correo  # noqa: E402

VERSION_PROTOCOLO = "2024-11-05"
NOMBRE = "google-chat"
MAX_TEXTO = 4000

HERRAMIENTAS = [{
    "name": "enviar_mensaje_chat",
    "description": "Publica un mensaje de texto en el espacio de Google Chat configurado (GOOGLE_CHAT_WEBHOOK_URL). Lo ven todos sus miembros.",
    "inputSchema": {
        "type": "object",
        "properties": {"texto": {"type": "string", "description": "Mensaje a publicar (admite *negrita* y _cursiva_ de Google Chat)."}},
        "required": ["texto"],
    },
}]


def _resultado(texto: str, error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": texto}], "isError": error}


def enviar_mensaje_chat(texto: object) -> dict:
    texto = texto.strip() if isinstance(texto, str) else ""
    if not texto:
        return _resultado("El mensaje no puede estar vacío.", True)
    if len(texto) > MAX_TEXTO:
        return _resultado(f"El mensaje supera {MAX_TEXTO} caracteres.", True)
    url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "").strip()
    if not url:
        return _resultado("Falta GOOGLE_CHAT_WEBHOOK_URL en el .env.", True)
    try:
        correo.notificar_chat(url, texto)
    except correo.CorreoError as exc:
        return _resultado(str(exc), True)
    return _resultado("Mensaje enviado a Google Chat.")


def responder(msg: dict) -> dict | None:
    """Respuesta JSON-RPC a un mensaje; None si es una notificación (sin id)."""
    metodo, id_ = msg.get("method"), msg.get("id")
    if id_ is None:
        return None
    if metodo == "initialize":
        res = {"protocolVersion": VERSION_PROTOCOLO, "capabilities": {"tools": {}}, "serverInfo": {"name": NOMBRE, "version": "1.0.0"}}
    elif metodo == "ping":
        res = {}
    elif metodo == "tools/list":
        res = {"tools": HERRAMIENTAS}
    elif metodo == "tools/call":
        p = msg.get("params") or {}
        if p.get("name") != "enviar_mensaje_chat":
            return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32602, "message": f"Herramienta desconocida: {p.get('name')}"}}
        res = enviar_mensaje_chat((p.get("arguments") or {}).get("texto"))
    else:
        return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": f"Método no soportado: {metodo}"}}
    return {"jsonrpc": "2.0", "id": id_, "result": res}


def main() -> int:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    for linea in sys.stdin:
        if not linea.strip():
            continue
        try:
            msg = json.loads(linea)
            if not isinstance(msg, dict):
                raise ValueError
        except ValueError:
            respuesta = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}}
        else:
            respuesta = responder(msg)
        if respuesta is not None:
            sys.stdout.write(json.dumps(respuesta, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
