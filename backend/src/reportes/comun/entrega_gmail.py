"""Destinatarios del correo de cada reporte, en el .env: `ENTREGA_CORREO_PARA_<REPORTE>` y `ENTREGA_CORREO_CC_<REPORTE>`
(correos separados por coma). Se editan en la pestaña Correo del reporte; ninguna dirección va en el código."""

from __future__ import annotations

import os
import re

from .entrega_chat import CORREO


def _clave(reporte: str) -> str:
    return re.sub(r"[^A-Z0-9]", "_", reporte.upper())


def variable_para(reporte: str) -> str:
    return "ENTREGA_CORREO_PARA_" + _clave(reporte)


def variable_cc(reporte: str) -> str:
    return "ENTREGA_CORREO_CC_" + _clave(reporte)


def _lista(variable: str) -> list[str]:
    return [c.strip() for c in os.getenv(variable, "").split(",") if CORREO.match(c.strip())]


def para(reporte: str) -> list[str]:
    return _lista(variable_para(reporte))


def cc(reporte: str) -> list[str]:
    return _lista(variable_cc(reporte))
