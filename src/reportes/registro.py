"""Catálogo de reportes automatizados: nombre -> (módulo, frecuencia, base(s) de datos)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Reporte:
    nombre: str
    modulo: str
    frecuencia: str
    bases: tuple[str, ...]
    descripcion: str


REPORTES: dict[str, Reporte] = {r.nombre: r for r in (
    Reporte("cmg-mora", "reportes.diarios.cmg_mora", "diaria", ("dw_raw",),
            "Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0)"),
    Reporte("bancarizados", "reportes.mensuales.bancarizados", "mensual", ("rcc", "slc"),
            "Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio"),
    Reporte("bancarizados-producto", "reportes.mensuales.bancarizados_producto", "mensual", ("slc",),
            "Bancarizados por producto (clientes nuevos con desembolso)"),
    Reporte("clientes-extranjeros", "reportes.mensuales.clientes_extranjeros", "mensual", ("slc", "rcc"),
            "Clientes por nacionalidad: créditos, pasivos y seguros"),
    Reporte("indicadores-clientes", "reportes.mensuales.indicadores_clientes", "mensual", ("slc",),
            "Indicadores de clientes para el Directorio"),
)}


def frecuencia_de(reporte: str) -> str:
    """'diaria' | 'mensual' para un reporte automatizado o para una carpeta pendiente de sql/."""
    from .config import DIR_SQL

    if reporte in REPORTES:
        return REPORTES[reporte].frecuencia
    for frecuencia, carpeta in (("diaria", "diarias"), ("mensual", "mensuales")):
        if (DIR_SQL / carpeta / reporte).is_dir():
            return frecuencia
    raise KeyError(f"Reporte desconocido: {reporte}")
