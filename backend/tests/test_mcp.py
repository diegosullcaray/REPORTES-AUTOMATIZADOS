"""API del MCP de Google Workspace: guardar en el .env sin devolver secretos, autorizar con código y probar cada servicio."""

import os
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from api import mcp, servicios, sesion
from api.app import app
from mcp_google import cliente as g

cliente = TestClient(app)
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))
ID = "123-abc.apps.googleusercontent.com"
VARS = ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REDIRECT_URI", "USER_GOOGLE_EMAIL", "GOOGLE_MCP_SERVICIOS",
        "GOOGLE_MCP_SOLO_LECTURA", "GOOGLE_MCP_NIVEL", "GOOGLE_OAUTH_REFRESH_TOKEN", "GOOGLE_OAUTH_SCOPES")


@pytest.fixture
def env(tmp_path, monkeypatch):
    ruta = tmp_path / ".env"
    ruta.write_text("RCC_PASSWORD=secreto\n", encoding="utf-8")
    monkeypatch.setattr(servicios, "ENV", ruta)
    for var in VARS:
        monkeypatch.delenv(var, raising=False)
    yield ruta
    for var in VARS:
        os.environ.pop(var, None)


def test_guardar_no_devuelve_secretos(env):
    r = cliente.put("/api/mcp/google", json={"client_id": ID, "client_secret": "GOCSPX-xyz", "servicios": ["chat", "gmail", "tasks"], "solo_lectura": True})
    assert r.status_code == 200 and "GOCSPX" not in r.text
    c = r.json()
    assert c["secreto_configurado"] is True and c["autorizado"] is False and c["solo_lectura"] is True
    assert [s["id"] for s in c["servicios"] if s["activo"]] == ["gmail", "chat", "tasks"]
    assert "--read-only" in c["configuracion_workspace_mcp"]["mcpServers"]["google_workspace"]["args"]
    texto = env.read_text(encoding="utf-8")
    assert "GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xyz" in texto and "GOOGLE_MCP_SERVICIOS=gmail,chat,tasks" in texto and "RCC_PASSWORD=secreto" in texto


@pytest.mark.parametrize("cuerpo,fragmento", [
    ({"client_id": "abc"}, "googleusercontent"),
    ({"cuenta": "no-correo"}, "correo válido"),
    ({"servicios": []}, "al menos un servicio"),
    ({"servicios": ["fax"]}, "fax"),
    ({"nivel": "todo"}, "core"),
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
    assert falta == {"gmail": False, "chat": True, "contacts": True}
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


def test_probar_servicio(env, monkeypatch):
    llamadas = []
    monkeypatch.setattr(g, "probar", lambda s, d, t: llamadas.append((s, d, t)) or "ok")
    assert cliente.post("/api/mcp/google/chat/prueba", json={"destinatario": "ana@x.pe", "texto": "hola"}).json() == {"ok": True, "detalle": "ok"}
    assert llamadas == [("chat", "ana@x.pe", "hola")]
    assert cliente.post("/api/mcp/google/chat/prueba", json={"destinatario": "ana"}).status_code == 422
    assert cliente.post("/api/mcp/google/fax/prueba", json={}).status_code == 404
    monkeypatch.setattr(g, "probar", lambda *a: (_ for _ in ()).throw(g.GoogleError("sin permiso")))
    assert cliente.post("/api/mcp/google/drive/prueba", json={}).json() == {"ok": False, "detalle": "sin permiso"}
