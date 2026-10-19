"""Candado del registro editable (reportes, grupos y etiquetas): cada operación lee y reescribe archivos, así que van de a una."""

from __future__ import annotations

import functools
import threading

_CANDADO = threading.RLock()  # reentrante: crear un grupo asigna sus etiquetas dentro de la misma operación


def exclusivo(f):
    @functools.wraps(f)
    def envuelta(*a, **k):
        with _CANDADO:
            return f(*a, **k)
    return envuelta
