"""Secciones de /reportes: se guardan en disco (aislado por conftest) y solo agrupan reportes que existen."""

import pytest

from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.reportes.aplicacion.casos_uso import secciones
from modulos.reportes.aplicacion.dto import PedidoSeccion


def test_crear_listar_y_eliminar():
    nueva = secciones.crear(PedidoSeccion(nombre=" Cierre ", reportes=["saca-tu-garra", "saca-tu-garra"]))
    assert nueva.nombre == "Cierre" and nueva.reportes == ["saca-tu-garra"]
    assert [s.id for s in secciones.listar()] == [nueva.id]
    secciones.eliminar(nueva.id)
    assert secciones.listar() == []


def test_rechaza_nombre_vacio_repetido_y_reporte_inexistente():
    with pytest.raises(PeticionInvalida, match="nombre"):
        secciones.crear(PedidoSeccion(nombre="  "))
    with pytest.raises(PeticionInvalida, match="desconocidos"):
        secciones.crear(PedidoSeccion(nombre="A", reportes=["no-existe"]))
    secciones.crear(PedidoSeccion(nombre="A"))
    with pytest.raises(PeticionInvalida, match="Ya existe"):
        secciones.crear(PedidoSeccion(nombre="a"))


def test_eliminar_inexistente():
    with pytest.raises(NoEncontrado):
        secciones.eliminar("nada")
