"""Cada tabla de cada reporte tiene su condición de fecha documentada (insumo para Producción)."""

from reportes.cli_tablas import cmd_columnas_fecha, filas_columnas_fecha
from reportes.reglas_fecha import REGLAS
from reportes.tablas import TABLAS, USO
from reportes.verificacion import mensaje_solicitud
from datetime import date


def test_reglas_cubren_exactamente_el_uso():
    assert set(REGLAS) == set(USO)
    for rep, tablas in USO.items():
        assert set(REGLAS[rep]) == set(tablas), rep


def test_tabla_con_columna_tiene_condicion_que_la_nombra():
    for rep, tablas in USO.items():
        for n in tablas:
            col = TABLAS[n].col_fecha
            if col and TABLAS[n].tipo in {"historica", "stock"}:
                assert col.lower() in REGLAS[rep][n].lower(), (rep, n)


def test_filas_y_comando(capsys):
    assert len(filas_columnas_fecha("saca-tu-garra")) == len(USO["saca-tu-garra"])
    assert cmd_columnas_fecha(["saca-tu-garra"]) == 0
    assert "HFECPRO" in capsys.readouterr().out
    assert cmd_columnas_fecha(["no-existe"]) == 2


def test_solicitud_incluye_condicion():
    assert "el reporte filtra:" in mensaje_solicitud("saca-tu-garra", date(2026, 9, 30))
