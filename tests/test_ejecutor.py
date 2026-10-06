from datetime import date

import pandas as pd
import pytest

from reportes.comun import ejecutor
from reportes.comun.ejecutor import ErrorDatos, Hoja, ReporteLote
from reportes.comun.fechas import Cortes, meses_atras
from reportes.config import ConfiguracionError
from reportes.verificacion import Estado, Resultado
from reportes.tablas import Tabla

LOTE = ReporteLote("saca-tu-garra", "demo", "mensual", "slc", "select '@@F@@', '@@F_ISO@@', '@@F_ANT@@'", hojas=(Hoja("Datos", columna_fecha="f"),))


def test_cortes_y_tokens():
    c = Cortes.mensual(date(2026, 7, 31))
    assert c.aplicar(LOTE.sql) == "select '20260731', '2026-07-31', '20260630'"
    assert c.tokens()["@@F_INI@@"] == "20260701" and c.tokens()["@@F_MENOS3@@"] == "20260430"
    assert meses_atras(date(2026, 1, 31), 2) == date(2025, 11, 30)


def test_corte_mensual_debe_ser_fin_de_mes():
    with pytest.raises(ConfiguracionError):
        Cortes.mensual(date(2026, 7, 15))


def test_token_sin_resolver_falla():
    with pytest.raises(ConfiguracionError):
        Cortes(date(2026, 7, 31)).aplicar("select '@@X@@'")


def test_todo_vacio_es_error_que_nombra_el_comando():
    with pytest.raises(ErrorDatos, match="python main.py tablas saca-tu-garra"):
        ejecutor.validar_resultados(LOTE, [pd.DataFrame(columns=["f"])], Cortes(date(2026, 7, 31)))


def test_vacio_valido_no_es_error():
    ok = ReporteLote("saca-tu-garra", "d", "mensual", "slc", "x", vacio_valido=True)
    assert ejecutor.validar_resultados(ok, [pd.DataFrame()], Cortes(date(2026, 7, 31))) == []


def test_fecha_del_resultado_anterior_al_corte_es_error():
    df = pd.DataFrame({"f": [date(2026, 7, 29)]})
    with pytest.raises(ErrorDatos, match="desactualizada"):
        ejecutor.validar_resultados(LOTE, [df], Cortes(date(2026, 7, 31)))


def test_exporta_excel_con_hoja_control(tmp_path):
    df = pd.DataFrame({"f": [date(2026, 7, 31)], "v": [1]})
    t = Tabla("storage.com_act.hcda001", "historica", "HFECPRO", "confirmada")
    ruta = ejecutor.exportar_excel(LOTE, [df], Cortes(date(2026, 7, 31)), [Resultado(t, Estado.OK, date(2026, 7, 31))], [], tmp_path)
    hojas = pd.read_excel(ruta, sheet_name=None)
    assert set(hojas) == {"Datos", "Control"} and ruta.name == "SacaTuGarra_20260731.xlsx"
    assert "Tabla · storage.com_act.hcda001" in set(hojas["Control"]["Concepto"])


def _correr(monkeypatch, tmp_path, estados, resultados=None, extra=()):
    t = Tabla("storage.com_act.hcda001", "historica", "HFECPRO", "confirmada")
    monkeypatch.setattr(ejecutor, "DIR_OUTPUTS", tmp_path)
    monkeypatch.setattr(ejecutor, "verificar_reporte", lambda c, f: [Resultado(t, e, date(2026, 7, 29)) for e in estados])
    monkeypatch.setattr(ejecutor, "ejecutar_lote", lambda servidor, sql, base=None: resultados if resultados is not None else [pd.DataFrame({"f": [date(2026, 7, 31)]})])
    return ejecutor.correr(LOTE, ["--fecha-corte", "2026-07-31", "--salida", str(tmp_path / "x"), *extra])


def test_tabla_desactualizada_no_ejecuta_y_deja_solicitud(monkeypatch, tmp_path, capsys):
    llamado = []
    monkeypatch.setattr(ejecutor, "ejecutar_lote", lambda *a: llamado.append(1))
    rc = _correr(monkeypatch, tmp_path, [Estado.DESACTUALIZADA])
    assert rc == ejecutor.SALIDA_TABLAS
    assert (tmp_path / "solicitudes" / "solicitud_saca-tu-garra_20260731.txt").exists()
    assert "storage.com_act.hcda001" in capsys.readouterr().out


def test_todo_ok_exporta(monkeypatch, tmp_path):
    assert _correr(monkeypatch, tmp_path, [Estado.OK]) == ejecutor.SALIDA_OK
    assert (tmp_path / "x" / "SacaTuGarra_20260731.xlsx").exists()


def test_forzar_ejecuta_y_lo_anota(monkeypatch, tmp_path):
    assert _correr(monkeypatch, tmp_path, [Estado.DESACTUALIZADA], extra=["--forzar"]) == ejecutor.SALIDA_OK


def test_escritura_exige_confirmacion(monkeypatch, tmp_path, capsys):
    import dataclasses

    escribe = dataclasses.replace(LOTE, escribe_en_bd=True)
    assert ejecutor.correr(escribe, ["--fecha-corte", "2026-07-31"]) == ejecutor.SALIDA_CONFIG
    assert "--confirmar-escritura" in capsys.readouterr().out
