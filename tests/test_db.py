from reportes.db import _columnas_unicas, partir_lotes


def test_partir_lotes_por_go():
    assert [b.strip() for b in partir_lotes("use a\nGO\nselect 1\n go -- x\nselect 2")] == ["use a", "select 1", "select 2"]


def test_go_dentro_de_palabra_no_parte():
    assert len(partir_lotes("select 1\nGOTO x")) == 1


def test_columnas_sin_nombre_y_repetidas():
    assert _columnas_unicas(["", "a", "a", ""]) == ["col1", "a", "a_2", "col4"]
