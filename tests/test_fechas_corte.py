from datetime import date

import pytest

from reportes.comun import ejecutor
from reportes.comun.fechas import resolver_corte
from reportes.config import ConfiguracionError


@pytest.fixture(autouse=True)
def sin_env(monkeypatch):
    monkeypatch.delenv("FECHA_CORTE_DIARIA", raising=False)
    monkeypatch.delenv("FECHA_CORTE_MENSUAL", raising=False)


def test_mensual_toma_la_fecha_del_env(monkeypatch):
    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "2026-09-30")
    assert resolver_corte("mensual") == (date(2026, 9, 30), ".env (FECHA_CORTE_MENSUAL)")


def test_diaria_toma_la_fecha_del_env(monkeypatch):
    monkeypatch.setenv("FECHA_CORTE_DIARIA", "2026-10-02")
    assert resolver_corte("diaria")[0] == date(2026, 10, 2)


def test_el_argumento_manda_sobre_el_env(monkeypatch):
    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "2026-09-30")
    assert resolver_corte("mensual", date(2026, 8, 31)) == (date(2026, 8, 31), "--fecha-corte")


def test_diaria_sin_nada_usa_dia_anterior_y_lunes_sabado():
    assert resolver_corte("diaria", hoy=date(2026, 10, 5))[0] == date(2026, 10, 3)  # lunes
    assert resolver_corte("diaria", hoy=date(2026, 10, 7))[0] == date(2026, 10, 6)


def test_mensual_sin_fecha_es_error_que_explica_el_env():
    with pytest.raises(ConfiguracionError, match="FECHA_CORTE_MENSUAL"):
        resolver_corte("mensual")


def test_valor_invalido_en_env(monkeypatch):
    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "30/09/2026")
    with pytest.raises(ConfiguracionError, match="FECHA_CORTE_MENSUAL"):
        resolver_corte("mensual")


def test_vacio_en_env_equivale_a_no_definido(monkeypatch):
    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "  ")
    with pytest.raises(ConfiguracionError):
        resolver_corte("mensual")


def test_reporte_de_lote_usa_la_fecha_del_env(monkeypatch, tmp_path, capsys):
    import pandas as pd

    from reportes.comun.ejecutor import ReporteLote
    from reportes.verificacion import Estado, Resultado
    from reportes.tablas import Tabla

    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "2026-09-30")
    t = Tabla("storage.com_act.hcda001", "slc", "historica", "HFECPRO", "confirmada")
    monkeypatch.setattr(ejecutor, "DIR_OUTPUTS", tmp_path)
    monkeypatch.setattr(ejecutor, "verificar_reporte", lambda c, f: [Resultado(t, Estado.OK, f)])
    llamadas = []
    monkeypatch.setattr(ejecutor, "ejecutar_lote", lambda s, sql, base=None: llamadas.append(sql) or [pd.DataFrame({"x": [1]})])
    lote = ReporteLote("saca-tu-garra", "demo", "mensual", "slc", "select '@@F@@'")
    assert ejecutor.correr(lote, ["--salida", str(tmp_path / "x")]) == ejecutor.SALIDA_OK   # sin --fecha-corte
    assert llamadas == ["select '20260930'"]
    assert ".env (FECHA_CORTE_MENSUAL)" in capsys.readouterr().out


def test_reporte_mensual_sin_fecha_ni_env_sale_con_error_de_configuracion(capsys):
    from reportes.comun.ejecutor import ReporteLote

    assert ejecutor.correr(ReporteLote("saca-tu-garra", "d", "mensual", "slc", "x"), []) == ejecutor.SALIDA_CONFIG
    assert "FECHA_CORTE_MENSUAL" in capsys.readouterr().out


def test_reportes_con_cli_propio_toman_la_fecha_del_env(monkeypatch):
    from reportes.mensuales import bancarizados, bancarizados_producto, clientes_extranjeros, indicadores_clientes

    monkeypatch.setenv("FECHA_CORTE_MENSUAL", "2026-09-30")
    assert bancarizados.parsear_argumentos([]).fecha_corte == date(2026, 9, 30)
    assert clientes_extranjeros.parsear_argumentos([]).fecha_corte == date(2026, 9, 30)
    assert [str(m) for m in bancarizados_producto.parsear_argumentos([]).mes] == ["2026-09"]
    assert str(indicadores_clientes.parsear_argumentos([]).mes) == "2026-09"
    assert bancarizados.parsear_argumentos(["--fecha-corte", "2026-08-31"]).fecha_corte == date(2026, 8, 31)


def test_cli_propio_sin_fecha_ni_env_pide_el_env(capsys):
    from reportes.mensuales import bancarizados

    with pytest.raises(SystemExit):
        bancarizados.parsear_argumentos([])
    assert "FECHA_CORTE_MENSUAL" in capsys.readouterr().err
