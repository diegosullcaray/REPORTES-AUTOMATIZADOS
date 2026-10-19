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


def test_una_tarea_propia_escribe_su_log_mientras_corre(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")
    seguir, vista = threading.Event(), []

    def tarea(emitir):
        emitir("▶ probando\n")
        seguir.wait(5)
        emitir("✗ mish: sin red\n")
        return 1

    x = lanzador.ejecutar_tarea("bases", tarea)
    for _ in range(50):                                   # la primera línea ya se ve con la tarea a medias
        vista = lanzador.obtener(x.id)
        if "probando" in vista.log:
            break
        time.sleep(0.05)
    assert vista.estado == "ejecutando" and "probando" in vista.log and "mish" not in vista.log
    seguir.set()
    _esperar_fin()
    d = lanzador.obtener(x.id)
    assert (d.proceso, d.estado, d.codigo) == ("bases", "error", 1) and "mish" in d.log


def test_si_la_tarea_revienta_no_queda_ejecutando(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")

    def rota(emitir):
        raise RuntimeError("boom")

    x = lanzador.ejecutar_tarea("bases", rota)
    _esperar_fin()
    d = lanzador.obtener(x.id)
    assert d.estado == "error" and "boom" in d.log and not lanzador.en_curso()


def test_si_la_tarea_revienta_conserva_lo_que_ya_habia_escrito(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")

    def a_medias(emitir):
        emitir("✓ mish: ok" + chr(10))
        raise RuntimeError("boom")

    x = lanzador.ejecutar_tarea("bases", a_medias)
    _esperar_fin()
    log = lanzador.obtener(x.id).log
    assert log.startswith("✓ mish: ok") and log.rstrip().endswith("boom")   # lo hecho primero y, al final, el error


def test_un_hilo_rezagado_no_escribe_en_el_log_ya_cerrado(monkeypatch, tmp_path):
    monkeypatch.setattr(lanzador, "DIR", tmp_path / "d")
    guardado = []

    def tarea(emitir):
        guardado.append(emitir)
        return 0

    x = lanzador.ejecutar_tarea("bases", tarea)
    _esperar_fin()
    guardado[0]("tarde\n")                                 # no debe fallar ni escribir
    assert "tarde" not in lanzador.obtener(x.id).log
