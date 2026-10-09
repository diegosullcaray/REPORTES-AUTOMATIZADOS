"""Correo y Google Chat desde la web: validación, secretos de solo escritura y pruebas que nunca van a la lista."""

import os

import pytest
from fastapi.testclient import TestClient

from api import servicios, sesion
from api.app import app
from reportes.comun import correo

cliente = TestClient(app)
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))
WEBHOOK = "https://chat.googleapis.com/v1/spaces/AAA/messages?key=K&token=T"


@pytest.fixture
def env(tmp_path, monkeypatch):
    ruta = tmp_path / ".env"
    ruta.write_text("RCC_PASSWORD=secreto\n", encoding="utf-8")
    monkeypatch.setattr(servicios, "ENV", ruta)
    for var in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "MAIL_FROM_NAME", "CORREO_PRUEBA", "GOOGLE_CHAT_WEBHOOK_URL"):
        monkeypatch.delenv(var, raising=False)
    return ruta


def test_guardar_escribe_en_el_env_y_no_devuelve_secretos(env):
    r = cliente.put("/api/notificaciones", json={"smtp_user": "mis@confianza.pe", "smtp_clave": "abcd efgh ijkl mnop", "webhook": WEBHOOK, "smtp_port": "587"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["smtp_user"] == "mis@confianza.pe" and cuerpo["smtp_port"] == 587
    assert cuerpo["clave_configurada"] is True and cuerpo["webhook_configurado"] is True
    assert "abcd" not in r.text and "AAA" not in r.text            # ni la clave ni el webhook salen en la respuesta
    texto = env.read_text(encoding="utf-8")
    assert "SMTP_PASSWORD=abcd efgh ijkl mnop" in texto and "RCC_PASSWORD=secreto" in texto
    assert os.environ["SMTP_USER"] == "mis@confianza.pe"            # rige de inmediato, también para las ejecuciones
    assert "abcd" not in cliente.get("/api/notificaciones").text


def test_texto_vacio_quita_la_variable(env):
    cliente.put("/api/notificaciones", json={"webhook": WEBHOOK})
    r = cliente.put("/api/notificaciones", json={"webhook": ""})
    assert r.json()["webhook_configurado"] is False and "GOOGLE_CHAT_WEBHOOK_URL" not in env.read_text(encoding="utf-8")


@pytest.mark.parametrize("cuerpo,fragmento", [
    ({"smtp_host": "smtp gmail com"}, "nombre del servidor"),
    ({"smtp_port": "70000"}, "puerto"),
    ({"smtp_user": "no-es-correo"}, "correo válido"),
    ({"correo_prueba": "x@"}, "correo válido"),
    ({"webhook": "https://otro-sitio.com/hook"}, "Google Chat"),
    ({"smtp_clave": "clave\nOTRA=1"}, "saltos de línea"),
    ({}, "ningún ajuste"),
])
def test_valores_invalidos_se_rechazan_sin_escribir(env, cuerpo, fragmento):
    antes = env.read_text(encoding="utf-8")
    r = cliente.put("/api/notificaciones", json=cuerpo)
    assert r.status_code == 422 and fragmento in r.json()["detail"]
    assert env.read_text(encoding="utf-8") == antes


def test_la_prueba_de_correo_solo_va_a_correo_prueba(env, monkeypatch):
    monkeypatch.setenv("SMTP_USER", "mis@confianza.pe")
    monkeypatch.setenv("SMTP_PASSWORD", "x")
    monkeypatch.setenv("CORREO_PRUEBA", "yo@confianza.pe")
    enviados = []
    monkeypatch.setattr(correo, "enviar", lambda cfg, msg, destinatarios: enviados.append(destinatarios))
    r = cliente.post("/api/notificaciones/correo/prueba").json()
    assert r["ok"] is True and enviados == [["yo@confianza.pe"]]


def test_prueba_sin_configurar_informa_el_motivo_sin_romper(env):
    r = cliente.post("/api/notificaciones/correo/prueba")
    assert r.status_code == 200 and r.json()["ok"] is False and "SMTP_USER" in r.json()["detalle"]


def test_prueba_de_chat_usa_el_webhook(env, monkeypatch):
    monkeypatch.setenv("SMTP_USER", "mis@confianza.pe")
    monkeypatch.setenv("SMTP_PASSWORD", "x")
    monkeypatch.setenv("GOOGLE_CHAT_WEBHOOK_URL", WEBHOOK)
    avisos = []
    monkeypatch.setattr(correo, "notificar_chat", lambda url, texto: avisos.append(url))
    assert cliente.post("/api/notificaciones/chat/prueba").json()["ok"] is True and avisos == [WEBHOOK]


def test_canal_desconocido_y_exige_sesion(env):
    assert cliente.post("/api/notificaciones/sms/prueba").status_code == 404
    assert TestClient(app).get("/api/notificaciones").status_code == 401
