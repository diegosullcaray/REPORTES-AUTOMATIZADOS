"""Lector del diccionario generado desde la base: se guarda sin dejar archivos a medias y se relee solo si cambió."""

import os

import pytest

from core.excepciones import NoEncontrado
from modulos.diccionario.infraestructura import lector


@pytest.fixture(autouse=True)
def salidas(monkeypatch, tmp_path):
    monkeypatch.setattr(lector, "DIR_OUTPUTS", tmp_path / "salidas")
    monkeypatch.setattr(lector, "_cache", None)


def test_sin_diccionario_dice_como_generarlo():
    with pytest.raises(NoEncontrado, match="Generar el diccionario desde la base"):
        lector.leer()
    assert lector.origen() is None


def test_guarda_y_lee_sin_dejar_el_temporal(tmp_path):
    lector.guardar({"reportes": [], "marca": "bd"})
    assert lector.leer()["marca"] == "bd" and lector.origen()
    assert not list((tmp_path / "salidas").rglob("*.tmp"))                    # el reemplazo es atómico


def test_el_lector_relee_solo_si_el_archivo_cambio(tmp_path):
    lector.guardar({"v": 1})
    primero = lector.leer()
    assert lector.leer() is primero
    lector.guardar({"v": 2})
    archivo = lector._archivo()
    os.utime(archivo, ns=(archivo.stat().st_atime_ns, archivo.stat().st_mtime_ns + 10**9))
    assert lector.leer() == {"v": 2}
