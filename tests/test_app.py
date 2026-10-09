"""Capa HTTP de la web: rutas y traducción de errores (no toca las bases reales)."""

from fastapi.testclient import TestClient

from api import sesion
from api.app import app
from reportes.registro import REPORTES

cliente = TestClient(app)
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))


def test_catalogo_lista_todos_los_reportes():
    r = cliente.get("/api/reportes")
    assert r.status_code == 200
    assert {x["nombre"] for x in r.json()} == set(REPORTES)


def test_reporte_desconocido_es_404():
    assert cliente.get("/api/reportes/no-existe").status_code == 404


def test_regla_incumplida_es_422_con_mensaje():
    r = cliente.post("/api/ejecuciones", json={"reporte": "saca-tu-garra", "fecha_corte": "2026-06-15"})
    assert r.status_code == 422 and "fin de mes" in r.json()["detail"]


def test_servidores_sin_secretos(monkeypatch):
    monkeypatch.setenv("RCC_PASSWORD", "no-debe-salir")
    r = cliente.get("/api/servidores")
    assert r.status_code == 200
    assert {s["nombre"] for s in r.json()} == {"mish", "slc", "rcc"}
    assert "no-debe-salir" not in r.text


def test_configuracion_informa_cortes_y_carpetas(monkeypatch):
    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "2026-09-30")
    c = cliente.get("/api/configuracion").json()
    assert c["corte_mensual"] == {"fecha": "2026-09-30", "origen": ".env (FECHA_CORTE_MENSUAL)"}
    assert c["dir_outputs"]


def test_perfil_no_expone_secretos(monkeypatch):
    monkeypatch.setenv("SMTP_USER", "mis@confianza.pe")
    monkeypatch.setenv("SMTP_PASSWORD", "clave-secreta")
    monkeypatch.setenv("GOOGLE_CHAT_WEBHOOK_URL", "https://chat.example/webhook-secreto")
    r = cliente.get("/api/perfil")
    assert r.status_code == 200
    p = r.json()
    assert (p["cuenta_envio"], p["clave_envio_configurada"], p["webhook_configurado"]) == ("mis@confianza.pe", True, True)
    assert "clave-secreta" not in r.text and "webhook-secreto" not in r.text


def test_historial_respeta_el_limite():
    assert cliente.get("/api/ejecuciones?limite=0").status_code == 422


def test_prueba_de_servidor_desconocido_es_404():
    assert cliente.post("/api/servidores/otro/prueba").status_code == 404


def test_archivo_fuera_de_la_carpeta_es_404():
    assert cliente.get("/api/reportes/saca-tu-garra/archivos/..%2F..%2F.env/vista-previa").status_code == 404


def test_sin_sesion_la_api_responde_401():
    assert TestClient(app).get("/api/reportes").status_code == 401
