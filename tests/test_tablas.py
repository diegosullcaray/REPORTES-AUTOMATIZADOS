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
