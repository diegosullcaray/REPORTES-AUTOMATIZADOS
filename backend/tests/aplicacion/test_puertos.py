"""Registro de puertos (aplicacion/puertos.py): los adaptadores se conectan al arrancar y las pruebas pueden sustituirlos."""

import pytest

import aplicacion.puertos as modulo
from aplicacion.puertos import Puertos, puertos, registrar


@pytest.fixture(autouse=True)
def restaurar():
    anterior = modulo._puertos
    yield
    modulo._puertos = anterior


def test_un_doble_registrado_reemplaza_al_adaptador_real():
    doble = Puertos(bd="bd", entorno="entorno", excel="excel", cola="cola", historial_validacion="h", lector_archivos="l", correo="c", google="g")
    registrar(doble)
    assert puertos() is doble and puertos().bd == "bd"


def test_sin_adaptadores_ni_fabrica_explica_que_hacer(monkeypatch):
    registrar(None)
    monkeypatch.setattr(modulo, "fabrica", None)
    with pytest.raises(RuntimeError, match="importa `composicion`"):
        puertos()


def test_con_fabrica_crea_los_adaptadores_la_primera_vez(monkeypatch):
    registrar(None)
    creados = []
    monkeypatch.setattr(modulo, "fabrica", lambda: creados.append(1) or "p")
    assert puertos() == "p" and puertos() == "p" and creados == [1]
