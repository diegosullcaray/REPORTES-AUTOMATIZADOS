"""Servidor MCP de Google Workspace (mcp_google/servidor.py): herramientas por servicio, solo lectura y proceso stdio."""

import json
import subprocess
import sys

import pytest

from mcp_google import cliente as g
from mcp_google import servidor


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("GOOGLE_MCP_SERVICIOS", "gmail,chat,contacts,drive,sheets")
    monkeypatch.delenv("GOOGLE_MCP_SOLO_LECTURA", raising=False)
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")


def nombres():
    return [h["name"] for h in servidor.herramientas()]


def test_herramientas_segun_servicios_y_solo_lectura(env, monkeypatch):
    assert nombres() == ["enviar_correo", "enviar_mensaje_chat", "listar_espacios_chat", "buscar_contacto", "buscar_archivos"]
    tipos = servidor.herramientas()[-1]["inputSchema"]["properties"]["tipo"]["enum"]
    assert tipos == ["drive", "sheets"]
    monkeypatch.setenv("GOOGLE_MCP_SOLO_LECTURA", "true")
    assert "enviar_correo" not in nombres() and "enviar_mensaje_chat" not in nombres()


def test_protocolo(env, monkeypatch):
    enviados = []
    monkeypatch.setattr(g, "enviar_chat", lambda token, para, texto: enviados.append((token, para, texto)))
    assert servidor.responder({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert servidor.responder({"jsonrpc": "2.0", "id": 1, "method": "initialize"})["result"]["serverInfo"]["name"] == "google-workspace"
    ok = servidor.responder({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                             "params": {"name": "enviar_mensaje_chat", "arguments": {"para": "ana@x.pe", "texto": "hola"}}})
    assert ok["result"]["isError"] is False and enviados == [("tok", "ana@x.pe", "hola")]
    vacio = servidor.responder({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "enviar_correo", "arguments": {"para": "a@x.pe"}}})
    assert vacio["result"]["isError"] is True
    no = servidor.responder({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "listar_tareas"}})
    assert no["error"]["code"] == -32602   # tasks no está activo


def test_proceso_stdio(tmp_path):
    entrada = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\nno-json\n"
    p = subprocess.run([sys.executable, str(servidor.__file__)], input=entrada, capture_output=True, text=True, timeout=30)
    lineas = [json.loads(x) for x in p.stdout.splitlines()]
    assert "tools" in lineas[0]["result"] and lineas[1]["error"]["code"] == -32700
