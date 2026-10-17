"""Errores de negocio compartidos por todas las capas (el dominio no depende de ninguna librería ni de la infraestructura)."""

from __future__ import annotations


class ConfiguracionError(RuntimeError):
    """Falta configuración necesaria (p. ej. credenciales) o un valor configurado no es válido."""


class ErrorDatos(RuntimeError):
    """Resultado inválido (todo vacío, fecha fuera de corte…): nunca se presenta como vacío válido."""


class ErrorIntegracion(RuntimeError):
    """Falla de un servicio externo (Google, correo…) con un mensaje listo para mostrar a la persona."""



class PeticionInvalida(ValueError):
    """La petición no cumple una regla del reporte (fecha, confirmación, correo…)."""


class NoEncontrado(LookupError):
    """El reporte, archivo o ejecución pedido no existe."""
