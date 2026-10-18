"""Secciones de /reportes en disco: data/outputs/secciones.json (no versionado)."""

from __future__ import annotations

import json

from core.configuracion import DIR_OUTPUTS
from modulos.reportes.aplicacion import dto as dto_reportes

RUTA = DIR_OUTPUTS / "secciones.json"


def leer() -> list[dto_reportes.Seccion]:
    if not RUTA.exists():
        return []
    return [dto_reportes.Seccion.model_validate(x) for x in json.loads(RUTA.read_text(encoding="utf-8"))]


def escribir(secciones: list[dto_reportes.Seccion]) -> None:
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    RUTA.write_text(json.dumps([s.model_dump() for s in secciones], ensure_ascii=False, indent=2), encoding="utf-8")
