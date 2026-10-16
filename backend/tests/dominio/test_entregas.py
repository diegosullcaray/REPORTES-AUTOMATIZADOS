"""A quién se entrega (dominio/entregas.py): nombres de las variables del .env y validación de correos, sin red."""

from dominio import entregas


def test_variables_por_reporte():
    assert entregas.variable_chat("cmg-mora") == "ENTREGA_CHAT_CMG_MORA"
    assert entregas.variable_chat("validacion-piero") == "ENTREGA_CHAT_VALIDACION_PIERO"
    assert entregas.variable_correo_para("cmg-mora") == "ENTREGA_CORREO_PARA_CMG_MORA"
    assert entregas.variable_correo_cc("cmg-mora") == "ENTREGA_CORREO_CC_CMG_MORA"


def test_solo_se_aceptan_correos_validos():
    assert entregas.correos_validos(" ana@x.pe , no-es-correo,luis@x.pe") == ["ana@x.pe", "luis@x.pe"]
    assert entregas.correos_validos("") == []
