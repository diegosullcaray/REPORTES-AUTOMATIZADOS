"""Fechas de corte y tokens del T-SQL (dominio/fechas.py): reglas puras, sin leer el .env."""

from datetime import date

import pytest

from core.excepciones import ConfiguracionError
from modulos.reportes.dominio.fechas import Cortes, corte_desde_texto, dia_anterior_habil_simple, meses_atras, resolver_corte

SQL = "select '@@F@@', '@@F_ISO@@', '@@F_ANT@@'"


def test_cortes_y_tokens():
    c = Cortes.mensual(date(2026, 7, 31))
    assert c.aplicar(SQL) == "select '20260731', '2026-07-31', '20260630'"
    assert c.tokens()["@@F_INI@@"] == "20260701" and c.tokens()["@@F_MENOS3@@"] == "20260430"
    assert meses_atras(date(2026, 1, 31), 2) == date(2025, 11, 30)


def test_corte_mensual_debe_ser_fin_de_mes():
    with pytest.raises(ConfiguracionError):
        Cortes.mensual(date(2026, 7, 15))


def test_token_sin_resolver_falla():
    with pytest.raises(ConfiguracionError):
        Cortes(date(2026, 7, 31)).aplicar("select '@@X@@'")


def test_prioridad_del_corte_es_argumento_env_y_dia_anterior():
    assert resolver_corte("mensual", date(2026, 8, 31), en_env=date(2026, 9, 30)) == (date(2026, 8, 31), "--fecha-corte")
    assert resolver_corte("mensual", en_env=date(2026, 9, 30)) == (date(2026, 9, 30), ".env (FECHA_CORTE_MENSUAL)")
    assert resolver_corte("diaria", hoy=date(2026, 10, 5))[0] == date(2026, 10, 3)       # lunes -> sábado
    assert resolver_corte("diaria", hoy=date(2026, 10, 5), lunes_sabado=False)[0] == date(2026, 10, 4)
    with pytest.raises(ConfiguracionError, match="FECHA_CORTE_MENSUAL"):
        resolver_corte("mensual")


def test_texto_del_env_se_valida_sin_tocar_el_entorno():
    assert corte_desde_texto("mensual", " 2026-09-30 ") == date(2026, 9, 30)
    assert corte_desde_texto("mensual", "  ") is None
    with pytest.raises(ConfiguracionError, match="FECHA_CORTE_DIARIA"):
        corte_desde_texto("diaria", "30/09/2026")


def test_dia_anterior():
    assert dia_anterior_habil_simple(date(2026, 10, 7)) == date(2026, 10, 6)
