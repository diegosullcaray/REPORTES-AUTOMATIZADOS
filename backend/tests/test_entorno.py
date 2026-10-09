"""Edición del .env desde la web: solo cambia lo enviado, valida y no toca los secretos."""

import os

import pytest
from fastapi.testclient import TestClient

from api import entorno, servicios, sesion
from api.app import app

cliente = TestClient(app)
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))


@pytest.fixture
def env(tmp_path, monkeypatch):
    ruta = tmp_path / ".env"
    ruta.write_text("RCC_PASSWORD=secreto\nFECHA_CORTE_MENSUAL=2026-08-31\n# comentario\n", encoding="utf-8")
    monkeypatch.setattr(servicios, "ENV", ruta)
    for var in ("FECHA_CORTE_MENSUAL", "FECHA_CORTE_DIARIA"):
        monkeypatch.delenv(var, raising=False)
    return ruta


def test_escribir_cambia_agrega_y_quita_sin_tocar_el_resto(tmp_path):
    ruta = tmp_path / ".env"
    ruta.write_text("A=1\nB=2\n# nota\n", encoding="utf-8")
    entorno.escribir(ruta, {"A": "9", "B": "", "C": "3", "D": ""})
    assert ruta.read_text(encoding="utf-8") == "A=9\n# nota\nC=3\n"


def test_guardar_cortes_actualiza_el_env_y_el_proceso(env):
    r = cliente.put("/api/configuracion", json={"corte_mensual": "2026-09-30", "corte_diario": "2026-10-01"})
    assert r.status_code == 200
    assert r.json()["corte_mensual"]["fecha"] == "2026-09-30" and r.json()["corte_diario"]["fecha"] == "2026-10-01"
    texto = env.read_text(encoding="utf-8")
    assert "FECHA_CORTE_MENSUAL=2026-09-30" in texto and "FECHA_CORTE_DIARIA=2026-10-01" in texto and "RCC_PASSWORD=secreto" in texto
    assert os.environ["FECHA_CORTE_MENSUAL"] == "2026-09-30"  # las ejecuciones heredan este valor


def test_texto_vacio_quita_la_variable(env, monkeypatch):
    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "2026-08-31")
    cliente.put("/api/configuracion", json={"corte_mensual": ""})
    assert "FECHA_CORTE_MENSUAL" not in env.read_text(encoding="utf-8") and "FECHA_CORTE_MENSUAL" not in os.environ


@pytest.mark.parametrize("cuerpo,fragmento", [
    ({"corte_mensual": "2026-09-15"}, "fin de mes"),
    ({"corte_mensual": "no-es-fecha"}, "FECHA_CORTE_MENSUAL"),
    ({"corte_diario": "2999-01-01"}, "futuro"),
    ({"dir_outputs": "relativa/salidas"}, "ruta completa"),
    ({"driver_odbc": "x\nRCC_PASSWORD=malo"}, "saltos de línea"),
    ({"dir_inputs": "D:\\datos # comentario"}, "comillas"),
    ({}, "ningún ajuste"),
])
def test_valores_invalidos_se_rechazan_sin_escribir(env, cuerpo, fragmento):
    antes = env.read_text(encoding="utf-8")
    r = cliente.put("/api/configuracion", json=cuerpo)
    assert r.status_code == 422 and fragmento in r.json()["detail"]
    assert env.read_text(encoding="utf-8") == antes


def test_carpetas_y_driver_quedan_pendientes_de_reinicio(env):
    r = cliente.put("/api/configuracion", json={"dir_outputs": "D:\\otra\\salida", "driver_odbc": "ODBC Driver 18 for SQL Server"})
    assert r.status_code == 200
    assert set(r.json()["pendientes_reinicio"]) == {"carpeta de salidas", "driver ODBC"}
    assert "REPORTES_DIR_OUTPUTS=D:\\otra\\salida" in env.read_text(encoding="utf-8")


def test_la_edicion_exige_sesion():
    assert TestClient(app).put("/api/configuracion", json={"corte_diario": ""}).status_code == 401
