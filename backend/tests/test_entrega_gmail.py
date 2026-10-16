"""Destinatarios del correo por reporte (reportes/comun/entrega_gmail.py): variables del .env, sin red."""

from reportes.comun import entrega_gmail


def test_variables_y_destinatarios(monkeypatch):
    assert entrega_gmail.variable_para("cmg-mora") == "ENTREGA_CORREO_PARA_CMG_MORA"
    assert entrega_gmail.variable_cc("cmg-mora") == "ENTREGA_CORREO_CC_CMG_MORA"
    monkeypatch.setenv("ENTREGA_CORREO_PARA_CMG_MORA", " ana@x.pe , no-es-correo,luis@x.pe")
    assert entrega_gmail.para("cmg-mora") == ["ana@x.pe", "luis@x.pe"]
    monkeypatch.delenv("ENTREGA_CORREO_CC_CMG_MORA", raising=False)
    assert entrega_gmail.cc("cmg-mora") == []
