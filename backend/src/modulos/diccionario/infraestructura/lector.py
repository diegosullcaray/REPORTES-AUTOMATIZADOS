"""Lee el repo DICCIONARIO (carpeta hermana de REPORTES-AUTOMATIZADOS, o `DICCIONARIO_DIR` del .env): su diccionario.json, el código de sus scripts y los archivos que genera. Solo lectura."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

from core.configuracion import RAIZ_REPO
from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.diccionario.aplicacion import dto

MAX_TEXTO = 200_000
_TEXTO = {".md", ".json", ".txt", ".mjs", ".js", ".py"}
_SCRIPT = re.compile(r"(?:node|python)\s+([\w./-]+\.(?:mjs|js|py))")   # los archivos que un script de package.json ejecuta

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


def _dentro(ruta: Path) -> bool:
    return carpeta().resolve() in ruta.resolve().parents


def archivos(patrones: tuple[str, ...]) -> list[dto.ArchivoProceso]:
    """Los archivos que dejan los patrones (relativos a la carpeta del repo), más recientes primero."""
    base = carpeta()
    salida = [dto.ArchivoProceso(ruta=f.relative_to(base).as_posix(), tamano=f.stat().st_size, tipo="texto" if f.suffix in _TEXTO else "otro",
                                 modificado=datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds"))
              for patron in patrones for f in sorted(base.glob(patron)) if f.is_file() and _dentro(f)]
    return sorted(salida, key=lambda a: a.modificado, reverse=True)


def texto(ruta: str, patrones: tuple[str, ...]) -> dto.VistaArchivo:
    """El texto de uno de los archivos que dejan los patrones (nunca una ruta que no salga de ellos)."""
    a = next((x for x in archivos(patrones) if x.ruta == ruta), None)
    if a is None:
        raise NoEncontrado(f"El proceso no genera «{ruta}».")
    if a.tipo != "texto":
        raise PeticionInvalida("Solo hay vista previa de archivos de texto.")
    contenido = (carpeta() / ruta).read_text(encoding="utf-8", errors="replace")
    return dto.VistaArchivo(ruta=ruta, texto=contenido[:MAX_TEXTO], recortado=len(contenido) > MAX_TEXTO)


def script_npm(nombre: str) -> list[dto.ScriptArchivo]:
    """El script de package.json y el código de los archivos que ejecuta (solo los que están dentro del repo)."""
    paquete = carpeta() / "package.json"
    try:
        comando = json.loads(paquete.read_text(encoding="utf-8"))["scripts"][nombre]
    except (OSError, ValueError, KeyError):
        raise NoEncontrado(f"No encontré el script «{nombre}» en {paquete}.") from None
    piezas = [dto.ScriptArchivo(ruta=f"package.json › scripts.{nombre}", codigo=comando)]
    for ruta in dict.fromkeys(_SCRIPT.findall(comando)):
        f = carpeta() / ruta
        if f.is_file() and _dentro(f):
            piezas.append(dto.ScriptArchivo(ruta=ruta, codigo=f.read_text(encoding="utf-8", errors="replace")[:MAX_TEXTO]))
    return piezas
