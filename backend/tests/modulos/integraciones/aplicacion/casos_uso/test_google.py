"""API del MCP de Google Workspace: guardar en el .env sin devolver secretos, autorizar con código y probar cada servicio."""

import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from tests.cliente_web import TestClient

from modulos.integraciones.aplicacion.casos_uso import google as mcp
from modulos.sistema.aplicacion.casos_uso import sesion
from core import entorno
from modulos.integraciones.infraestructura.google import cliente as g

cliente = TestClient()
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))
ID = "123-abc.apps.googleusercontent.com"
VARS = ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REDIRECT_URI", "USER_GOOGLE_EMAIL", "GOOGLE_MCP_SERVICIOS",
        "GOOGLE_OAUTH_REFRESH_TOKEN", "GOOGLE_OAUTH_SCOPES")


@pytest.fixture
def env(tmp_path, monkeypatch):
    ruta = tmp_path / ".env"
    ruta.write_text("RCC_PASSWORD=secreto\n", encoding="utf-8")
    monkeypatch.setattr(entorno, "ENV", ruta)
    for var in VARS:
        monkeypatch.delenv(var, raising=False)
    yield ruta
    for var in VARS:
        os.environ.pop(var, None)


def test_guardar_no_devuelve_secretos_y_arma_el_json(env):
    r = cliente.put("/api/mcp/google", json={"client_id": ID, "client_secret": "GOCSPX-xyz", "servicios": ["chat", "drive"]})
    assert r.status_code == 200 and "GOCSPX" not in r.text
    c = r.json()
    assert c["secreto_configurado"] is True and c["autorizado"] is False
    assert [s["id"] for s in c["servicios"] if s["activo"]] == ["drive", "chat"]
    srv = c["configuracion"]["mcpServers"]
    assert list(srv) == ["gws-drive", "gws-chat", "google-envio"]
    envio = srv["google-envio"]  # el cliente MCP lo lanza tal cual: el Python del entorno y un archivo que existe
    assert envio["command"] == sys.executable and Path(envio["args"][0]).is_file()
    assert srv["gws-chat"] == {"serverUrl": "https://chatmcp.googleapis.com/mcp/v1", "oauth": {"clientId": ID, "clientSecret": mcp.SECRETO}}
    texto = env.read_text(encoding="utf-8")
    assert "GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xyz" in texto and "GOOGLE_MCP_SERVICIOS=drive,chat" in texto and "RCC_PASSWORD=secreto" in texto


@pytest.mark.parametrize("cuerpo,fragmento", [
    ({"client_id": "abc"}, "googleusercontent"),
    ({"cuenta": "no-correo"}, "correo válido"),
    ({"servicios": []}, "al menos un servicio"),
    ({"servicios": ["fax"]}, "fax"),
    ({"redirect_uri": "ftp://x"}, "http"),
])
def test_validaciones(env, cuerpo, fragmento):
    r = cliente.put("/api/mcp/google", json=cuerpo)
    assert r.status_code == 422 and fragmento in r.text


def test_autorizar_y_canjear_codigo_pegado_como_url(env, monkeypatch):
    cliente.put("/api/mcp/google", json={"client_id": ID, "client_secret": "s"})
    r = cliente.post("/api/mcp/google/autorizar", json={"redirect_uri": "http://localhost:3000/configuracion/mcp"}).json()
    q = parse_qs(urlparse(r["url"]).query)
    state = q["state"][0]
    vistos = {}

    def canjear(codigo, redirect, verificador):
        vistos.update(codigo=codigo, redirect=redirect, verificador=verificador)
        return {"refresh_token": "1//refresco", "access_token": "a", "scope": " ".join(g.scopes_de(["gmail"]))}
    monkeypatch.setattr(g, "canjear_codigo", canjear)
    monkeypatch.setattr(g, "correo_de", lambda token: "yo@empresa.pe")
    r = cliente.post("/api/mcp/google/codigo", json={"codigo": f"http://localhost:3000/configuracion/mcp?state={state}&code=4/0Abc&scope=x"})
    assert r.status_code == 200 and "refresco" not in r.text
    c = r.json()
    assert c["autorizado"] is True and c["cuenta"] == "yo@empresa.pe"
    assert vistos["codigo"] == "4/0Abc" and vistos["redirect"].endswith("/configuracion/mcp")
    falta = {s["id"]: s["falta_consentimiento"] for s in c["servicios"] if s["activo"]}
    assert falta == {"drive": True, "gmail": False, "docs": True, "sheets": True, "slides": True, "chat": True}
    assert "GOOGLE_OAUTH_REFRESH_TOKEN=1//refresco" in env.read_text(encoding="utf-8")
    # el mismo state no se puede reutilizar
    assert cliente.post("/api/mcp/google/codigo", json={"codigo": "x", "state": state}).status_code == 422


def test_codigo_solo_usa_la_ultima_autorizacion(env, monkeypatch):
    cliente.put("/api/mcp/google", json={"client_id": ID, "client_secret": "s"})
    cliente.post("/api/mcp/google/autorizar", json={"redirect_uri": "http://localhost:3000/configuracion/mcp"})
    monkeypatch.setattr(g, "canjear_codigo", lambda *a: {"refresh_token": "r", "access_token": "a"})
    monkeypatch.setattr(g, "correo_de", lambda token: "")
    assert cliente.post("/api/mcp/google/codigo", json={"codigo": "4/0Abc"}).json()["autorizado"] is True


def test_autorizar_sin_secreto(env):
    cliente.put("/api/mcp/google", json={"client_id": ID})
    assert cliente.post("/api/mcp/google/autorizar", json={"redirect_uri": "http://x"}).status_code == 422


def test_desconectar_quita_el_token(env, monkeypatch):
    revocados = []
    monkeypatch.setattr(g, "revocar", revocados.append)
    mcp._poner({"GOOGLE_OAUTH_REFRESH_TOKEN": "r", "GOOGLE_OAUTH_SCOPES": "openid"})
    assert cliente.delete("/api/mcp/google/autorizacion").json()["autorizado"] is False
    assert revocados == ["r"] and "REFRESH" not in env.read_text(encoding="utf-8")


def test_probar_mcp_lista_y_ejecuta(env, monkeypatch):
    monkeypatch.setattr(g, "mcp_herramientas", lambda s: [{"name": "search_files", "description": "Busca", "inputSchema": {"type": "object"}}])
    r = cliente.post("/api/mcp/google/drive/herramientas").json()
    assert r["ok"] is True and r["herramientas"][0]["nombre"] == "search_files"
    monkeypatch.setattr(g, "mcp_ejecutar", lambda s, h, a: (True, f"{s}:{h}:{a}"))
    assert cliente.post("/api/mcp/google/drive/ejecutar", json={"herramienta": "search_files", "argumentos": {"q": "x"}}).json()["detalle"] == "drive:search_files:{'q': 'x'}"
    assert cliente.post("/api/mcp/google/drive/ejecutar", json={"herramienta": " "}).status_code == 422
    assert cliente.post("/api/mcp/google/fax/herramientas").status_code == 404
    monkeypatch.setattr(g, "mcp_herramientas", lambda s: (_ for _ in ()).throw(g.GoogleError("401")))
    assert cliente.post("/api/mcp/google/chat/herramientas").json() == {"ok": False, "detalle": "401", "herramientas": []}


def test_enviar_directo(env, monkeypatch):
    llamadas = []
    monkeypatch.setattr(g, "enviar", lambda s, d, t: llamadas.append((s, d, t)) or "ok")
    assert cliente.post("/api/mcp/google/chat/enviar", json={"destinatario": "spaces/AAA", "texto": "hola"}).json() == {"ok": True, "detalle": "ok"}
    assert cliente.post("/api/mcp/google/gmail/enviar", json={"destinatario": "ana@x.pe"}).json()["ok"] is True
    assert llamadas == [("chat", "spaces/AAA", "hola"), ("gmail", "ana@x.pe", "")]
    assert cliente.post("/api/mcp/google/gmail/enviar", json={"destinatario": "spaces/AAA"}).status_code == 422
    assert cliente.post("/api/mcp/google/drive/enviar", json={"destinatario": "ana@x.pe"}).status_code == 422
