"""Contratos HTTP: la entrada mal formada se rechaza antes de llegar a los casos de uso."""

import pytest
from pydantic import ValidationError

from api.esquemas import PedidoEjecucion


def test_pedido_valida_fecha_y_correo():
    assert PedidoEjecucion(reporte="x", fecha_corte="2026-06-30").correo == "prueba"
    with pytest.raises(ValidationError):
        PedidoEjecucion(reporte="x", fecha_corte="30/06/2026")
    with pytest.raises(ValidationError):
        PedidoEjecucion(reporte="x", correo="a-todos-ya")
