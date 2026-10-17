"""Formato de columnas de un reporte (aplicacion/columnas.py): orden, encabezados y reemplazo de 0 y nulos."""

import pandas as pd
import pytest

from modulos.reportes.aplicacion.columnas import aplicar_columnas
from modulos.reportes.dominio.formato_excel import Columna, ColumnaFaltante


def test_deja_solo_las_columnas_del_formato_en_su_orden_y_con_su_encabezado():
    df = pd.DataFrame({"Monto": [1, 0, None], "sobra": [9, 9, 9], "FECHA": ["a", "b", "c"]})
    r = aplicar_columnas(df, (Columna("fecha", "Fecha", formato="dd/mm/yyyy"), Columna("MONTO", "Importe", si_cero="-", si_nulo="NULL")))
    assert list(r.columns) == ["Fecha", "Importe"]
    assert list(r["Importe"]) == [1, "-", "NULL"] and r.attrs["formatos"] == {"Fecha": "dd/mm/yyyy"}


def test_columna_con_varios_origenes_toma_la_primera_que_exista():
    r = aplicar_columnas(pd.DataFrame({"B": [1]}), (Columna(("A", "B"), "Valor"),))
    assert list(r["Valor"]) == [1]


def test_columna_que_falta_es_error_que_lista_las_que_trae():
    with pytest.raises(ColumnaFaltante, match="trae: B"):
        aplicar_columnas(pd.DataFrame({"B": [1]}), (Columna("A", "A"),))
