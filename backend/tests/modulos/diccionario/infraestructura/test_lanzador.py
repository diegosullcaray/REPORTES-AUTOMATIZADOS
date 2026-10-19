"""Lanzador de procesos del repo DICCIONARIO (subproceso real, sin tocar ese repo)."""

import json
import sys
import threading
import time

import pytest

from core.excepciones import PeticionInvalida
from modulos.diccionario.infraestructura import lanzador


def _esperar_fin():
    for _ in range(100):
        if not lanzador.en_curso():
            return
        time.sleep(0.1)
    pytest.fail("el proceso no terminó")


@pytest.mark.parametrize("codigo,estado", [(0, "ok"), (3, "error")])
def test_lanza_un_proceso_y_deja_su_estado_y_log(monkeypatch, tmp_path, codigo, estado):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")
    x = lanzador.ejecutar("prueba", (sys.executable, "-c", f"print('hola'); raise SystemExit({codigo})"), tmp_path)
    assert x.estado == "ejecutando" and lanzador.en_curso()
    _esperar_fin()
    d = lanzador.obtener(x.id)
    assert (d.estado, d.codigo) == (estado, codigo) and "hola" in d.log and d.fin
    assert [e.id for e in lanzador.historial()] == [x.id]


def test_comando_inexistente_queda_como_error_con_su_mensaje(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")
    x = lanzador.ejecutar("prueba", ("programa-que-no-existe",), tmp_path)
    _esperar_fin()
    d = lanzador.obtener(x.id)
    assert d.estado == "error" and "No encuentro" in d.log


def test_un_proceso_que_quedo_a_medias_tras_reiniciar_se_muestra_como_error(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path)
    (tmp_path / "abc.json").write_text(json.dumps({"id": "abc", "proceso": "generar", "estado": "ejecutando", "inicio": "2026-10-18T10:00:00", "fin": None, "codigo": None}), encoding="utf-8")
    assert lanzador.historial()[0].estado == "error"
    with pytest.raises(KeyError):
        lanzador.obtener("../../.env")


def test_dos_peticiones_a_la_vez_lanzan_un_solo_proceso(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")
    lento = (sys.executable, "-c", "import time; time.sleep(1)")
    resultados = []

    def pedir():
        try:
            resultados.append(lanzador.ejecutar("prueba", lento, tmp_path).id)
        except PeticionInvalida:
            resultados.append(None)

    hilos = [threading.Thread(target=pedir) for _ in range(8)]
    [h.start() for h in hilos]
    [h.join() for h in hilos]
    assert sum(r is not None for r in resultados) == 1
    _esperar_fin()


def test_el_proceso_no_ve_las_claves_de_la_api(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")
    monkeypatch.setenv("SMTP_PASSWORD", "clave-secreta")
    x = lanzador.ejecutar("prueba", (sys.executable, "-c", "import os; print('SMTP' if 'SMTP_PASSWORD' in os.environ else 'limpio')"), tmp_path)
    _esperar_fin()
    assert "limpio" in lanzador.obtener(x.id).log


@pytest.mark.skipif(sys.platform != "win32", reason="en Windows node no arranca sin SYSTEMROOT")
def test_el_proceso_conserva_lo_que_windows_exige(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")
    x = lanzador.ejecutar("prueba", (sys.executable, "-c", "import os; print('SYSTEMROOT' in os.environ and 'PATH' in os.environ)"), tmp_path)
    _esperar_fin()
    assert "True" in lanzador.obtener(x.id).log


def test_el_historial_conserva_solo_las_ultimas_fichas(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path)
    monkeypatch.setattr(lanzador, "MAX_FICHAS", 2)
    for i in range(4):
        (tmp_path / f"a{i}.json").write_text("{}", encoding="utf-8")
        time.sleep(0.02)
    lanzador._podar()
    assert sorted(p.stem for p in tmp_path.glob("*.json")) == ["a2", "a3"]
