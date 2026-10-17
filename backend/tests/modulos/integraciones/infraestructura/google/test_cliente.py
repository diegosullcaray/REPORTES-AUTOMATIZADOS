"""Cliente de Google Workspace (infraestructura/google/cliente.py): scopes, OAuth, cliente MCP por HTTP y envío por Gmail y Chat, sin red."""

import base64
import io
import json
from urllib.parse import parse_qs, urlparse

import pytest

from modulos.integraciones.infraestructura.google import cliente as g

ID = "123-abc.apps.googleusercontent.com"


@pytest.fixture
def env(monkeypatch):
    for var in ("GOOGLE_MCP_SERVICIOS", "GOOGLE_OAUTH_SCOPES", "USER_GOOGLE_EMAIL"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", ID)
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "secreto")
    monkeypatch.setenv("GOOGLE_OAUTH_REFRESH_TOKEN", "refresco")


@pytest.fixture
def http(monkeypatch):
    """Registra las llamadas a las APIs REST y responde según la URL."""
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


class Resp:
    def __init__(self, cuerpo: str, tipo="application/json", sesion=None):
        self._c, self.headers = cuerpo.encode(), {"Content-Type": tipo, **({"Mcp-Session-Id": sesion} if sesion else {})}

    def read(self):
        return self._c

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_servidores_oficiales_y_scopes(env, monkeypatch):
    assert g.servicios_activos() == ["drive", "gmail", "docs", "sheets", "slides", "chat"]
    assert g.SERVICIOS["chat"].url == "https://chatmcp.googleapis.com/mcp/v1"
    monkeypatch.setenv("GOOGLE_MCP_SERVICIOS", "chat, nada ,docs")
    assert g.servicios_activos() == ["chat", "docs"]
    scopes = g.scopes_de(["docs", "sheets"])
    assert scopes[:2] == ["openid", "email"] and len(scopes) == len(set(scopes)) and g.G + "drive.file" in scopes


def test_falta_consentimiento(env, monkeypatch):
    monkeypatch.setenv("GOOGLE_OAUTH_SCOPES", " ".join(g.SERVICIOS["drive"].scopes))
    assert not g.falta_consentimiento("drive") and g.falta_consentimiento("docs")


def test_url_de_autorizacion_pide_refresh_y_pkce(env, monkeypatch):
    monkeypatch.setenv("USER_GOOGLE_EMAIL", "yo@empresa.pe")
    q = parse_qs(urlparse(g.url_autorizacion("http://localhost:3000/configuracion/mcp", "S", "D", ["gmail"])).query)
    assert q["client_id"] == [ID] and q["access_type"] == ["offline"] and q["prompt"] == ["consent"]
    assert q["code_challenge"] == ["D"] and q["state"] == ["S"] and q["login_hint"] == ["yo@empresa.pe"]
    assert g.G + "gmail.send" in q["scope"][0]


def test_canjear_exige_refresh_token(env, http):
    http[1]["oauth2.googleapis.com/token"] = {"access_token": "a"}
    with pytest.raises(g.GoogleError, match="refresh token"):
        g.canjear_codigo("c", "http://x", "v")


def test_sin_autorizar_explica_que_hacer(env, monkeypatch):
    monkeypatch.delenv("GOOGLE_OAUTH_REFRESH_TOKEN")
    with pytest.raises(g.GoogleError, match="Autorizar"):
        g.token_de_acceso()


def test_gmail_envia_mime_en_base64(env, http):
    g.enviar_correo("tok", "ana@empresa.pe", "Hola", "Cuerpo")
    metodo, url, datos, _, token = http[0][-1]
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


def test_enviar_valida_destino(env, http):
    http[1]["oauth2.googleapis.com/token"] = {"access_token": "tok"}
    http[1]["findDirectMessage"] = {"name": "spaces/DM"}
    assert "Chat" in g.enviar("chat", "ana@x.pe", "")
    assert "Gmail" in g.enviar("gmail", "ana@x.pe", "hola")
    with pytest.raises(g.GoogleError):
        g.enviar("chat", "", "hola")
    with pytest.raises(g.GoogleError):
        g.enviar("drive", "ana@x.pe", "hola")


def test_cliente_mcp_sesion_sse_y_herramientas(env, monkeypatch):
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    vistos = []

    def urlopen(req, timeout):
        cuerpo = json.loads(req.data)
        vistos.append((req.full_url, cuerpo.get("method"), req.get_header("Mcp-session-id"), req.get_header("Authorization")))
        if cuerpo["method"] == "initialize":
            return Resp(json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}), sesion="S1")
        if cuerpo["method"] == "notifications/initialized":
            return Resp("")
        if cuerpo["method"] == "tools/list":
            return Resp('event: message\ndata: {"jsonrpc":"2.0","id":%d,"result":{"tools":[{"name":"search_threads","description":"Busca"}]}}\n\n' % cuerpo["id"],
                        tipo="text/event-stream")
        return Resp(json.dumps({"jsonrpc": "2.0", "id": cuerpo["id"], "result": {"content": [{"type": "text", "text": "3 hilos"}]}}))
    monkeypatch.setattr(g.urllib.request, "urlopen", urlopen)
    assert [h["name"] for h in g.mcp_herramientas("gmail")] == ["search_threads"]
    assert vistos[0][0] == "https://gmailmcp.googleapis.com/mcp/v1" and vistos[0][3] == "Bearer tok"
    assert [v[1] for v in vistos] == ["initialize", "notifications/initialized", "tools/list"] and vistos[2][2] == "S1"
    assert g.mcp_ejecutar("gmail", "search_threads", {"query": "x"}) == (True, "3 hilos")


def test_cliente_mcp_error_jsonrpc(env, monkeypatch):
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    monkeypatch.setattr(g.urllib.request, "urlopen", lambda req, timeout: Resp(json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"message": "no"}})))
    with pytest.raises(g.GoogleError, match="MCP: no"):
        g.mcp_herramientas("drive")


def test_mensaje_de_error_de_google(env):
    import urllib.error
    exc = urllib.error.HTTPError("u", 403, "x", {}, io.BytesIO(json.dumps({"error": {"message": "Chat app not found"}}).encode()))
    assert g._mensaje_error(exc) == "Google respondió 403: Chat app not found"


def test_chat_con_adjunto_sube_y_lo_referencia(env, http, monkeypatch, tmp_path):
    llamadas, respuestas = http
    respuestas["findDirectMessage"] = {"name": "spaces/DM"}
    archivo = tmp_path / "inserts.txt"
    archivo.write_text("INSERT;", encoding="utf-8")
    subidas = []

    def urlopen(req, timeout):
        subidas.append((req.full_url, req.get_header("Content-type"), req.data))
        return Resp(json.dumps({"attachmentDataRef": {"resourceName": "R", "attachmentUploadToken": "T"}}))
    monkeypatch.setattr(g.urllib.request, "urlopen", urlopen)
    g.enviar_chat("tok", "oscar@x.pe", "hola", [archivo])
    url, tipo, cuerpo = subidas[0]
    assert url == "https://chat.googleapis.com/upload/v1/spaces/DM/attachments:upload?uploadType=multipart"
    assert tipo.startswith("multipart/related; boundary=") and b'"filename": "inserts.txt"' in cuerpo and b"INSERT;" in cuerpo
    assert llamadas[-1][2] == {"text": "hola", "attachment": [{"attachmentDataRef": {"resourceName": "R", "attachmentUploadToken": "T"}}]}
