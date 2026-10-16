"""Herramientas MCP propias para ENVIAR: correo por Gmail y mensajes de Google Chat a contactos o espacios.

Complementan a los MCP oficiales de Google (el de Gmail solo crea borradores). La interfaz MCP (`interfaces/mcp/servidor.py`)
las expone por stdio; aquí están su catálogo y lo que hace cada una.
"""

from __future__ import annotations

import json

from aplicacion.puertos import puertos
from dominio.errores import ErrorIntegracion

MAX_TEXTO = 4000


def _obj(props: dict, requeridos: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": requeridos}


_TXT = {"type": "string"}
_CATALOGO = [   # (servicio, definición)
    ("gmail", {"name": "enviar_correo", "description": "Envía un correo desde la cuenta de Google autorizada.",
               "inputSchema": _obj({"para": {**_TXT, "description": "Correo del destinatario (varios separados por coma)."},
                                    "asunto": _TXT, "cuerpo": {**_TXT, "description": "Texto del correo."}}, ["para", "asunto", "cuerpo"])}),
    ("chat", {"name": "enviar_mensaje_chat",
              "description": "Envía un mensaje de Google Chat como la cuenta autorizada: directo a un contacto (por su correo) o a un espacio (spaces/…).",
              "inputSchema": _obj({"para": {**_TXT, "description": "Correo del contacto o nombre del espacio spaces/…"}, "texto": _TXT}, ["para", "texto"])}),
    ("chat", {"name": "listar_espacios_chat", "description": "Lista los espacios y mensajes directos de Google Chat de la cuenta.", "inputSchema": _obj({}, [])}),
]


def herramientas() -> list[dict]:
    """Las herramientas de los servicios activos."""
    activos = set(puertos().google.servicios_activos())
    return [d for s, d in _CATALOGO if s in activos]


def _texto(valor: object, campo: str) -> str:
    valor = valor.strip() if isinstance(valor, str) else ""
    if not valor:
        raise ErrorIntegracion(f"Falta «{campo}».")
    if len(valor) > MAX_TEXTO:
        raise ErrorIntegracion(f"«{campo}» supera {MAX_TEXTO} caracteres.")
    return valor


def ejecutar(nombre: str, a: dict) -> str:
    google = puertos().google
    token = google.token_de_acceso()
    if nombre == "enviar_correo":
        google.enviar_correo(token, _texto(a.get("para"), "para"), _texto(a.get("asunto"), "asunto"), _texto(a.get("cuerpo"), "cuerpo"))
        return f"Correo enviado a {a['para']}."
    if nombre == "enviar_mensaje_chat":
        google.enviar_chat(token, _texto(a.get("para"), "para"), _texto(a.get("texto"), "texto"))
        return f"Mensaje de Google Chat enviado a {a['para']}."
    if nombre == "listar_espacios_chat":
        return json.dumps(google.espacios_chat(token), ensure_ascii=False)
    raise ErrorIntegracion(f"Herramienta desconocida: {nombre}")
