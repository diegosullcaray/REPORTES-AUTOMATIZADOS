"""Reglas puras del diccionario: qué columnas parecen de fecha y qué procesos del diccionario se pueden lanzar desde la web."""

from __future__ import annotations

import re
from dataclasses import dataclass

_FECHA = re.compile(r"fec|fch|date|periodo|(^|_)dia($|_)", re.I)


def es_columna_fecha(nombre: str) -> bool:
    """Heurística por el nombre (HFECPRO, FECHA_CIERRE, FC_DIA…). Sugiere; quien decide es la persona que confirma en tablas.py."""
    return bool(_FECHA.search(nombre))


@dataclass(frozen=True)
class Proceso:
    id: str
    nombre: str
    descripcion: str
    comando: tuple[str, ...]      # lo que ejecuta, para mostrarlo: los procesos corren dentro de la API y nada del pedido entra a ellos
    escribe: str                  # qué toca (para que la persona sepa qué va a cambiar)


PROCESOS: dict[str, Proceso] = {p.id: p for p in (
    Proceso("construir", "Generar el diccionario desde la base", "Lee el catálogo de reportes (mod_rep.rep.RREGREP01) y, de cada base, las dependencias de sus procedimientos, su código (que analiza) y la estructura de las tablas. Solo lee metadatos y definiciones.",
            ("mod_rep.rep.RREGREP01 + sys.dm_sql_referenced_entities + sys.sql_modules + INFORMATION_SCHEMA",), "data/outputs/diccionario/generado/diccionario.json (de esta app)"),
    Proceso("bases", "Validar las bases de datos", "Prueba la conexión a cada servidor SQL (mish, slc, rcc) y que cada base que usan los reportes esté en línea. Solo lee.",
            ("SELECT name, state_desc FROM sys.databases",), "nada"),
)}
