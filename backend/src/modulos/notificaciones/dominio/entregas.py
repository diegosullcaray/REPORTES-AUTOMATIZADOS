"""A quién se entregan los archivos de un reporte: nombres de las variables del .env y validación de correos.

Ninguna dirección va en el código: cada lista vive en el .env y se edita desde la web (pestañas General y Correo de cada reporte,
y pantalla de cada responsable en Validación). Aquí solo está la regla; el valor lo da el puerto de entorno.
"""

from __future__ import annotations

import re

REMITENTE_DEFECTO = "Sistemas de Información de Gestión"
CORREO_PRUEBA_DEFECTO = "diego.sullcaray@confianza.pe"

CORREO = re.compile(r"^[^@\s,]+@[^@\s,]+\.[^@\s,]+$")


def _clave(reporte: str) -> str:
    return re.sub(r"[^A-Z0-9]", "_", reporte.upper())


def variable_chat(reporte: str) -> str:
    """Destinatarios del archivo por Google Chat: ENTREGA_CHAT_<REPORTE> (también «validacion-<grupo>» para el mensaje de tablas)."""
    return "ENTREGA_CHAT_" + _clave(reporte)


def variable_correo_para(reporte: str) -> str:
    return "ENTREGA_CORREO_PARA_" + _clave(reporte)


def variable_correo_cc(reporte: str) -> str:
    return "ENTREGA_CORREO_CC_" + _clave(reporte)


def correos_validos(texto: str) -> list[str]:
    """Los correos válidos de una lista separada por comas (los demás se ignoran)."""
    return [c.strip() for c in texto.split(",") if CORREO.match(c.strip())]
