"""Inicio de sesión con usuario y clave del .env y cookie firmada."""

from fastapi.testclient import TestClient

from api import sesion
from api.app import app


def test_login_correcto_entrega_cookie_y_clave_mala_no(monkeypatch):
    monkeypatch.setenv("WEB_USUARIO", "ana")
    monkeypatch.setenv("WEB_CLAVE", "buena")
    nuevo = TestClient(app)
    assert nuevo.post("/api/sesion", json={"usuario": "Ana", "clave": "mala"}).status_code == 401
    assert nuevo.post("/api/sesion", json={"usuario": "Ana", "clave": "buena"}).json() == {"usuario": "ana"}
    assert nuevo.get("/api/reportes").status_code == 200
    assert nuevo.delete("/api/sesion").status_code == 204
    assert nuevo.get("/api/sesion").status_code == 401


def test_usuario_fuera_de_la_lista_no_entra(monkeypatch):
    monkeypatch.setenv("WEB_USUARIO", "ana")
    monkeypatch.setenv("WEB_CLAVE", "buena")
    assert TestClient(app).post("/api/sesion", json={"usuario": "luis", "clave": "buena"}).status_code == 401


def test_cookie_alterada_o_vencida_se_rechaza(monkeypatch):
    token = sesion.emitir("ana")
    assert sesion.leer(token) == "ana" and sesion.leer(token[:-1] + "0") is None and sesion.leer("basura") is None
    monkeypatch.setattr(sesion, "DURACION", -1)
    assert sesion.leer(sesion.emitir("ana")) is None


def test_cinco_fallos_bloquean_al_usuario(monkeypatch):
    monkeypatch.setenv("WEB_USUARIO", "bloqueado")
    monkeypatch.setenv("WEB_CLAVE", "buena")
    nuevo = TestClient(app)
    codigos = [nuevo.post("/api/sesion", json={"usuario": "bloqueado", "clave": "x"}).status_code for _ in range(6)]
    assert codigos == [401] * 5 + [429]


def test_sin_credenciales_en_el_env_no_entra_nadie(monkeypatch):
    monkeypatch.delenv("WEB_USUARIO", raising=False)
    monkeypatch.delenv("WEB_CLAVE", raising=False)
    assert TestClient(app).post("/api/sesion", json={"usuario": "", "clave": "x"}).status_code == 422
    assert TestClient(app).post("/api/sesion", json={"usuario": "a", "clave": "x"}).status_code == 401
