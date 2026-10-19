"""Raíz de composición: crea los adaptadores reales de cada módulo y los conecta a sus puertos.

Es el único lugar que conoce a la vez la aplicación y la infraestructura de todos los módulos. La API web, la consola y el servidor MCP
lo importan al arrancar; las pruebas registran dobles con el `registrar(...)` de cada registro de puertos.
"""

from __future__ import annotations

from core import bd, entorno
from core.puertos import Nucleo, nucleo
from modulos.diccionario.aplicacion.puertos import Puertos as PuertosDiccionario
from modulos.diccionario.aplicacion.puertos import puertos as puertos_diccionario
from modulos.diccionario.infraestructura import catalogo_bd, lanzador, lector
from modulos.integraciones.aplicacion.puertos import Puertos as PuertosIntegraciones
from modulos.integraciones.aplicacion.puertos import puertos as puertos_integraciones
from modulos.integraciones.infraestructura.google import cliente as google
from modulos.integraciones.infraestructura.ia import cliente as ia
from modulos.notificaciones.aplicacion.puertos import Puertos as PuertosNotificaciones
from modulos.notificaciones.aplicacion.puertos import puertos as puertos_notificaciones
from modulos.notificaciones.infraestructura import correo_smtp
from modulos.reportes.aplicacion.puertos import Puertos as PuertosReportes
from modulos.reportes.aplicacion.puertos import puertos as puertos_reportes
from modulos.reportes.infraestructura import cola_ejecuciones, excel, historial_validacion, etiquetas, lector_archivos

# los adaptadores se crean la primera vez que algún caso de uso los pide
nucleo.fabrica = lambda: Nucleo(bd=bd, entorno=entorno)
puertos_reportes.fabrica = lambda: PuertosReportes(excel=excel, cola=cola_ejecuciones, historial_validacion=historial_validacion, lector_archivos=lector_archivos, etiquetas=etiquetas)
puertos_notificaciones.fabrica = lambda: PuertosNotificaciones(correo=correo_smtp)
puertos_integraciones.fabrica = lambda: PuertosIntegraciones(google=google, ia=ia)
puertos_diccionario.fabrica = lambda: PuertosDiccionario(lector=lector, lanzador=lanzador, catalogo=catalogo_bd)
