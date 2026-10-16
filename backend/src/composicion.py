"""Raíz de composición: crea los adaptadores reales y los conecta a los puertos de la aplicación.

Es el único lugar que conoce a la vez la aplicación y la infraestructura. La API web, la consola y el servidor MCP lo importan
al arrancar; las pruebas registran dobles con `aplicacion.puertos.registrar(...)`.
"""

from __future__ import annotations

import aplicacion.puertos as _puertos
from infraestructura import bd, cola_ejecuciones, correo_smtp, entorno, excel, historial_validacion, lector_archivos
from infraestructura.google import cliente as google


def construir() -> _puertos.Puertos:
    return _puertos.Puertos(bd=bd, entorno=entorno, excel=excel, cola=cola_ejecuciones, historial_validacion=historial_validacion,
                            lector_archivos=lector_archivos, correo=correo_smtp, google=google)


_puertos.fabrica = construir  # los puertos se crean la primera vez que algún caso de uso los pide
