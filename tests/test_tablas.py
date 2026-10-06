from reportes.config import SERVIDORES
from reportes.tablas import TABLAS, USO, reportes_que_usan, tablas_de


def test_todo_uso_apunta_a_una_tabla_registrada():
    for reporte, nombres in USO.items():
        for n in nombres:
            assert n in TABLAS, f"{reporte}: {n}"


def test_alias_validos_y_columna_si_es_verificable():
    for t in TABLAS.values():
        assert t.servidor in SERVIDORES
        if t.tipo in {"historica", "stock"}:
            assert t.col_fecha, t.nombre


def test_consulta_inversa_tabla_a_reportes():
    assert "saca-tu-garra" in reportes_que_usan("storage.com_act.hcda001")
    assert len(tablas_de("cmg-mora")) >= 5


def test_clientes_extranjeros_declara_su_tabla_de_pasivos_del_cierre():
    nombres = set(USO["clientes-extranjeros"])
    assert "rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}" in nombres      # por defecto: linked server desde slc
    assert "db{yyyymm}.dbo.ccp{yyyymmdd}" in nombres             # con --pasivos-directo: servidor rcc
    assert TABLAS["rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}"].servidor == "slc"
    assert TABLAS["db{yyyymm}.dbo.ccp{yyyymmdd}"].servidor == "rcc"


def test_toda_tabla_registrada_la_usa_algun_reporte():
    usadas = set().union(*map(set, USO.values()))
    assert set(TABLAS) <= usadas, sorted(set(TABLAS) - usadas)
