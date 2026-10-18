"""Cola de ejecuciones: corre main.py como subproceso y deja estado + log en disco."""

from modulos.reportes.infraestructura import cola_ejecuciones as ejecuciones


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
    from modulos.reportes.aplicacion.dto import Ejecucion

    for i, inicio in enumerate(["2026-10-01T10:00:00", "2026-10-03T10:00:00", "2026-10-02T10:00:00"]):
        ejecuciones._guardar(Ejecucion(id=f"e{i}", reporte="saca-tu-garra", argumentos=[], estado="ok", codigo=0, inicio=inicio, fin=None))
    assert [x.inicio[:10] for x in ejecuciones.historial(limite=3)] == ["2026-10-03", "2026-10-02", "2026-10-01"]


def test_codigo_3_es_tablas_desactualizadas():
    assert ejecuciones.ESTADO_POR_CODIGO[3] == "tablas_desactualizadas"


def test_id_invalido_no_sale_de_la_carpeta():
    import pytest

    with pytest.raises(KeyError):
        ejecuciones.obtener("../../.env")


def _guardar_ejecucion(id_, estado):
    from modulos.reportes.aplicacion.dto import Ejecucion

    ejecuciones._guardar(Ejecucion(id=id_, reporte="saca-tu-garra", argumentos=[], estado=estado, codigo=None, inicio="2026-10-01T10:00:00", fin=None))
    (ejecuciones.DIR / f"{id_}.log").write_text("salida", encoding="utf-8")


def test_eliminar_borra_estado_y_log_pero_no_las_en_curso(tmp_path, monkeypatch):
    import pytest

    monkeypatch.setattr(ejecuciones, "DIR", tmp_path)
    for id_, estado in [("a1", "ok"), ("a2", "error"), ("a3", "ejecutando")]:
        _guardar_ejecucion(id_, estado)
    with pytest.raises(ValueError, match="a3"):
        ejecuciones.eliminar(["a1", "a3"])                      # una en curso: no se borra ninguna
    assert {x.id for x in ejecuciones.historial()} == {"a1", "a2", "a3"}
    assert ejecuciones.eliminar(["a1", "a2", "a2"]) == 2
    assert [x.id for x in ejecuciones.historial()] == ["a3"] and not (tmp_path / "a1.log").exists()
    with pytest.raises(KeyError):
        ejecuciones.eliminar(["a1"])
    with pytest.raises(KeyError):
        ejecuciones.eliminar(["../../.env"])


def test_historial_solo_vuelve_a_leer_lo_que_cambio(tmp_path, monkeypatch):
    import os

    from modulos.reportes.aplicacion.dto import Ejecucion

    monkeypatch.setattr(ejecuciones, "DIR", tmp_path)
    monkeypatch.setattr(ejecuciones, "_cache", {})
    leidas, leer = [], ejecuciones._leer
    monkeypatch.setattr(ejecuciones, "_leer", lambda id_: leidas.append(id_) or leer(id_))
    for i in range(2):
        ejecuciones._guardar(Ejecucion(id=f"e{i}", reporte="saca-tu-garra", argumentos=[], estado="ok", codigo=0, inicio=f"2026-10-0{i + 1}T10:00:00", fin=None))
    ejecuciones.historial()
    ejecuciones.historial()
    assert leidas == ["e0", "e1"]  # la segunda consulta salió del caché
    ruta = tmp_path / "e1.json"
    os.utime(ruta, ns=(ruta.stat().st_atime_ns, ruta.stat().st_mtime_ns + 10**9))
    ejecuciones.historial()
    assert leidas == ["e0", "e1", "e1"]
