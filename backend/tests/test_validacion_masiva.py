"""Validación masiva de tablas por responsable: cada tabla se verifica una vez y el pedido a Producción es uno solo."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from api import servicios, sesion
from api.app import app
from reportes.verificacion import Estado, Resultado, mensaje_solicitud_grupo

CORTE = date(2026, 6, 30)
cliente = TestClient(app)
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))


@pytest.fixture
def consultas(monkeypatch):
    """Cuenta las verificaciones por tabla; todas OK salvo las que se marquen como pendientes."""
    hechas: list[str] = []
    pendientes: set[str] = set()

    def falsa(tabla, fecha):
        hechas.append(tabla.nombre)
        if tabla.nombre in pendientes:
            return Resultado(tabla, Estado.DESACTUALIZADA, date(2026, 5, 31), "llega hasta mayo")
        return Resultado(tabla, Estado.OK, fecha)

    monkeypatch.setattr(servicios, "verificar_tabla", falsa)
    return hechas, pendientes


def test_cada_tabla_distinta_se_verifica_una_sola_vez(consultas):
    hechas, _ = consultas
    r = cliente.post("/api/validacion/piero", json={"fecha_corte": "2026-06-30"})
    assert r.status_code == 200
    assert len(hechas) == len(set(hechas)) == len(r.json()["tablas"])
    assert all(x["listo"] for x in r.json()["reportes"]) and r.json()["listo"] and r.json()["solicitud"] is None


def test_una_tabla_pendiente_marca_a_todos_los_reportes_que_la_usan(consultas):
    _, pendientes = consultas
    base = cliente.post("/api/validacion/piero", json={"fecha_corte": "2026-06-30"}).json()
    compartida = next(t for t in base["tablas"] if len(t["reportes"]) > 1)
    pendientes.add(next(n for n in servicios_nombres_de(compartida["nombre"])))
    r = cliente.post("/api/validacion/piero", json={"fecha_corte": "2026-06-30"}).json()
    afectados = {x["nombre"] for x in r["reportes"] if not x["listo"]}
    assert afectados == set(compartida["reportes"]) and not r["listo"]
    assert compartida["nombre"] in r["solicitud"] and r["solicitud"].count(compartida["nombre"]) == 1  # un solo renglón por tabla


def servicios_nombres_de(nombre_resuelto: str):
    """Nombre de registro de la tabla (con tokens) cuyo nombre resuelto es `nombre_resuelto`."""
    from reportes.tablas import TABLAS
    from reportes.verificacion import nombre_resuelto as resolver
    return [t.nombre for t in TABLAS.values() if resolver(t, CORTE) == nombre_resuelto]


def test_grupo_desconocido_es_404_y_mensual_exige_fin_de_mes(consultas):
    assert cliente.post("/api/validacion/nadie", json={}).status_code == 404
    r = cliente.post("/api/validacion/erick", json={"fecha_corte": "2026-06-15"})
    assert r.status_code == 422 and "fin de mes" in r.json()["detail"]


def test_la_solicitud_se_guarda_con_un_unico_archivo(consultas, monkeypatch, tmp_path):
    _, pendientes = consultas
    monkeypatch.setattr(servicios, "DIR_OUTPUTS", tmp_path)
    base = cliente.post("/api/validacion/erick", json={"fecha_corte": "2026-06-30"}).json()
    pendientes.update(servicios_nombres_de(base["tablas"][0]["nombre"]))
    r = cliente.post("/api/validacion/erick/solicitud", json={"fecha_corte": "2026-06-30"})
    assert r.status_code == 200 and r.json()["archivo"] == "solicitud_mensual_erick_20260630.txt"
    assert (tmp_path / "solicitudes" / r.json()["archivo"]).exists()


def test_mensaje_sin_pendientes_dice_que_no_hace_falta_pedir():
    assert "no hace falta" in mensaje_solicitud_grupo("Heredados de Piero", CORTE, [])


def test_la_validacion_masiva_exige_sesion():
    assert TestClient(app).post("/api/validacion/piero", json={}).status_code == 401
