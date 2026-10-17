"""Fichas del historial de validación en disco: data/outputs/validaciones/<grupo>/<id>.json (no versionadas)."""

from __future__ import annotations

from pathlib import Path


from core.configuracion import DIR_OUTPUTS
from modulos.reportes.aplicacion import dto as dto_reportes

DIR = DIR_OUTPUTS / "validaciones"


def _carpeta(grupo: str) -> Path:
    return DIR / grupo


def guardar(x: dto_reportes.EntradaValidacion) -> None:
    carpeta = _carpeta(x.grupo)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / f"{x.id}.json").write_text(x.model_dump_json(indent=2), encoding="utf-8")


def podar(grupo: str, maximo: int) -> None:
    """Deja solo las `maximo` fichas más recientes del grupo."""
    for vieja in sorted(_carpeta(grupo).glob("*.json"))[:-maximo]:
        vieja.unlink(missing_ok=True)


def listar(grupo: str, limite: int) -> list[dto_reportes.EntradaValidacion]:
    """De la más reciente a la más antigua."""
    carpeta = _carpeta(grupo)
    if not carpeta.is_dir():
        return []
    return [dto_reportes.EntradaValidacion.model_validate_json(p.read_text(encoding="utf-8")) for p in sorted(carpeta.glob("*.json"), reverse=True)[:limite]]
