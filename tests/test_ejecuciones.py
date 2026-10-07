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


def test_codigo_3_es_tablas_desactualizadas():
    assert ejecuciones.ESTADO_POR_CODIGO[3] == "tablas_desactualizadas"


def test_id_invalido_no_sale_de_la_carpeta():
    import pytest

    with pytest.raises(KeyError):
        ejecuciones.obtener("../../.env")
