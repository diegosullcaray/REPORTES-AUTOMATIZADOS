"""Alta de reportes desde la web: validaciones del T-SQL y texto que se genera."""

import pytest

from core.excepciones import PeticionInvalida
from modulos.reportes.aplicacion import nuevo_reporte as nr

SQL = "use storage;\ngo\nselect * from storage.com_act.hcda001 a join [storage].[ref].[rcalen001] b on 1=1 where a.hfecpro='@@F@@'"


def test_tablas_de_3_partes_en_minusculas_y_sin_comentarios():
    sql = SQL + "\n-- from storage.x.comentada\n/* join storage.y.otra */"
    assert nr.tablas_de_sql(sql) == ["storage.com_act.hcda001", "storage.ref.rcalen001"]


def test_sql_valido_devuelve_sus_tablas():
    assert nr.validar_sql(SQL, "mensual", "mish") == ["storage.com_act.hcda001", "storage.ref.rcalen001"]


@pytest.mark.parametrize("sql,frag", [
    ("  ", "Pega"),
    ("select 1 from storage.a.b where f='20260731'", "fecha literal"),
    ("select 1 from storage.a.b where f='@@NOPE@@'", "no existe"),
    ("select 1 from storage.a.b", "ningún token"),
    ('select """ @@F@@', '"""'),
])
def test_sql_invalido(sql, frag):
    with pytest.raises(PeticionInvalida, match=frag):
        nr.validar_sql(sql, "mensual", "mish")


def test_rechaza_tablas_de_otro_servidor():
    with pytest.raises(PeticionInvalida, match="otro"):
        nr.validar_sql(SQL, "mensual", "slc")


@pytest.mark.parametrize("nombre,orden", [("Mal Nombre", "07"), ("ok", "7"), ("ok", "07.")])
def test_identidad_invalida(nombre, orden):
    with pytest.raises(PeticionInvalida):
        nr.validar_identidad(nombre, orden)


@pytest.mark.parametrize("nombre,id_", [("Cierre de Riesgos", "cierre-de-riesgos"), ("  Gestión  Crédito ", "gestion-credito")])
def test_id_de_grupo(nombre, id_):
    assert nr.id_de_grupo(nombre) == id_


@pytest.mark.parametrize("nombre", ["", "###", 'con "comillas"', "a#b"])
def test_id_de_grupo_invalido(nombre):
    with pytest.raises(PeticionInvalida):
        nr.id_de_grupo(nombre)


def test_insertar_grupo():
    texto = "x = 1\n_GRUPOS_EXTRA: list[tuple[str, str, str]] = [\n]\n"
    assert "    ('cierre', 'Cierre', 'mensual'),\n]" in nr.insertar_grupo(texto, "cierre", "Cierre", "mensual")
    with pytest.raises(PeticionInvalida):
        nr.insertar_grupo("sin ancla", "a", "A", "diaria")


def test_rutas_siguen_el_orden_del_legado():
    assert nr.rutas("piero", "mensual", "10.1", "mi-reporte", None) == (
        "modulos.reportes.catalogo.mensuales.piero.r10_1_mi_reporte",
        "modulos/reportes/catalogo/mensuales/piero/r10_1_mi_reporte.py",
        "mensuales/piero/10_mi_reporte",
    )
    assert nr.rutas("diarias", "diaria", "05", "x", "diarias/05_otro")[2] == "diarias/05_otro"


def test_rutas_de_un_grupo_propio():
    assert nr.rutas("cierre-riesgos", "mensual", "01", "mi-reporte", None) == (
        "modulos.reportes.catalogo.grupos.cierre_riesgos.r01_mi_reporte",
        "modulos/reportes/catalogo/grupos/cierre_riesgos/r01_mi_reporte.py",
        "mensuales/cierre_riesgos/01_mi_reporte",
    )


def test_modulo_y_test_generados_compilan_y_el_modulo_declara_el_lote():
    modulo = nr.render_modulo("mi-reporte", "Mi reporte: «prueba»", "mensual", "mish", "storage", SQL)
    compile(modulo, "m", "exec")
    assert "comando='mi-reporte'" in modulo and "def main(argv" in modulo
    compile(nr.render_test("mi-reporte", "modulos.reportes.catalogo.mensuales.piero.r10_mi_reporte", "mensual"), "t", "exec")
