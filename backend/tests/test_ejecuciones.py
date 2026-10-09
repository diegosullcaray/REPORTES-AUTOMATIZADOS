"""Cola de ejecuciones: corre main.py como subproceso y deja estado + log en disco."""

from api import ejecuciones


def test_ejecucion_completa_guarda_estado_y_log(tmp_path, monkeypatch):
    monkeypatch.setattr(ejecuciones, "DIR", tmp_path)
    monkeypatch.setattr(ejecuciones, "carpeta_salida", lambda _: tmp_path / "salida")
    x = ejecuciones.encolar("saca-tu-garra", ["listar"])  # `main.py listar` no se conecta a nada
    assert ejecuciones.obtener(x.id).estado == "en_cola"
    ejecuciones._correr(x.id)
    d = ejecuciones.obtener(x.id)
    assert (d.estado, d.codigo) == ("ok", 0)
    assert "saca-tu-garra" in d.log
    assert [h.id for h in ejecuciones.historial("saca-tu-garra")] == [x.id]


def test_historial_va_de_la_mas_reciente_a_la_mas_antigua(tmp_path, monkeypatch):
    monkeypatch.setattr(ejecuciones, "DIR", tmp_path)
    from api.esquemas import Ejecucion

    for i, inicio in enumerate(["2026-10-01T10:00:00", "2026-10-03T10:00:00", "2026-10-02T10:00:00"]):
        ejecuciones._guardar(Ejecucion(id=f"e{i}", reporte="saca-tu-garra", argumentos=[], estado="ok", codigo=0, inicio=inicio, fin=None))
    assert [x.inicio[:10] for x in ejecuciones.historial(limite=3)] == ["2026-10-03", "2026-10-02", "2026-10-01"]


def test_codigo_3_es_tablas_desactualizadas():
    assert ejecuciones.ESTADO_POR_CODIGO[3] == "tablas_desactualizadas"


def test_id_invalido_no_sale_de_la_carpeta():
    import pytest

    with pytest.raises(KeyError):
        ejecuciones.obtener("../../.env")
