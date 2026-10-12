"""Servidor MCP (stdio) de Google Workspace: Gmail, Chat directo a contactos, Contactos, Calendar, Drive y Tasks.

Lo lanza el cliente MCP (Claude Code, Claude Desktop…): `python backend/src/mcp_google/servidor.py`.
Usa la cuenta autorizada en la web (MCP › Google Workspace); credenciales y token solo en el .env.
Las herramientas dependen de GOOGLE_MCP_SERVICIOS; con GOOGLE_MCP_SOLO_LECTURA=true no se ofrecen las que envían.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

from mcp_google import cliente as g  # noqa: E402

VERSION_PROTOCOLO = "2024-11-05"
NOMBRE = "google-workspace"
MAX_TEXTO = 4000
ARCHIVOS = ["drive", "docs", "sheets", "slides", "forms"]


def _obj(props: dict, requeridos: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": requeridos}


_TXT = {"type": "string"}
# (servicio, envía, definición)
_CATALOGO = [
    ("gmail", True, {"name": "enviar_correo", "description": "Envía un correo desde la cuenta de Google autorizada.",
                     "inputSchema": _obj({"para": {**_TXT, "description": "Correo del destinatario (varios separados por coma)."},
                                          "asunto": _TXT, "cuerpo": {**_TXT, "description": "Texto del correo."}}, ["para", "asunto", "cuerpo"])}),
    ("chat", True, {"name": "enviar_mensaje_chat",
                    "description": "Envía un mensaje de Google Chat como la cuenta autorizada: directo a un contacto (por su correo) o a un espacio (spaces/…).",
                    "inputSchema": _obj({"para": {**_TXT, "description": "Correo del contacto o nombre del espacio spaces/…"}, "texto": _TXT}, ["para", "texto"])}),
    ("chat", False, {"name": "listar_espacios_chat", "description": "Lista los espacios y mensajes directos de Google Chat de la cuenta.", "inputSchema": _obj({}, [])}),
    ("contacts", False, {"name": "buscar_contacto", "description": "Busca contactos (y el directorio de la organización) por nombre o correo.",
                         "inputSchema": _obj({"consulta": _TXT}, ["consulta"])}),
    ("calendar", False, {"name": "proximos_eventos", "description": "Próximos eventos del calendario principal.",
                         "inputSchema": _obj({"cantidad": {"type": "integer", "minimum": 1, "maximum": 50}}, [])}),
    ("tasks", False, {"name": "listar_tareas", "description": "Listas de tareas de Google Tasks.", "inputSchema": _obj({}, [])}),
]


def herramientas() -> list[dict]:
    activos, lectura = set(g.servicios_activos()), g.solo_lectura()
    lista = [d for s, envia, d in _CATALOGO if s in activos and not (envia and lectura)]
    tipos = [s for s in ARCHIVOS if s in activos]
    if tipos:
        lista.append({"name": "buscar_archivos", "description": "Busca archivos de Drive por nombre (opcional: tipo docs, sheets, slides o forms).",
                      "inputSchema": _obj({"consulta": _TXT, "tipo": {"type": "string", "enum": tipos}}, [])})
    return lista


def _texto(valor: object, campo: str) -> str:
    valor = valor.strip() if isinstance(valor, str) else ""
    if not valor:
        raise g.GoogleError(f"Falta «{campo}».")
    if len(valor) > MAX_TEXTO:
        raise g.GoogleError(f"«{campo}» supera {MAX_TEXTO} caracteres.")
    return valor


def ejecutar(nombre: str, a: dict) -> str:
    token = g.token_de_acceso()
    if nombre == "enviar_correo":
        g.enviar_correo(token, _texto(a.get("para"), "para"), _texto(a.get("asunto"), "asunto"), _texto(a.get("cuerpo"), "cuerpo"))
        return f"Correo enviado a {a['para']}."
    if nombre == "enviar_mensaje_chat":
        g.enviar_chat(token, _texto(a.get("para"), "para"), _texto(a.get("texto"), "texto"))
        return f"Mensaje de Google Chat enviado a {a['para']}."
    if nombre == "listar_espacios_chat":
        return json.dumps(g.espacios_chat(token), ensure_ascii=False)
    if nombre == "buscar_contacto":
        return json.dumps(g.buscar_contactos(token, _texto(a.get("consulta"), "consulta")), ensure_ascii=False)
    if nombre == "proximos_eventos":
        return json.dumps(g.proximos_eventos(token, int(a.get("cantidad") or 5)), ensure_ascii=False)
    if nombre == "listar_tareas":
        return json.dumps(g.listas_tareas(token), ensure_ascii=False)
    if nombre == "buscar_archivos":
        return json.dumps(g.buscar_archivos(token, str(a.get("consulta") or ""), a.get("tipo")), ensure_ascii=False)
    raise g.GoogleError(f"Herramienta desconocida: {nombre}")


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
        except g.GoogleError as exc:
            res = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
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
