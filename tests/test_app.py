"""Capa HTTP de la web: rutas y traducción de errores (no toca las bases reales)."""

from fastapi.testclient import TestClient

from api.app import app
from reportes.registro import REPORTES

cliente = TestClient(app)


def test_catalogo_lista_todos_los_reportes():
    r = cliente.get("/api/reportes")
    assert r.status_code == 200
    assert {x["nombre"] for x in r.json()} == set(REPORTES)


def test_reporte_desconocido_es_404():
    assert cliente.get("/api/reportes/no-existe").status_code == 404


def test_regla_incumplida_es_422_con_mensaje():
    r = cliente.post("/api/ejecuciones", json={"reporte": "saca-tu-garra", "fecha_corte": "2026-06-15"})
    assert r.status_code == 422 and "fin de mes" in r.json()["detail"]


def test_archivo_fuera_de_la_carpeta_es_404():
    assert cliente.get("/api/reportes/saca-tu-garra/archivos/..%2F..%2F.env/vista-previa").status_code == 404
