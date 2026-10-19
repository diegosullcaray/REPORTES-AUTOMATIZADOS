"""Ajustes editables de la web: lo que se guarda en el .env se valida antes (sin tocar el archivo real)."""

import pytest

from core.excepciones import PeticionInvalida
from modulos.sistema.aplicacion.casos_uso import configuracion


@pytest.mark.parametrize("campo,valor,frag", [
    ("dir_inputs", "relativa/ruta", "ruta completa"),
    ("dir_outputs", "C:/datos # comentario", "no admite"),
    ("corte_mensual", "2999-12-31", "futuro"),
    ("corte_mensual", "2026-06-15", "fin de mes"),
])
def test_un_ajuste_invalido_se_rechaza_antes_de_guardarlo(campo, valor, frag):
    with pytest.raises(PeticionInvalida, match=frag):
        configuracion._validar_ajuste(campo, valor)


def test_un_ajuste_vacio_quita_la_variable():
    assert configuracion._validar_ajuste("corte_diario", "") == ""
