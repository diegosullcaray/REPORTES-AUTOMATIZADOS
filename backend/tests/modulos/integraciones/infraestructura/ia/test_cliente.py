"""Proveedores de IA: se deduce del URL y se listan los modelos con la cabecera que pide cada uno (sin red real)."""

import io
import json
import urllib.error

import pytest

from core.excepciones import ErrorIntegracion
from modulos.integraciones.infraestructura.ia import cliente as c


@pytest.mark.parametrize("url,esperado", [
    ("https://api.openai.com/v1", "openai"), ("https://api.anthropic.com/v1", "anthropic"), ("http://localhost:11434", "ollama"),
    ("https://generativelanguage.googleapis.com/v1beta/openai", "gemini"), ("https://openrouter.ai/api/v1", "openrouter"), ("https://mi.servidor/v1", "custom"),
])
def test_proveedor_de(url, esperado):
    assert c.proveedor_de(url) == esperado


def _falso(monkeypatch, cuerpo, capturado):
    def urlopen(req, timeout):
        capturado.update(url=req.full_url, cab={k.lower(): v for k, v in req.header_items()})
        return io.BytesIO(json.dumps(cuerpo).encode())
    monkeypatch.setattr(c.urllib.request, "urlopen", urlopen)


def test_openai_usa_bearer_y_lee_data(monkeypatch):
    visto = {}
    _falso(monkeypatch, {"data": [{"id": "gpt-b"}, {"id": "gpt-a"}]}, visto)
    assert c.modelos("https://api.openai.com/v1/", "sk-1") == ["gpt-a", "gpt-b"]
    assert visto["url"] == "https://api.openai.com/v1/models" and visto["cab"]["authorization"] == "Bearer sk-1"


def test_anthropic_usa_x_api_key(monkeypatch):
    visto = {}
    _falso(monkeypatch, {"data": [{"id": "claude-x"}]}, visto)
    assert c.modelos("https://api.anthropic.com/v1", "k") == ["claude-x"]
    assert visto["cab"]["x-api-key"] == "k" and "authorization" not in visto["cab"]


def test_ollama_sin_clave_lee_models_name(monkeypatch):
    visto = {}
    _falso(monkeypatch, {"models": [{"name": "llama3"}]}, visto)
    assert c.modelos("http://localhost:11434", "") == ["llama3"] and visto["url"].endswith("/api/tags")


def test_proveedor_con_lista_fija_no_sale_a_la_red(monkeypatch):
    monkeypatch.setattr(c.urllib.request, "urlopen", lambda *a, **k: pytest.fail("no debía conectar"))
    assert "sonar" in c.modelos("https://api.perplexity.ai", "k")


def test_sin_clave_en_proveedor_que_la_exige():
    with pytest.raises(ErrorIntegracion, match="API key"):
        c.modelos("https://api.openai.com/v1", "")


def test_error_http_se_traduce(monkeypatch):
    def urlopen(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 401, "no", {}, None)
    monkeypatch.setattr(c.urllib.request, "urlopen", urlopen)
    with pytest.raises(ErrorIntegracion, match="401"):
        c.modelos("https://api.openai.com/v1", "mala")
