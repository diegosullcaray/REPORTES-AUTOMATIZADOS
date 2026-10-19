"""Lector del repo DICCIONARIO: el diccionario.json, el código de sus scripts y los archivos que genera (solo lo que está dentro del repo)."""

import json
import os

import pytest

from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.diccionario.infraestructura import lector


@pytest.fixture
def repo(monkeypatch, tmp_path):
    base = tmp_path / "DICCIONARIO"
    (base / "diccionario").mkdir(parents=True)
    (base / "diccionario" / "diccionario.json").write_text(json.dumps({"v": 1}), encoding="utf-8")
    (base / "diccionario" / "reportes.md").write_text("# reportes", encoding="utf-8")
    (base / "diccionario" / "x.xlsx").write_bytes(b"PK")
    (base / "governance" / "scripts").mkdir(parents=True)
    (base / "governance" / "scripts" / "gen.mjs").write_text("console.log(1)", encoding="utf-8")
    scripts = {"generar": "node governance/scripts/gen.mjs && node ../fuera.mjs", "test": "node --test x/*.test.mjs"}
    (base / "package.json").write_text(json.dumps({"scripts": scripts}), encoding="utf-8")
    (tmp_path / "fuera.mjs").write_text("secreto", encoding="utf-8")   # fuera del repo: nunca se muestra
    monkeypatch.setenv("DICCIONARIO_DIR", str(base))
    monkeypatch.setattr(lector, "DIR_OUTPUTS", tmp_path / "salidas")
    monkeypatch.setattr(lector, "_cache", None)
    return base


def test_sin_diccionario_dice_como_generarlo(monkeypatch, tmp_path):
    monkeypatch.setenv("DICCIONARIO_DIR", str(tmp_path / "no-hay-repo"))
    monkeypatch.setattr(lector, "DIR_OUTPUTS", tmp_path / "salidas")
    with pytest.raises(NoEncontrado, match="Generar el diccionario desde la base"):
        lector.leer()
    assert lector.origen() is None and not lector.repo_disponible()


def test_el_lector_relee_solo_si_el_archivo_cambio(repo):
    primero = lector.leer()
    assert lector.leer() is primero
    archivo = repo / "diccionario" / "diccionario.json"
    archivo.write_text(json.dumps({"v": 2}), encoding="utf-8")
    os.utime(archivo, ns=(archivo.stat().st_atime_ns, archivo.stat().st_mtime_ns + 10**9))
    assert lector.leer() == {"v": 2}


def test_lista_los_archivos_que_dejan_los_patrones(repo):
    a = {x.ruta: x.tipo for x in lector.archivos(("diccionario/*.md", "diccionario/diccionario.json", "diccionario/*.xlsx"))}
    assert a == {"diccionario/reportes.md": "texto", "diccionario/diccionario.json": "texto", "diccionario/x.xlsx": "otro"}


def test_solo_se_lee_texto_de_los_archivos_de_los_patrones(repo):
    assert lector.texto("diccionario/reportes.md", ("diccionario/*.md",)).texto == "# reportes"
    for ruta in ("package.json", "../fuera.mjs", "diccionario/diccionario.json"):
        with pytest.raises(NoEncontrado):
            lector.texto(ruta, ("diccionario/*.md",))
    with pytest.raises(PeticionInvalida):
        lector.texto("diccionario/x.xlsx", ("diccionario/*.xlsx",))


def test_el_script_trae_el_comando_y_el_codigo_de_sus_archivos_pero_no_los_de_fuera(repo):
    s = lector.script_npm("generar")
    assert [x.ruta for x in s] == ["package.json › scripts.generar", "governance/scripts/gen.mjs"]   # ../fuera.mjs no entra
    assert [x.ruta for x in lector.script_npm("test")] == ["package.json › scripts.test"]
    with pytest.raises(NoEncontrado):
        lector.script_npm("inventado")


def test_el_diccionario_generado_desde_la_base_funciona_sin_el_repo(monkeypatch, tmp_path):
    monkeypatch.setenv("DICCIONARIO_DIR", str(tmp_path / "no-hay-repo"))
    monkeypatch.setattr(lector, "DIR_OUTPUTS", tmp_path / "salidas")
    monkeypatch.setattr(lector, "_cache", None)
    lector.guardar({"reportes": [], "marca": "bd"})
    assert lector.leer()["marca"] == "bd" and lector.origen()[0] == "bd" and not lector.repo_disponible()
    assert not list((tmp_path / "salidas").rglob("*.tmp"))                    # el reemplazo es atómico: no queda el temporal


def test_si_hay_los_dos_se_usa_el_escrito_ultimo(repo):
    archivo = repo / "diccionario" / "diccionario.json"
    lector.guardar({"marca": "bd"})
    generado = repo.parent / "salidas" / "diccionario" / "generado" / "diccionario.json"
    os.utime(archivo, ns=(archivo.stat().st_atime_ns, generado.stat().st_mtime_ns - 10**9))      # el del repo, más viejo
    assert lector.leer() == {"marca": "bd"} and lector.origen()[0] == "bd"
    os.utime(archivo, ns=(archivo.stat().st_atime_ns, generado.stat().st_mtime_ns + 10**9))      # ahora el del repo es el más nuevo
    assert lector.leer() == {"v": 1} and lector.origen()[0] == "repo" and lector.repo_disponible()


def test_un_json_a_medias_dice_que_reintente_en_vez_de_romper(repo):
    (repo / "diccionario" / "diccionario.json").write_text('{"reportes": [', encoding="utf-8")
    with pytest.raises(NoEncontrado, match="Reintenta"):
        lector.leer()
