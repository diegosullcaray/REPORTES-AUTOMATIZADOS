"""Vista previa de archivos Excel (infraestructura/lector_archivos.py)."""

from datetime import date, datetime
from decimal import Decimal

import pandas as pd

from modulos.reportes.infraestructura import lector_archivos


def test_lee_hojas_con_columnas_y_limita_las_filas(tmp_path):
    ruta = tmp_path / "r.xlsx"
    pd.DataFrame({"A": range(30), "B": ["x"] * 30}).to_excel(ruta, index=False, sheet_name="Datos")
    (hoja,) = lector_archivos.hojas_excel(ruta, 5)
    assert (hoja.nombre, hoja.columnas, hoja.total_filas, len(hoja.filas)) == ("Datos", ["A", "B"], 30, 5)


def test_celdas_se_convierten_a_valores_de_json():
    assert lector_archivos._celda(Decimal("1.5")) == 1.5
    assert lector_archivos._celda(date(2026, 9, 30)) == "2026-09-30"
    assert lector_archivos._celda(datetime(2026, 9, 30, 8, 0)) == "2026-09-30T08:00:00"
    assert lector_archivos._celda(None) is None and lector_archivos._celda(object()).startswith("<object")
