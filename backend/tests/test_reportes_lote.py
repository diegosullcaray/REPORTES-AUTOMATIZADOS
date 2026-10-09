"""Todos los reportes de lote: importan, resuelven sus tokens de fecha y declaran tablas."""

from datetime import date
from importlib import import_module

import pytest

from reportes.comun.fechas import Cortes
from reportes.db import partir_lotes
from reportes.registro import REPORTES
from reportes.tablas import USO

LOTES = [(r.nombre, getattr(import_module(r.modulo), "REPORTE", None)) for r in REPORTES.values()]
LOTES = [(n, l) for n, l in LOTES if l is not None]


def test_hay_17_reportes_de_lote():
    assert len(LOTES) == 17


@pytest.mark.parametrize("nombre,lote", LOTES)
def test_tokens_resueltos_y_sin_fechas_fijas(nombre, lote):
    assert lote.comando == nombre and nombre in USO
    c = Cortes.mensual(date(2026, 7, 31)) if lote.frecuencia == "mensual" else Cortes(date(2026, 7, 31))
    sql = c.aplicar(lote.sql)
    assert "@@" not in sql and partir_lotes(sql)
    assert "20260731" in sql or "2026-07-31" in sql  # el corte entró en la consulta


def test_tapp_declara_que_escribe_en_bd():
    assert dict(LOTES)["tapp-saldo-medio-territorio"].escribe_en_bd is True
    assert dict(LOTES)["michael-castigos"].vacio_valido is True


@pytest.mark.parametrize("nombre,lote", LOTES)
def test_servidor_y_base_coherentes_con_sus_tablas(nombre, lote):
    from reportes.config import servidor_de_base
    from reportes.tablas import tablas_de

    assert REPORTES[nombre].servidores == (lote.servidor,)
    if lote.base:
        assert servidor_de_base(lote.base) == lote.servidor
    assert {t.servidor for t in tablas_de(nombre) if t.tipo != "destino"} == {lote.servidor}
