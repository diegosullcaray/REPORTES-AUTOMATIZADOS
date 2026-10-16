"""Errores de los casos de uso: la capa HTTP los traduce a 422 y 404, la consola a un mensaje."""

from __future__ import annotations


class PeticionInvalida(ValueError):
    """La petición no cumple una regla del reporte (fecha, confirmación, correo…)."""


class NoEncontrado(LookupError):
    """El reporte, archivo o ejecución pedido no existe."""
