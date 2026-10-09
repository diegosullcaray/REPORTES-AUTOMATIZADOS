"""Inicio de sesión con la cuenta de Windows y cookie firmada (la validación de Windows se parchea)."""

from fastapi.testclient import TestClient

from api import sesion
from api.app import app


def test_login_correcto_entrega_cookie_y_clave_mala_no(monkeypatch):
    monkeypatch.setenv("USUARIOS_WEB", "ana")
    monkeypatch.setattr(sesion, "clave_valida_en_windows", lambda u, c: c == "buena")
    nuevo = TestClient(app)
    assert nuevo.post("/api/sesion", json={"usuario": "DOM\\Ana", "clave": "mala"}).status_code == 401
    assert nuevo.post("/api/sesion", json={"usuario": "DOM\\Ana", "clave": "buena"}).json() == {"usuario": "ana"}
    assert nuevo.get("/api/reportes").status_code == 200
    assert nuevo.delete("/api/sesion").status_code == 204
    assert nuevo.get("/api/sesion").status_code == 401


def test_usuario_fuera_de_la_lista_no_entra(monkeypatch):
    monkeypatch.setenv("USUARIOS_WEB", "ana")
    monkeypatch.setattr(sesion, "clave_valida_en_windows", lambda u, c: True)
    assert TestClient(app).post("/api/sesion", json={"usuario": "luis", "clave": "x"}).status_code == 401


def test_cookie_alterada_o_vencida_se_rechaza(monkeypatch):
    token = sesion.emitir("ana")
    assert sesion.leer(token) == "ana" and sesion.leer(token[:-1] + "0") is None and sesion.leer("basura") is None
    monkeypatch.setattr(sesion, "DURACION", -1)
    assert sesion.leer(sesion.emitir("ana")) is None


def test_cinco_fallos_bloquean_al_usuario(monkeypatch):
    monkeypatch.setenv("USUARIOS_WEB", "bloqueado")
    monkeypatch.setattr(sesion, "clave_valida_en_windows", lambda u, c: False)
    nuevo = TestClient(app)
    codigos = [nuevo.post("/api/sesion", json={"usuario": "bloqueado", "clave": "x"}).status_code for _ in range(6)]
    assert codigos == [401] * 5 + [429]
