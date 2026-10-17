"""Fichas del historial de validación en disco (infraestructura/historial_validacion.py)."""

from datetime import date

from modulos.reportes.infraestructura import historial_validacion as h
from modulos.reportes.aplicacion import dto as dto_reportes


def _ficha(id_, grupo="piero"):
    return dto_reportes.EntradaValidacion(id=id_, grupo=grupo, ejecutada="2026-10-16T10:00:00", corte=date(2026, 9, 30), listo=True, reportes=[],
                               tablas_total=0, tablas_ok=0, tablas_pendientes=0, tablas_dudosas=0)


def test_guarda_lista_y_poda_por_grupo(monkeypatch, tmp_path):
    monkeypatch.setattr(h, "DIR", tmp_path / "validaciones")
    assert h.listar("piero", 10) == []
    for i in ("a", "b", "c"):
        h.guardar(_ficha(i))
    h.guardar(_ficha("z", "erick"))
    assert [x.id for x in h.listar("piero", 10)] == ["c", "b", "a"]      # la más reciente primero
    assert [x.id for x in h.listar("piero", 2)] == ["c", "b"]
    h.podar("piero", 2)
    assert [x.id for x in h.listar("piero", 10)] == ["c", "b"] and [x.id for x in h.listar("erick", 10)] == ["z"]
