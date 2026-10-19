"""Columnas que parecen fecha."""

import pytest

from modulos.diccionario.dominio.columnas import es_columna_fecha


@pytest.mark.parametrize("nombre,es", [("HFECPRO", True), ("FECHA_CIERRE", True), ("FC_DIA", True), ("periodo", True), ("HCODA", False), ("MEDIA", False), ("DIARIO", False)])
def test_columnas_que_parecen_fecha(nombre, es):
    assert es_columna_fecha(nombre) is es
