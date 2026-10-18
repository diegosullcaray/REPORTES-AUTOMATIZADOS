"""API de las conexiones de IA: se guardan en el .env, la API key nunca vuelve al navegador y la clave guardada solo viaja a su URL."""

import os

import pytest
from tests.cliente_web import TestClient

from core import entorno
from core.excepciones import ErrorIntegracion
from modulos.integraciones.aplicacion.puertos import puertos
from modulos.sistema.aplicacion.casos_uso import sesion

cliente = TestClient()
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))
OPENAI = {"nombre": "OpenAI prod", "api_url": "https://api.openai.com/v1/", "api_key": "sk-secreta", "modelo": "gpt-x"}


@pytest.fixture
def env(tmp_path, monkeypatch):
    ruta = tmp_path / ".env"
    ruta.write_text("RCC_PASSWORD=secreto\n", encoding="utf-8")
    monkeypatch.setattr(entorno, "ENV", ruta)
    antes = {k for k in os.environ if k.startswith("IA_")}
    yield ruta
    for k in [k for k in os.environ if k.startswith("IA_") and k not in antes]:
        os.environ.pop(k)


@pytest.fixture
def proveedor(monkeypatch):
    visto = []

    def modelos(url, clave):
        visto.append((url, clave))
        if clave == "mala":
            raise ErrorIntegracion("El proveedor respondió 401")
        return ["m1", "m2"]
    monkeypatch.setattr(puertos().ia, "modelos", modelos)
    return visto


def test_crear_guarda_en_el_env_y_no_devuelve_la_clave(env):
    r = cliente.post("/api/ia", json=OPENAI)
    assert r.status_code == 201 and "sk-secreta" not in r.text
    c = r.json()
    assert c["id"] == "openai-prod" and c["proveedor"] == "openai" and c["clave_configurada"] is True and c["api_url"] == "https://api.openai.com/v1"
    texto = env.read_text(encoding="utf-8")
    assert "IA_OPENAI_PROD_CLAVE=sk-secreta" in texto and "IA_CONFIGS=openai-prod" in texto and "RCC_PASSWORD=secreto" in texto
    assert "sk-secreta" not in cliente.get("/api/ia").text


def test_mismo_nombre_obtiene_otro_id(env):
    cliente.post("/api/ia", json=OPENAI)
    assert cliente.post("/api/ia", json=OPENAI).json()["id"] == "openai-prod-2"
    assert [x["id"] for x in cliente.get("/api/ia").json()] == ["openai-prod", "openai-prod-2"]


def test_actualizar_conserva_la_clave_si_viene_vacia(env):
    cliente.post("/api/ia", json=OPENAI)
    r = cliente.put("/api/ia/openai-prod", json={"modelo": "gpt-y", "api_key": "", "activo": False})
    assert r.status_code == 200 and r.json()["modelo"] == "gpt-y" and r.json()["activo"] is False
    assert "IA_OPENAI_PROD_CLAVE=sk-secreta" in env.read_text(encoding="utf-8")
    cliente.put("/api/ia/openai-prod", json={"api_key": "sk-nueva"})
    assert "IA_OPENAI_PROD_CLAVE=sk-nueva" in env.read_text(encoding="utf-8")


def test_eliminar_quita_todas_sus_variables(env):
    cliente.post("/api/ia", json=OPENAI)
    assert cliente.delete("/api/ia/openai-prod").status_code == 200
    assert "IA_" not in env.read_text(encoding="utf-8") and cliente.get("/api/ia").json() == []
    assert cliente.delete("/api/ia/openai-prod").status_code == 404


@pytest.mark.parametrize("cambio,frag", [
    ({"nombre": "  "}, "Nombre"), ({"api_url": "ftp://x"}, "http"), ({"api_key": "con espacio"}, "API key"),
    ({"modelo": "a#b"}, "Modelo"), ({"nombre": "a\nb"}, "Nombre"),
])
def test_validaciones(env, cambio, frag):
    r = cliente.post("/api/ia", json={**OPENAI, **cambio})
    assert r.status_code == 422 and frag in r.text
    assert "IA_" not in env.read_text(encoding="utf-8")


def test_modelos_con_clave_escrita_y_con_la_guardada(env, proveedor):
    assert cliente.post("/api/ia/modelos", json={"api_url": "https://api.openai.com/v1", "api_key": "sk-1"}).json() == {"proveedor": "openai", "modelos": ["m1", "m2"]}
    cliente.post("/api/ia", json=OPENAI)
    cliente.post("/api/ia/modelos", json={"api_url": "https://api.openai.com/v1", "id": "openai-prod"})
    assert proveedor[-1] == ("https://api.openai.com/v1", "sk-secreta")


def test_la_clave_guardada_no_viaja_a_otra_url(env, proveedor):
    cliente.post("/api/ia", json=OPENAI)
    r = cliente.post("/api/ia/modelos", json={"api_url": "https://otro.sitio/v1", "id": "openai-prod"})
    assert r.status_code == 422 and "API key" in r.text and proveedor == []


def test_probar_ok_y_error_del_proveedor(env, proveedor):
    cliente.post("/api/ia", json=OPENAI)
    assert cliente.post("/api/ia/openai-prod/probar").json()["modelos"] == ["m1", "m2"]
    cliente.post("/api/ia", json={**OPENAI, "nombre": "Mala", "api_key": "mala"})
    r = cliente.post("/api/ia/mala/probar")
    assert r.status_code == 422 and "401" in r.text
    assert cliente.post("/api/ia/nada/probar").status_code == 404
