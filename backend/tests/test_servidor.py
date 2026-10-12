"""Servidor MCP de Google Chat (mcp_chat/servidor.py): protocolo JSON-RPC y proceso stdio."""

import json
import subprocess
import sys

import pytest

from mcp_chat import servidor
from reportes.comun import correo

WEBHOOK = "https://chat.googleapis.com/v1/spaces/AAA/messages?key=K&token=T"


@pytest.fixture
def enviados(monkeypatch):
    salida = []
    monkeypatch.setattr(correo, "notificar_chat", lambda url, texto: salida.append((url, texto)))
    return salida


def test_protocolo_del_servidor(monkeypatch, enviados):
    monkeypatch.setenv("GOOGLE_CHAT_WEBHOOK_URL", WEBHOOK)
    assert servidor.responder({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    ini = servidor.responder({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert ini["result"]["serverInfo"]["name"] == "google-chat"
    lista = servidor.responder({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert lista["result"]["tools"][0]["name"] == "enviar_mensaje_chat"
    ok = servidor.responder({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "enviar_mensaje_chat", "arguments": {"texto": "hola"}}})
    assert ok["result"]["isError"] is False and enviados == [(WEBHOOK, "hola")]
    vacio = servidor.responder({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "enviar_mensaje_chat", "arguments": {}}})
    assert vacio["result"]["isError"] is True
    assert servidor.responder({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "x"}})["error"]["code"] == -32602


def test_servidor_como_proceso_stdio():
    entrada = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\nno-json\n"
    p = subprocess.run([sys.executable, str(servidor.__file__)], input=entrada, capture_output=True, text=True, timeout=30)
    lineas = [json.loads(x) for x in p.stdout.splitlines()]
    assert lineas[0]["result"]["tools"][0]["name"] == "enviar_mensaje_chat" and lineas[1]["error"]["code"] == -32700
