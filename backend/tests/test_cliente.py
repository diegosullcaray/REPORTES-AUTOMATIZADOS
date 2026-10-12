"""Cliente de Google Workspace (mcp_google/cliente.py): scopes por servicio, OAuth y llamadas a Gmail y Chat sin red."""

import base64
import json
from urllib.parse import parse_qs, urlparse

import pytest

from mcp_google import cliente as g

ID = "123-abc.apps.googleusercontent.com"


@pytest.fixture
def env(monkeypatch):
    for var in ("GOOGLE_MCP_SERVICIOS", "GOOGLE_MCP_SOLO_LECTURA", "GOOGLE_OAUTH_SCOPES", "USER_GOOGLE_EMAIL"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", ID)
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "secreto")
    monkeypatch.setenv("GOOGLE_OAUTH_REFRESH_TOKEN", "refresco")


@pytest.fixture
def http(monkeypatch):
    """Registra las llamadas y responde según la URL."""
    llamadas, respuestas = [], {}

    def falso(metodo, url, *, datos=None, form=None, token=None):
        llamadas.append((metodo, url, datos, form, token))
        for clave, r in respuestas.items():
            if clave in url:
                if isinstance(r, Exception):
                    raise r
                return r
        return {}
    monkeypatch.setattr(g, "_http", falso)
    return llamadas, respuestas


def test_servicios_por_defecto_y_scopes(env, monkeypatch):
    assert g.servicios_activos() == ["gmail", "chat", "contacts"]
    monkeypatch.setenv("GOOGLE_MCP_SERVICIOS", "chat, nada ,drive")
    assert g.servicios_activos() == ["chat", "drive"]
    scopes = g.scopes_de(["chat", "drive"])
    assert scopes[:2] == ["openid", "email"] and g.G + "chat.messages.create" in scopes and len(scopes) == len(set(scopes))


def test_falta_consentimiento(env, monkeypatch):
    monkeypatch.setenv("GOOGLE_OAUTH_SCOPES", " ".join(g.SERVICIOS["gmail"].scopes))
    assert not g.falta_consentimiento("gmail") and g.falta_consentimiento("chat")


def test_url_de_autorizacion_pide_refresh_y_pkce(env, monkeypatch):
    monkeypatch.setenv("USER_GOOGLE_EMAIL", "yo@empresa.pe")
    q = parse_qs(urlparse(g.url_autorizacion("http://localhost:3000/configuracion/mcp", "S", "D", ["gmail"])).query)
    assert q["client_id"] == [ID] and q["access_type"] == ["offline"] and q["prompt"] == ["consent"]
    assert q["code_challenge"] == ["D"] and q["state"] == ["S"] and q["login_hint"] == ["yo@empresa.pe"]
    assert g.G + "gmail.send" in q["scope"][0]


def test_canjear_exige_refresh_token(env, http):
    _, respuestas = http
    respuestas["oauth2.googleapis.com/token"] = {"access_token": "a"}
    with pytest.raises(g.GoogleError, match="refresh token"):
        g.canjear_codigo("c", "http://x", "v")


def test_sin_autorizar_explica_que_hacer(env, monkeypatch):
    monkeypatch.delenv("GOOGLE_OAUTH_REFRESH_TOKEN")
    with pytest.raises(g.GoogleError, match="Autorizar"):
        g.token_de_acceso()


def test_gmail_envia_mime_en_base64(env, http):
    llamadas, _ = http
    g.enviar_correo("tok", "ana@empresa.pe", "Hola", "Cuerpo")
    metodo, url, datos, _, token = llamadas[-1]
    assert metodo == "POST" and url.endswith("/messages/send") and token == "tok"
    mime = base64.urlsafe_b64decode(datos["raw"]).decode()
    assert "To: ana@empresa.pe" in mime and "Subject: Hola" in mime


def test_chat_directo_busca_o_crea_el_espacio(env, http):
    llamadas, respuestas = http
    respuestas["findDirectMessage"] = g.GoogleError("Google respondió 404: not found")
    respuestas["spaces:setup"] = {"name": "spaces/NUEVO"}
    g.enviar_chat("tok", "ana@empresa.pe", "hola")
    assert [u.split("/v1/")[1].split("?")[0] for _, u, *_ in llamadas] == ["spaces:findDirectMessage", "spaces:setup", "spaces/NUEVO/messages"]
    assert llamadas[-1][2] == {"text": "hola"}


def test_chat_a_un_espacio_va_directo(env, http):
    llamadas, _ = http
    g.enviar_chat("tok", "spaces/AAA", "hola")
    assert len(llamadas) == 1 and llamadas[0][1].endswith("spaces/AAA/messages")


def test_probar_cada_servicio(env, http):
    _, respuestas = http
    respuestas["oauth2.googleapis.com/token"] = {"access_token": "tok"}
    respuestas["findDirectMessage"] = {"name": "spaces/DM"}
    respuestas["calendar/v3"] = {"items": [{"summary": "Comité", "start": {"date": "2026-10-13"}}]}
    respuestas["drive/v3"] = {"files": [{"name": "Cartera"}]}
    respuestas["tasks/v1"] = {"items": [{"id": "1", "title": "Pendientes"}]}
    respuestas["searchContacts"] = {"results": [{"person": {"names": [{"displayName": "Ana"}], "emailAddresses": [{"value": "ana@x.pe"}]}}]}
    assert "Gmail" in g.probar("gmail", "ana@x.pe")
    assert "Chat" in g.probar("chat", "ana@x.pe")
    assert "Ana" in g.probar("contacts", "Ana")
    assert "Comité" in g.probar("calendar")
    assert "Pendientes" in g.probar("tasks")
    for s in ("drive", "docs", "sheets", "slides", "forms"):
        assert "Cartera" in g.probar(s)
    with pytest.raises(g.GoogleError, match="correo"):
        g.probar("gmail")


def test_mensaje_de_error_de_google(env):
    import io
    import urllib.error
    exc = urllib.error.HTTPError("u", 403, "x", {}, io.BytesIO(json.dumps({"error": {"message": "Chat app not found"}}).encode()))
    assert g._mensaje_error(exc) == "Google respondió 403: Chat app not found"
