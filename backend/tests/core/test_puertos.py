"""Registro de puertos (core/puertos.py): los adaptadores de cada módulo se conectan al arrancar y las pruebas pueden sustituirlos."""

import pytest

from core.puertos import Nucleo, Registro, nucleo


def test_un_doble_registrado_reemplaza_al_adaptador_real():
    registro = Registro("demo")
    registro.registrar("doble")
    assert registro() == "doble"


def test_sin_adaptadores_ni_fabrica_explica_que_hacer():
    with pytest.raises(RuntimeError, match="«demo».*config.composicion"):
        Registro("demo")()


def test_con_fabrica_crea_los_adaptadores_la_primera_vez():
    registro, creados = Registro("demo"), []
    registro.fabrica = lambda: creados.append(1) or "p"
    assert registro() == "p" and registro() == "p" and creados == [1]
    registro.registrar(None)           # desconectar: vuelve a pedir la fábrica
    assert registro() == "p" and creados == [1, 1]


def test_el_nucleo_arranca_con_la_base_de_datos_y_el_entorno_reales():
    n = nucleo()
    assert isinstance(n, Nucleo) and callable(n.bd.leer_sql) and n.entorno.raiz().name == "backend"
