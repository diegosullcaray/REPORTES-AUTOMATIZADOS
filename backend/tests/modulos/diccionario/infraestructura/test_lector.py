"""Lector del diccionario.json: dónde lo busca y cuándo lo vuelve a leer."""

import json
import os

import pytest

from core.excepciones import NoEncontrado
from modulos.diccionario.infraestructura import lector


def test_sin_diccionario_dice_donde_buscarlo(monkeypatch, tmp_path):
    monkeypatch.setenv("DICCIONARIO_DIR", str(tmp_path))
    with pytest.raises(NoEncontrado, match="DICCIONARIO_DIR"):
        lector.leer()


def test_el_lector_relee_solo_si_el_archivo_cambio(monkeypatch, tmp_path):
    (tmp_path / "diccionario").mkdir()
    archivo = tmp_path / "diccionario" / "diccionario.json"
    archivo.write_text(json.dumps({"v": 1}), encoding="utf-8")
    monkeypatch.setenv("DICCIONARIO_DIR", str(tmp_path))
    monkeypatch.setattr(lector, "_cache", None)
    primero = lector.leer()
    assert lector.leer() is primero
    archivo.write_text(json.dumps({"v": 2}), encoding="utf-8")
    os.utime(archivo, ns=(archivo.stat().st_atime_ns, archivo.stat().st_mtime_ns + 10**9))
    assert lector.leer() == {"v": 2}
