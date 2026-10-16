"""Errores de negocio compartidos (dominio/errores.py) y su jerarquía en las capas exteriores."""

from dominio.errores import ConfiguracionError, ErrorDatos, ErrorIntegracion
from infraestructura import correo_smtp
from infraestructura.google import cliente


def test_son_errores_de_ejecucion_distinguibles():
    assert issubclass(ConfiguracionError, RuntimeError) and issubclass(ErrorDatos, RuntimeError)
    assert not issubclass(ErrorDatos, ConfiguracionError)


def test_los_fallos_de_servicios_externos_son_errores_de_integracion():
    """La aplicación captura ErrorIntegracion sin conocer a Google ni al SMTP."""
    assert issubclass(cliente.GoogleError, ErrorIntegracion)
    assert issubclass(correo_smtp.CorreoError, ErrorIntegracion)
