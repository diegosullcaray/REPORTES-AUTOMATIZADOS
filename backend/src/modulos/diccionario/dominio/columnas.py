"""Reglas puras del diccionario: qué columnas parecen de fecha y qué procesos del repo DICCIONARIO se pueden lanzar desde la web."""

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
    comando: tuple[str, ...]      # se ejecuta en la carpeta del repo DICCIONARIO; sin shell, así que nada del pedido entra al comando
    escribe: str                  # qué archivos toca (para que la persona sepa qué va a cambiar)


PROCESOS: dict[str, Proceso] = {p.id: p for p in (
    Proceso("generar", "Regenerar el diccionario", "Regenera SQL, diccionario, errores y copias de agentes desde la fuente. No se conecta a la base.",
            ("npm", "run", "generar"), "diccionario/, errores/, extraccion/sql/ y .claude/ del repo DICCIONARIO"),
    Proceso("verificar", "Verificar la calidad", "Falla ante errores nuevos o algo viejo, roto o inconsistente. Solo lee.",
            ("npm", "run", "verificar"), "nada"),
    Proceso("test", "Probar el analizador T-SQL", "Corre las pruebas del analizador de procedimientos. Solo lee.",
            ("npm", "test"), "nada"),
)}
