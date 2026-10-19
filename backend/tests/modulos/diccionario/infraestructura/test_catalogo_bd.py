"""Catálogo desde mod_rep.rep.RREGREP01: solo lectura con NOLOCK, caché breve y la falla también se recuerda (sin VPN no se espera cada vez)."""

import pandas as pd
import pytest

from modulos.diccionario.infraestructura import catalogo_bd
from modulos.diccionario.infraestructura.catalogo_bd import reporte_de_fila


@pytest.fixture(autouse=True)
def limpio(monkeypatch):
    monkeypatch.setattr(catalogo_bd, "_cache", None)


def test_lee_la_tabla_con_un_select_nolock_en_mod_rep(monkeypatch):
    llamadas = []

    def leer_sql(servidor, consulta, params=None, base=None, timeout=None):
        llamadas.append((servidor, consulta, base, timeout))
        return pd.DataFrame({"RCODREP": ["A_01"], "RDESREP": ["Reporte A"], "RTPREP": ['{"name":"mod_rep.com.SPA","params":[{"order":1,"name":"fec"}]}']})

    monkeypatch.setattr(catalogo_bd.bd, "leer_sql", leer_sql)
    assert catalogo_bd.leer() == [{"codigo": "A_01", "descripcion": "Reporte A", "procedimiento": "mod_rep.com.SPA", "parametros": ["fec"]}]
    catalogo_bd.leer()
    assert len(llamadas) == 1                                   # la segunda lectura sale de la caché
    servidor, consulta, base, timeout = llamadas[0]
    assert (servidor, base) == ("mish", "mod_rep") and timeout == catalogo_bd.TIMEOUT
    assert consulta.upper().startswith("SELECT") and "NOLOCK" in consulta and "RREGREP01" in consulta
    assert not any(p in consulta.upper() for p in ("INSERT", "UPDATE", "DELETE", "EXEC"))


def test_la_falla_se_recuerda_para_no_esperar_en_cada_pantalla(monkeypatch):
    llamadas = []

    def sin_vpn(*a, **k):
        llamadas.append(1)
        raise OSError("08001")

    monkeypatch.setattr(catalogo_bd.bd, "leer_sql", sin_vpn)
    for _ in range(3):
        with pytest.raises(OSError):
            catalogo_bd.leer()
    assert len(llamadas) == 1


RTPREP = '{"name":"mod_rep.com.RTABSEG01","params":[{"order":3,"name":"fec"},{"order":1,"name":"tip_cod"},{"order":2,"name":"cod_rel"}]}'


def test_lee_el_procedimiento_y_ordena_los_parametros():
    assert reporte_de_fila(" TAB_SEG_01 ", "Tablero de Seguimiento ", RTPREP) == {
        "codigo": "TAB_SEG_01", "descripcion": "Tablero de Seguimiento", "procedimiento": "mod_rep.com.RTABSEG01", "parametros": ["tip_cod", "cod_rel", "fec"]}


@pytest.mark.parametrize("rtprep", [None, "", "no es json", "[1, 2]", '{"name": "x", "params": [{"sin_nombre": 1}]}'])
def test_un_rtprep_ilegible_deja_el_reporte_sin_procedimiento(rtprep):
    assert reporte_de_fila("X", None, rtprep) == {"codigo": "X", "descripcion": "", "procedimiento": "", "parametros": []}


def test_forzar_salta_la_cache_incluida_la_falla(monkeypatch):
    estado = {"vpn": False}

    def leer_sql(*a, **k):
        if not estado["vpn"]:
            raise OSError("08001")
        return pd.DataFrame({"RCODREP": ["A"], "RDESREP": ["a"], "RTPREP": ['{"name":"mod_rep.com.SPA"}']})

    monkeypatch.setattr(catalogo_bd.bd, "leer_sql", leer_sql)
    with pytest.raises(OSError):
        catalogo_bd.leer()
    estado["vpn"] = True
    with pytest.raises(OSError):
        catalogo_bd.leer()                                      # sigue la falla recordada
    assert len(catalogo_bd.leer(forzar=True)) == 1


def test_si_la_mayoria_no_trae_procedimiento_es_un_error_no_un_catalogo_vacio(monkeypatch):
    df = pd.DataFrame({"RCODREP": ["A", "B", "C"], "RDESREP": ["a", "b", "c"], "RTPREP": ["no es json", None, '{"name":"mod_rep.com.SPC"}']})
    monkeypatch.setattr(catalogo_bd.bd, "leer_sql", lambda *a, **k: df)
    with pytest.raises(ValueError, match="¿cambió el formato"):
        catalogo_bd.leer()


def test_los_nombres_con_corchetes_se_leen_sin_ellos():
    r = reporte_de_fila("R1", "x", '{"name":"[mod_rep].[com].[SP_X]","params":[]}')
    assert r["procedimiento"] == "mod_rep.com.SP_X"
