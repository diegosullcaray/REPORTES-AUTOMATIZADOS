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
    npm: str | None = None        # script de package.json que corre: de ahí se muestra su código
    generados: tuple[str, ...] = ()   # patrones (relativos a la carpeta del repo) de los archivos que deja: se pueden ver desde la web


PROCESOS: dict[str, Proceso] = {p.id: p for p in (
    Proceso("construir", "Generar el diccionario desde la base", "Lee el catálogo de reportes (mod_rep.rep.RREGREP01) y, de cada base, las dependencias de sus procedimientos y la estructura de las tablas. No necesita el repo DICCIONARIO. Solo lee metadatos.",
            ("mod_rep.rep.RREGREP01 + sys.dm_sql_referenced_entities + INFORMATION_SCHEMA",), "data/outputs/diccionario/generado/diccionario.json (de esta app)"),
    Proceso("generar", "Regenerar el diccionario", "Con el repo DICCIONARIO: regenera SQL, diccionario, errores y copias de agentes desde su fuente. No se conecta a la base.",
            ("npm", "run", "generar"), "diccionario/, errores/, extraccion/sql/ y .claude/ del repo DICCIONARIO", npm="generar",
            generados=("diccionario/*.md", "diccionario/diccionario.json", "errores/*.md")),
    Proceso("verificar", "Verificar la calidad", "Falla ante errores nuevos o algo viejo, roto o inconsistente. Solo lee.",
            ("npm", "run", "verificar"), "nada", npm="verificar"),
    Proceso("test", "Probar el analizador T-SQL", "Corre las pruebas del analizador de procedimientos. Solo lee.",
            ("npm", "test"), "nada", npm="test"),
    Proceso("bases", "Validar las bases de datos", "Prueba la conexión a cada servidor SQL (mish, slc, rcc) y que cada base que usan los reportes esté en línea. Solo lee; no toca el repo DICCIONARIO.",
            ("SELECT name, state_desc FROM sys.databases",), "nada"),
)}
