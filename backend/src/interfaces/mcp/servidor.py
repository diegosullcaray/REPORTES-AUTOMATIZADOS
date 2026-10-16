"""Servidor MCP propio (stdio) para ENVIAR: correo por Gmail y mensajes de Google Chat a contactos o espacios.

Interfaz JSON-RPC sobre stdio; las herramientas son un caso de uso (`aplicacion/casos_uso/herramientas_envio.py`).
Complementa a los MCP oficiales de Google (el de Gmail solo crea borradores). Lo lanza el cliente MCP:
`python backend/src/interfaces/mcp/servidor.py`. Usa la cuenta autorizada en la web; credenciales y token solo en el .env.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import composicion  # noqa: E402,F401 - conecta los adaptadores (carga también el .env)
from aplicacion.casos_uso.herramientas_envio import ejecutar, herramientas  # noqa: E402
from dominio.errores import ErrorIntegracion  # noqa: E402

VERSION_PROTOCOLO = "2024-11-05"
NOMBRE = "google-envio"


def responder(msg: dict) -> dict | None:
    """Respuesta JSON-RPC a un mensaje; None si es una notificación (sin id)."""
    metodo, id_ = msg.get("method"), msg.get("id")
    if id_ is None:
        return None
    if metodo == "initialize":
        res = {"protocolVersion": VERSION_PROTOCOLO, "capabilities": {"tools": {}}, "serverInfo": {"name": NOMBRE, "version": "2.0.0"}}
    elif metodo == "ping":
        res = {}
    elif metodo == "tools/list":
        res = {"tools": herramientas()}
    elif metodo == "tools/call":
        p = msg.get("params") or {}
        if p.get("name") not in {h["name"] for h in herramientas()}:
            return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32602, "message": f"Herramienta no disponible: {p.get('name')}"}}
        try:
            res = {"content": [{"type": "text", "text": ejecutar(p["name"], p.get("arguments") or {})}], "isError": False}
        except ErrorIntegracion as exc:
            res = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": f"Método no soportado: {metodo}"}}
    return {"jsonrpc": "2.0", "id": id_, "result": res}


def main() -> int:
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
