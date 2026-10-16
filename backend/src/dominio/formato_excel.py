"""Cómo sale un resultado en el Excel del legado: descripción de columnas y de hojas de resumen (sin escribir ningún archivo)."""

from __future__ import annotations

from dataclasses import dataclass

FORMATO_MONEDA = '"S/" #,##0.00'


@dataclass(frozen=True)
class Columna:
    """Cómo sale una columna del resultado en el Excel: qué columna del SQL es, qué encabezado lleva y cómo se muestra."""

    origen: str | tuple[str, ...]   # nombre(s) de la columna en el resultado (sin distinguir mayúsculas)
    titulo: str                     # encabezado en el Excel
    si_cero: str | None = None      # texto que reemplaza al valor 0 (p. ej. "-" o "NULL")
    si_nulo: str | None = None      # texto que reemplaza a los nulos (p. ej. "NULL", como los pega SSMS)
    formato: str | None = None      # formato de número/fecha de Excel (p. ej. "dd/mm/yyyy")


class ColumnaFaltante(ValueError):
    """El resultado no trae una columna que el formato del reporte espera."""


@dataclass(frozen=True)
class Resumen:
    """Hoja de resumen jerárquico calculada a partir del resultado `origen` (índice en la lista de resultados)."""

    nombre: str                   # nombre de la hoja (RESUMEN_v2)
    niveles: tuple[str, ...]      # columnas del resultado, de mayor a menor nivel
    valor: str                    # columna que se suma
    titulo_filas: str             # encabezado de la columna de etiquetas
    titulo_valor: str             # encabezado de la columna de valores
    origen: int = 0
    formato: str = FORMATO_MONEDA
