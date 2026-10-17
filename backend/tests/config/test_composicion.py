"""Raíz de composición (config/composicion.py): conecta los adaptadores reales de cada módulo a sus puertos."""

from config import composicion  # noqa: F401
from core.puertos import nucleo
from modulos.integraciones.aplicacion.puertos import puertos as integraciones
from modulos.notificaciones.aplicacion.puertos import puertos as notificaciones
from modulos.reportes.aplicacion.puertos import puertos as reportes


def test_cada_modulo_obtiene_sus_adaptadores_reales():
    assert nucleo().bd.__name__ == "core.bd" and nucleo().entorno.__name__ == "core.entorno"
    assert callable(reportes().cola.encolar) and callable(reportes().excel.guardar_libro) and callable(reportes().lector_archivos.hojas_excel)
    assert reportes().cola.__name__.endswith("cola_ejecuciones") and reportes().historial_validacion.__name__.endswith("historial_validacion")
    assert callable(notificaciones().correo.enviar) and callable(integraciones().google.token_de_acceso)
    assert integraciones().google.__name__.endswith("google.cliente")
