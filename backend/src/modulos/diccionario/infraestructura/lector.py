"""Lee el diccionario.json del repo DICCIONARIO (carpeta hermana de REPORTES-AUTOMATIZADOS, o `DICCIONARIO_DIR` del .env)."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from core.configuracion import RAIZ_REPO
from core.excepciones import NoEncontrado

_cache: tuple[int, dict] | None = None   # (mtime del archivo, contenido): son ~2 MB y las pantallas lo piden a cada rato


def carpeta() -> Path:
    return Path(os.getenv("DICCIONARIO_DIR") or RAIZ_REPO.parent / "DICCIONARIO")


def _archivo() -> Path:
    return carpeta() / "diccionario" / "diccionario.json"


def leer() -> dict:
    global _cache
    ruta = _archivo()
    if not ruta.is_file():
        raise NoEncontrado(f"No encontré el diccionario en {ruta}. Clona el repo DICCIONARIO junto a este o define DICCIONARIO_DIR en el .env.")
    t = ruta.stat().st_mtime_ns
    if _cache is None or _cache[0] != t:
        _cache = (t, json.loads(ruta.read_text(encoding="utf-8")))
    return _cache[1]


def generado() -> str:
    return datetime.fromtimestamp(_archivo().stat().st_mtime).isoformat(timespec="seconds")
