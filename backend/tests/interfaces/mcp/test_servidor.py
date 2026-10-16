"""Servidor MCP propio de envío (interfaces/mcp/servidor.py): herramientas según servicios activos y proceso stdio."""

import json
import subprocess
import sys

import pytest

from aplicacion.casos_uso import herramientas_envio
from infraestructura.google import cliente as g
from interfaces.mcp import servidor


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("GOOGLE_MCP_SERVICIOS", "gmail,chat,drive")
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")


def nombres():
    return [h["name"] for h in herramientas_envio.herramientas()]


def test_herramientas_segun_servicios(env, monkeypatch):
    assert nombres() == ["enviar_correo", "enviar_mensaje_chat", "listar_espacios_chat"]
    monkeypatch.setenv("GOOGLE_MCP_SERVICIOS", "drive,docs")
    assert nombres() == []


def test_protocolo(env, monkeypatch):
    enviados = []
    monkeypatch.setattr(g, "enviar_chat", lambda token, para, texto: enviados.append((token, para, texto)))
    assert servidor.responder({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert servidor.responder({"jsonrpc": "2.0", "id": 1, "method": "initialize"})["result"]["serverInfo"]["name"] == "google-envio"
    ok = servidor.responder({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                             "params": {"name": "enviar_mensaje_chat", "arguments": {"para": "ana@x.pe", "texto": "hola"}}})
    assert ok["result"]["isError"] is False and enviados == [("tok", "ana@x.pe", "hola")]
    vacio = servidor.responder({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "enviar_correo", "arguments": {"para": "a@x.pe"}}})
    assert vacio["result"]["isError"] is True
    no = servidor.responder({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "buscar_archivos"}})
    assert no["error"]["code"] == -32602


def test_proceso_stdio(tmp_path):
    entrada = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\nno-json\n"
    p = subprocess.run([sys.executable, str(servidor.__file__)], input=entrada, capture_output=True, text=True, timeout=30)
    lineas = [json.loads(x) for x in p.stdout.splitlines()]
    assert "tools" in lineas[0]["result"] and lineas[1]["error"]["code"] == -32700
