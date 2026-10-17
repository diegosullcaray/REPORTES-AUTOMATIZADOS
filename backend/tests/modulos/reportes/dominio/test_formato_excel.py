"""Descripción del formato Excel de un reporte (dominio/formato_excel.py): valores inmutables y por defecto."""

import dataclasses

import pytest

from modulos.reportes.dominio.formato_excel import Columna, FORMATO_MONEDA, Resumen


def test_resumen_usa_formato_de_soles_por_defecto():
    r = Resumen("RESUMEN_v2", ("NIVEL",), "Saldo", "FILAS", "VALOR")
    assert r.formato == FORMATO_MONEDA == '"S/" #,##0.00' and r.origen == 0


def test_son_inmutables():
    col = Columna("saldo", "Saldo")
    with pytest.raises(dataclasses.FrozenInstanceError):
        col.titulo = "otro"
