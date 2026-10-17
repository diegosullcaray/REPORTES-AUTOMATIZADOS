"""Errores compartidos (core/excepciones.py): negocio, integraciones y los que la interfaz traduce a 422 y 404."""

from core.excepciones import ConfiguracionError, ErrorDatos, ErrorIntegracion, NoEncontrado, PeticionInvalida
from modulos.notificaciones.infraestructura import correo_smtp
from modulos.integraciones.infraestructura.google import cliente


def test_son_errores_de_ejecucion_distinguibles():
    assert issubclass(ConfiguracionError, RuntimeError) and issubclass(ErrorDatos, RuntimeError)
    assert not issubclass(ErrorDatos, ConfiguracionError)


def test_los_fallos_de_servicios_externos_son_errores_de_integracion():
    """La aplicación captura ErrorIntegracion sin conocer a Google ni al SMTP."""
    assert issubclass(cliente.GoogleError, ErrorIntegracion)
    assert issubclass(correo_smtp.CorreoError, ErrorIntegracion)


def test_tipos_base_para_traducirlos_en_la_interfaz():
    assert issubclass(PeticionInvalida, ValueError) and issubclass(NoEncontrado, LookupError)
    assert not issubclass(PeticionInvalida, LookupError)
