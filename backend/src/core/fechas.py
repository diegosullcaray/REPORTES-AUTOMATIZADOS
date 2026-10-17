"""Lo mínimo de fechas que comparten el núcleo (variables del .env) y el módulo de reportes: AAAA-MM-DD y la fecha de corte escrita en el .env."""

from __future__ import annotations

from datetime import date, datetime

from .excepciones import ConfiguracionError


def fecha_iso(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Fecha inválida '{valor}', usa AAAA-MM-DD") from exc


VAR_CORTE = {"diaria": "FECHA_CORTE_DIARIA", "mensual": "FECHA_CORTE_MENSUAL"}


def corte_desde_texto(frecuencia: str, valor: str) -> date | None:
    """Fecha de corte escrita en la variable de entorno de esa frecuencia (AAAA-MM-DD); vacío = sin definir."""
    variable = VAR_CORTE[frecuencia]
    valor = valor.strip()
    if not valor:
        return None
    try:
        return fecha_iso(valor)
    except ValueError as exc:
        raise ConfiguracionError(f"{variable} en el .env no es válida: {exc}") from exc
