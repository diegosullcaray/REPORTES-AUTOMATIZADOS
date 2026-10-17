"""Fecha de corte de un reporte: argumento > .env > día anterior (la regla es del dominio; el .env se lee por el puerto)."""

from __future__ import annotations

from datetime import date

from modulos.reportes.dominio import fechas
from core.puertos import nucleo



def resolver_corte(frecuencia: str, cli: date | None = None, hoy: date | None = None, lunes_sabado: bool = True) -> tuple[date, str]:
    """Fecha de corte y de dónde salió. Prioridad: --fecha-corte > .env > (solo diaria) día anterior; mensual sin fecha = error."""
    en_env = None if cli else nucleo().entorno.corte(frecuencia)
    return fechas.resolver_corte(frecuencia, cli, hoy, lunes_sabado, en_env)
