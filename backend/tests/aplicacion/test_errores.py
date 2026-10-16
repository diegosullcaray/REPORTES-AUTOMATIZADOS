"""Errores de los casos de uso (aplicacion/errores.py): la capa HTTP los traduce a 422 y 404."""

from aplicacion.errores import NoEncontrado, PeticionInvalida


def test_tipos_base_para_traducirlos_en_la_interfaz():
    assert issubclass(PeticionInvalida, ValueError) and issubclass(NoEncontrado, LookupError)
    assert not issubclass(PeticionInvalida, LookupError)
