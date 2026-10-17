"""Contratos compartidos por todos los módulos. Solo forma de los datos: sin lógica."""

from __future__ import annotations

from pydantic import BaseModel


class PruebaNotificacion(BaseModel):
    ok: bool
    detalle: str
