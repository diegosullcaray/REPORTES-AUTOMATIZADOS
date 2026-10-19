"""Lanza los procesos del repo DICCIONARIO como subproceso (sin shell), uno a la vez, y deja su estado y log en data/outputs/diccionario/."""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
import uuid
from datetime import datetime
from pathlib import Path

from core.configuracion import DIR_OUTPUTS
from core.excepciones import PeticionInvalida
from modulos.diccionario.aplicacion import dto

DIR = DIR_OUTPUTS / "diccionario"
MAX_LOG = 500_000
MAX_FICHAS = 50
# Lo único que npm y node necesitan: el repo DICCIONARIO es otro código y no debe ver las claves de esta API (SMTP, bases, Google).
_ENTORNO_MINIMO = ("PATH", "PATHEXT", "SYSTEMROOT", "COMSPEC", "TEMP", "TMP", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "HOME")  # en mayúsculas: Windows no distingue y Python las entrega así; node no arranca sin SYSTEMROOT
_activos: set[str] = set()
_candado = threading.Lock()
_lanzar = threading.Lock()


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _ruta(id_: str, ext: str) -> Path:
    if not id_.isalnum():
        raise KeyError(id_)
    return DIR / f"{id_}.{ext}"


def _guardar(x: dto.Ejecucion) -> None:
    with _candado:
        _ruta(x.id, "json").write_text(x.model_dump_json(indent=2), encoding="utf-8")


def _leer(id_: str) -> dto.Ejecucion:
    ruta = _ruta(id_, "json")
    with _candado:  # no leer a medias lo que otro hilo está reescribiendo
        if not ruta.exists():
            raise KeyError(id_)
        x = dto.Ejecucion.model_validate_json(ruta.read_text(encoding="utf-8"))
    if x.estado == "ejecutando" and id_ not in _activos:  # la API se reinició a mitad del proceso
        x.estado = "error"
    return x


def en_curso() -> bool:
    return bool(_activos)


def _podar() -> None:
    """Deja solo las fichas más recientes (el historial se lee completo en cada consulta)."""
    for vieja in sorted(DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)[:-MAX_FICHAS]:
        if vieja.stem not in _activos:
            vieja.unlink(missing_ok=True)
            vieja.with_suffix(".log").unlink(missing_ok=True)


def _correr(x: dto.Ejecucion, comando: tuple[str, ...], carpeta: Path) -> None:
    try:
        exe = shutil.which(comando[0])
        with _ruta(x.id, "log").open("w", encoding="utf-8") as log:
            if exe is None:
                log.write(f"✗ No encuentro «{comando[0]}»: instálalo y vuelve a abrir la API.\n")
                codigo = 127
            else:
                codigo = subprocess.run([exe, *comando[1:]], cwd=carpeta, stdout=log, stderr=subprocess.STDOUT, env={k: v for k, v in os.environ.items() if k.upper() in _ENTORNO_MINIMO}).returncode
        x.codigo, x.estado = codigo, "ok" if codigo == 0 else "error"
    except OSError as exc:
        _ruta(x.id, "log").write_text(f"✗ No se pudo lanzar el proceso: {exc}\n", encoding="utf-8")
        x.codigo, x.estado = 1, "error"
    finally:
        x.fin = _ahora()
        _guardar(x)
        _activos.discard(x.id)


def ejecutar(proceso: str, comando: tuple[str, ...], carpeta: Path) -> dto.Ejecucion:
    DIR.mkdir(parents=True, exist_ok=True)
    x = dto.Ejecucion(id=uuid.uuid4().hex[:12], proceso=proceso, estado="ejecutando", inicio=_ahora(), fin=None, codigo=None)
    with _lanzar:  # comprobar y anotar de una vez: dos peticiones casi juntas no pueden lanzar dos procesos
        if _activos:
            raise PeticionInvalida("Ya hay un proceso del diccionario en curso: espera a que termine.")
        _activos.add(x.id)
    _podar()
    _guardar(x)
    threading.Thread(target=_correr, args=(x.model_copy(), comando, carpeta), daemon=True, name=f"diccionario-{x.id}").start()
    return x


def historial(limite: int = 30) -> list[dto.Ejecucion]:
    if not DIR.is_dir():
        return []
    todas = sorted((_leer(p.stem) for p in DIR.glob("*.json")), key=lambda x: x.inicio, reverse=True)
    return todas[:limite]


def obtener(id_: str) -> dto.EjecucionDetalle:
    x, log = _leer(id_), _ruta(id_, "log")
    return dto.EjecucionDetalle(**x.model_dump(), log=log.read_text(encoding="utf-8", errors="replace")[-MAX_LOG:] if log.exists() else "")
