from reportes.db import cargar_sql


def test_cargar_sql_lee_archivo_versionado():
    assert "RECAUDO_DIARIO_FINANZAS" in cargar_sql("diarias/cmg_mora/p002_01_recaudo.sql")
