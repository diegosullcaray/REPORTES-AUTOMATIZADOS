import pytest

from reportes import config


def test_hay_exactamente_tres_bases():
    assert set(config.BASES) == {"dw_raw", "rcc", "slc"}


def test_cadena_con_credenciales_escapa_llaves(monkeypatch):
    monkeypatch.setenv("RCC_USER", "u")
    monkeypatch.setenv("RCC_PASSWORD", "a}b")
    cadena = config.obtener_base("rcc").cadena_odbc()
    assert "UID=u" in cadena and "PWD={a}}b}" in cadena


def test_base_sql_sin_credenciales_falla(monkeypatch):
    monkeypatch.delenv("RCC_USER", raising=False)
    monkeypatch.delenv("RCC_PASSWORD", raising=False)
    with pytest.raises(config.ConfiguracionError):
        config.obtener_base("rcc").cadena_odbc()


def test_slc_usa_autenticacion_windows_por_defecto(monkeypatch):
    monkeypatch.delenv("SLC_USER", raising=False)
    monkeypatch.delenv("SLC_PASSWORD", raising=False)
    assert "Trusted_Connection=yes" in config.obtener_base("slc").cadena_odbc()


def test_usuario_sin_clave_es_error(monkeypatch):
    monkeypatch.setenv("SLC_USER", "solo_usuario")
    monkeypatch.delenv("SLC_PASSWORD", raising=False)
    with pytest.raises(config.ConfiguracionError):
        config.obtener_base("slc").cadena_odbc()


def test_base_desconocida():
    with pytest.raises(config.ConfiguracionError):
        config.obtener_base("otra")
