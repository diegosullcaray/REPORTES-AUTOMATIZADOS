"""Inicio de sesión con usuario y clave del .env y cookie firmada."""

import pytest
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


# ---- perfil: cambiar usuario y contraseña (pide la contraseña actual)
def _sesion_de(monkeypatch, tmp_path, usuario="ana", clave="buena-clave"):
    from api import servicios

    ruta = tmp_path / ".env"
    ruta.write_text(f"RCC_PASSWORD=secreto\nWEB_USUARIO={usuario}\nWEB_CLAVE={clave}\n", encoding="utf-8")
    monkeypatch.setattr(servicios, "ENV", ruta)
    monkeypatch.setenv("WEB_USUARIO", usuario)
    monkeypatch.setenv("WEB_CLAVE", clave)
    c = TestClient(app)
    assert c.post("/api/sesion", json={"usuario": usuario, "clave": clave}).status_code == 200
    return c, ruta


def test_cambiar_usuario_y_clave_actualiza_env_y_sesion(monkeypatch, tmp_path):
    c, ruta = _sesion_de(monkeypatch, tmp_path)
    r = c.put("/api/cuenta", json={"clave_actual": "buena-clave", "usuario": "luis", "clave_nueva": "otra-clave-9"})
    assert r.status_code == 200 and r.json() == {"usuario": "luis"}
    texto = ruta.read_text(encoding="utf-8")
    assert "WEB_USUARIO=luis" in texto and "WEB_CLAVE=otra-clave-9" in texto and "RCC_PASSWORD=secreto" in texto
    assert c.get("/api/sesion").json() == {"usuario": "luis"}                      # la cookie se reemitió con el nombre nuevo
    assert TestClient(app).post("/api/sesion", json={"usuario": "ana", "clave": "buena-clave"}).status_code == 401
    assert TestClient(app).post("/api/sesion", json={"usuario": "luis", "clave": "otra-clave-9"}).status_code == 200


def test_cambiar_cuenta_exige_la_clave_actual(monkeypatch, tmp_path):
    c, ruta = _sesion_de(monkeypatch, tmp_path, usuario="solo-clave-actual")
    antes = ruta.read_text(encoding="utf-8")
    r = c.put("/api/cuenta", json={"clave_actual": "equivocada", "clave_nueva": "otra-clave-9"})
    assert r.status_code == 422 and "no es correcta" in r.json()["detail"]
    assert ruta.read_text(encoding="utf-8") == antes


@pytest.mark.parametrize("cuerpo,fragmento", [
    ({"clave_nueva": "corta"}, "8 caracteres"),
    ({"clave_nueva": "tiene#almohadilla1"}, "no admite"),
    ({"usuario": "con espacio"}, "no admite espacios"),
    ({}, "ningún cambio"),
])
def test_cuenta_rechaza_valores_invalidos(monkeypatch, tmp_path, cuerpo, fragmento):
    c, ruta = _sesion_de(monkeypatch, tmp_path, usuario="validador")
    antes = ruta.read_text(encoding="utf-8")
    r = c.put("/api/cuenta", json={"clave_actual": "buena-clave", **cuerpo})
    assert r.status_code == 422 and fragmento in r.json()["detail"]
    assert ruta.read_text(encoding="utf-8") == antes
