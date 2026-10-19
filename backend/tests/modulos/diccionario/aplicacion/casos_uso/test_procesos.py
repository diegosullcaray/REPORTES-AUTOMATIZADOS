"""Procesos del repo DICCIONARIO: solo los de la lista."""

from types import SimpleNamespace

import pytest

from core.excepciones import NoEncontrado
from modulos.diccionario.aplicacion import dto
from modulos.diccionario.aplicacion.casos_uso import procesos
from modulos.diccionario.aplicacion.puertos import Puertos, puertos
from modulos.diccionario.dominio.columnas import PROCESOS


@pytest.fixture(autouse=True)
def sin_puertos():
    yield
    puertos.registrar(None)


class Lanzador:
    def __init__(self):
        self.lanzados = []

    def ejecutar(self, proceso, comando, carpeta):
        self.lanzados.append((proceso, comando, carpeta))
        return dto.Ejecucion(id="abc", proceso=proceso, estado="ejecutando", inicio="2026-10-18T10:00:00", fin=None, codigo=None)


def test_solo_lanza_procesos_de_la_lista():
    lanzador = Lanzador()
    puertos.registrar(Puertos(lector=SimpleNamespace(carpeta=lambda: "carpeta"), lanzador=lanzador, catalogo=SimpleNamespace()))
    with pytest.raises(NoEncontrado):
        procesos.ejecutar("rm -rf")
    assert procesos.ejecutar("verificar").id == "abc"
    assert lanzador.lanzados == [("verificar", PROCESOS["verificar"].comando, "carpeta")]
