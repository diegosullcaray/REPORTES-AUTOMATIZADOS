"""API de MCP: catálogo y envío de mensajes a Google Chat sin exponer el webhook."""

import pytest
from fastapi.testclient import TestClient

from api import sesion
from api.app import app
from reportes.comun import correo

cliente = TestClient(app)
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))
WEBHOOK = "https://chat.googleapis.com/v1/spaces/AAA/messages?key=K&token=T"


@pytest.fixture
def enviados(monkeypatch):
    salida = []
    monkeypatch.setattr(correo, "notificar_chat", lambda url, texto: salida.append((url, texto)))
    return salida


def test_catalogo_no_expone_el_webhook(monkeypatch):
    monkeypatch.setenv("GOOGLE_CHAT_WEBHOOK_URL", WEBHOOK)
    r = cliente.get("/api/mcp")
    assert r.status_code == 200 and "AAA" not in r.text
    s = r.json()[0]
    assert s["id"] == "google-chat" and s["webhook_configurado"] is True
    assert [h["nombre"] for h in s["herramientas"]] == ["enviar_mensaje_chat"]
    assert s["configuracion"]["mcpServers"]["google-chat"]["args"] == s["args"]


def test_mensaje_desde_la_web(monkeypatch, enviados):
    monkeypatch.setenv("GOOGLE_CHAT_WEBHOOK_URL", WEBHOOK)
    r = cliente.post("/api/mcp/google-chat/mensaje", json={"texto": "  hola  "})
    assert r.json()["ok"] is True and enviados == [(WEBHOOK, "hola")]


def test_mensaje_sin_webhook_o_vacio(monkeypatch, enviados):
    monkeypatch.delenv("GOOGLE_CHAT_WEBHOOK_URL", raising=False)
    assert cliente.post("/api/mcp/google-chat/mensaje", json={"texto": "hola"}).json()["ok"] is False
    assert cliente.post("/api/mcp/google-chat/mensaje", json={"texto": "  "}).status_code == 422
    assert cliente.post("/api/mcp/otro/mensaje", json={"texto": "hola"}).status_code == 404
    assert enviados == []
