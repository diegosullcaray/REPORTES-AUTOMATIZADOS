from datetime import date, datetime

import pandas as pd
import pytest

from reportes import verificacion as v
from reportes.config import ConfiguracionError
from reportes.tablas import Tabla


def test_fecha_esperada_diaria_lunes_toma_sabado():
    assert v.fecha_esperada("diaria", hoy=date(2026, 10, 5)) == date(2026, 10, 3)  # lunes
    assert v.fecha_esperada("diaria", hoy=date(2026, 10, 7)) == date(2026, 10, 6)


def test_mensual_exige_fecha_corte(monkeypatch):
    monkeypatch.delenv("FECHA_CORTE_MENSUAL", raising=False)
    with pytest.raises(ConfiguracionError):
        v.fecha_esperada("mensual")


def test_nombre_dinamico_se_resuelve():
    t = Tabla("db{yyyymm}.dbo.ccd{yyyymmdd}", "rcc", "dinamica", None, "por_confirmar")
    assert v.nombre_resuelto(t, date(2026, 9, 30)) == "db202609.dbo.ccd20260930"


def _tabla():
    return Tabla("storage.com_act.hcda001", "slc", "historica", "HFECPRO", "confirmada")


def test_tabla_al_dia(monkeypatch):
    monkeypatch.setattr(v, "leer_sql", lambda *a, **k: pd.DataFrame({"u": [datetime(2026, 10, 31)]}))
    r = v.verificar_tabla(_tabla(), date(2026, 10, 31))
    assert r.estado is v.Estado.OK


def test_tabla_desactualizada_genera_solicitud(monkeypatch):
    monkeypatch.setattr(v, "leer_sql", lambda *a, **k: pd.DataFrame({"u": [datetime(2026, 10, 29)]}))
    r = v.verificar_tabla(_tabla(), date(2026, 10, 31))
    assert r.estado is v.Estado.DESACTUALIZADA and r.ultima_fecha == date(2026, 10, 29)
    texto = v.mensaje_solicitud("saca-tu-garra", date(2026, 10, 31), [r])
    assert "storage.com_act.hcda001" in texto and "29/10/2026" in texto


def test_tabla_inexistente(monkeypatch):
    def falla(*a, **k):
        raise RuntimeError("Invalid object name 'x'")

    monkeypatch.setattr(v, "leer_sql", falla)
    t = Tabla("db{yyyymm}.dbo.ccd{yyyymmdd}", "rcc", "dinamica", None, "por_confirmar")
    assert v.verificar_tabla(t, date(2026, 9, 30)).estado is v.Estado.NO_EXISTE


def test_referencia_sin_control():
    t = Tabla("storage.ref.rcalen001", "slc", "referencia", None, "por_confirmar")
    assert v.verificar_tabla(t, date(2026, 9, 30)).estado is v.Estado.SIN_CONTROL


def test_nombre_malicioso_no_se_ejecuta(monkeypatch):
    llamado = []
    monkeypatch.setattr(v, "leer_sql", lambda *a, **k: llamado.append(1))
    t = Tabla("x; DROP TABLE y", "slc", "historica", "HFECPRO", "confirmada")
    assert v.verificar_tabla(t, date(2026, 9, 30)).estado is v.Estado.ERROR and not llamado
