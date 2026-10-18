"""Etiquetas de los grupos de /reportes en disco: data/outputs/etiquetas.json (no versionado)."""

from __future__ import annotations

from core.configuracion import DIR_OUTPUTS
from modulos.reportes.aplicacion import dto as dto_reportes

RUTA = DIR_OUTPUTS / "etiquetas.json"


def leer() -> dto_reportes.CatalogoEtiquetas:
    if not RUTA.exists():
        return dto_reportes.CatalogoEtiquetas()
    return dto_reportes.CatalogoEtiquetas.model_validate_json(RUTA.read_text(encoding="utf-8"))


def escribir(catalogo: dto_reportes.CatalogoEtiquetas) -> None:
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    RUTA.write_text(catalogo.model_dump_json(indent=2), encoding="utf-8")
