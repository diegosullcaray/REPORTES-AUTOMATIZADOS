import pytest

from reportes import config


def test_hay_exactamente_tres_servidores():
    assert set(config.SERVIDORES) == {"mish", "slc", "rcc"}


def test_cadena_con_credenciales_escapa_llaves(monkeypatch):
    monkeypatch.setenv("RCC_USER", "u")
    monkeypatch.setenv("RCC_PASSWORD", "a}b")
    cadena = config.obtener_servidor("rcc").cadena_odbc()
    assert "UID=u" in cadena and "PWD={a}}b}" in cadena


def test_servidor_sql_sin_credenciales_falla(monkeypatch):
    monkeypatch.delenv("RCC_USER", raising=False)
    monkeypatch.delenv("RCC_PASSWORD", raising=False)
    with pytest.raises(config.ConfiguracionError):
        config.obtener_servidor("rcc").cadena_odbc()


@pytest.mark.parametrize("nombre,pref", [("slc", "SLC"), ("mish", "MISH")])
def test_servidores_windows_por_defecto(monkeypatch, nombre, pref):
    monkeypatch.delenv(f"{pref}_USER", raising=False)
    monkeypatch.delenv(f"{pref}_PASSWORD", raising=False)
    assert "Trusted_Connection=yes" in config.obtener_servidor(nombre).cadena_odbc()


def test_usuario_sin_clave_es_error(monkeypatch):
    monkeypatch.setenv("SLC_USER", "solo_usuario")
    monkeypatch.delenv("SLC_PASSWORD", raising=False)
    with pytest.raises(config.ConfiguracionError):
        config.obtener_servidor("slc").cadena_odbc()


def test_servidor_desconocido():
    with pytest.raises(config.ConfiguracionError):
        config.obtener_servidor("otra")


def test_la_base_de_datos_la_elige_cada_reporte(monkeypatch):
    monkeypatch.delenv("RCC_DATABASE", raising=False)
    monkeypatch.setenv("RCC_USER", "u")
    monkeypatch.setenv("RCC_PASSWORD", "p")
    rcc = config.obtener_servidor("rcc")
    assert "DATABASE" not in rcc.cadena_odbc()                      # el .env no fija ninguna base
    assert "DATABASE=DBRCC" in rcc.cadena_odbc("DBRCC")             # un reporte pide DBRCC
    assert "DATABASE=DW_Raw_v2" in rcc.cadena_odbc("DW_Raw_v2")     # otro reporte, otra base, mismo servidor


def test_base_del_reporte_manda_sobre_la_del_env(monkeypatch):
    monkeypatch.setenv("SLC_DATABASE", "slc")
    assert "DATABASE=storage" in config.obtener_servidor("slc").cadena_odbc("storage")
    assert "DATABASE=slc" in config.obtener_servidor("slc").cadena_odbc()
