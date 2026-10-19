"""Lee el diccionario (el generado desde la base o el diccionario.json del repo DICCIONARIO), el código de los scripts de ese repo y los archivos que genera. Solo lectura del repo.

El repo es la carpeta `DICCIONARIO` junto a este proyecto, o `DICCIONARIO_DIR` del .env; no hace falta: el diccionario también se puede generar desde la base
(`data/outputs/diccionario/generado/diccionario.json`). Si hay los dos, se usa el que se escribió último.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

from core.configuracion import DIR_OUTPUTS, RAIZ_REPO
from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.diccionario.aplicacion import dto

MAX_TEXTO = 200_000
_TEXTO = {".md", ".json", ".txt", ".mjs", ".js", ".py"}
_SCRIPT = re.compile(r"(?:node|python)\s+([\w./-]+\.(?:mjs|js|py))")   # los archivos que un script de package.json ejecuta

_cache: tuple[tuple[Path, int], dict] | None = None   # ((archivo, su mtime), contenido): son ~2 MB y las pantallas lo piden a cada rato


def carpeta() -> Path:
    return Path(os.getenv("DICCIONARIO_DIR") or RAIZ_REPO.parent / "DICCIONARIO")


def repo_disponible() -> bool:
    return (carpeta() / "package.json").is_file()


def _generado() -> Path:
    return DIR_OUTPUTS / "diccionario" / "generado" / "diccionario.json"


def _elegido() -> tuple[str, Path] | None:
    """El diccionario más reciente entre el generado desde la base y el del repo."""
    candidatos = [(o, p) for o, p in (("bd", _generado()), ("repo", carpeta() / "diccionario" / "diccionario.json")) if p.is_file()]
    return max(candidatos, key=lambda c: c[1].stat().st_mtime_ns, default=None)


def leer() -> dict:
    global _cache
    elegido = _elegido()
    if elegido is None:
        raise NoEncontrado("Todavía no hay diccionario: genéralo desde la base en Diccionario › Procesos › «Generar el diccionario desde la base» "
                           "(o deja el repo DICCIONARIO junto a este, o define DICCIONARIO_DIR en el .env).")
    ruta = elegido[1]
    clave = (ruta, ruta.stat().st_mtime_ns)
    if _cache is None or _cache[0] != clave:
        _cache = (clave, json.loads(ruta.read_text(encoding="utf-8")))
    return _cache[1]


def origen() -> tuple[str, str] | None:
    elegido = _elegido()
    return None if elegido is None else (elegido[0], datetime.fromtimestamp(elegido[1].stat().st_mtime).isoformat(timespec="seconds"))


def guardar(datos: dict) -> None:
    """Escribe el diccionario generado; el reemplazo es atómico: nunca queda un archivo a medias."""
    destino = _generado()
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".json.tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    temporal.replace(destino)


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
