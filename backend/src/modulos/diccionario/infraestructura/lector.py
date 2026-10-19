"""Lee y guarda el diccionario generado desde la base (`data/outputs/diccionario/generado/diccionario.json`). Lo escribe el proceso «Generar el diccionario desde la base»."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from core.configuracion import DIR_OUTPUTS
from core.excepciones import NoEncontrado

_cache: tuple[tuple[Path, int], dict] | None = None   # ((archivo, su mtime), contenido): son ~2 MB y las pantallas lo piden a cada rato


def _archivo() -> Path:
    return DIR_OUTPUTS / "diccionario" / "generado" / "diccionario.json"


def leer() -> dict:
    global _cache
    ruta = _archivo()
    if not ruta.is_file():
        raise NoEncontrado("Todavía no hay diccionario: genéralo en Diccionario › Procesos › «Generar el diccionario desde la base».")
    clave = (ruta, ruta.stat().st_mtime_ns)
    if _cache is None or _cache[0] != clave:
        _cache = (clave, json.loads(ruta.read_text(encoding="utf-8")))
    return _cache[1]


def origen() -> str | None:
    ruta = _archivo()
    return datetime.fromtimestamp(ruta.stat().st_mtime).isoformat(timespec="seconds") if ruta.is_file() else None


def guardar(datos: dict) -> None:
    """Escribe el diccionario; el reemplazo es atómico: nunca queda un archivo a medias."""
    destino = _archivo()
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".json.tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    temporal.replace(destino)
