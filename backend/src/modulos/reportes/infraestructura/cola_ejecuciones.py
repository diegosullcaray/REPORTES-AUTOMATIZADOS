"""Cola de ejecuciones: un reporte a la vez, como subproceso de `main.py` (mismos códigos de salida y mensajes que la consola).

Un solo trabajador porque hay reportes que escriben en BD (cmg-mora trunca CMGMora_Recaudo, tapp crea/borra una tabla):
dos a la vez podrían pisarse. Cada ejecución deja en data/outputs/ejecuciones/ su `<id>.json` (estado) y `<id>.log` (salida),
así el historial sobrevive a reinicios de la API.
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

from modulos.reportes.dominio.archivos import es_generado
from modulos.reportes.dominio.reportes import REPORTES

from core.configuracion import DIR_OUTPUTS, RAIZ
from modulos.reportes.aplicacion import dto as dto_reportes

DIR = DIR_OUTPUTS / "ejecuciones"
ESTADO_POR_CODIGO = {0: "ok", 1: "error", 2: "configuracion", 3: "tablas_desactualizadas"}
MAX_LOG = 500_000

_cola: queue.Queue[str] = queue.Queue()
_candado = threading.Lock()


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _ruta(id_: str, ext: str) -> Path:
    if not id_.isalnum():
        raise KeyError(id_)
    return DIR / f"{id_}.{ext}"


def _leer(id_: str) -> dto_reportes.Ejecucion:
    ruta = _ruta(id_, "json")
    if not ruta.exists():
        raise KeyError(id_)
    x = dto_reportes.Ejecucion.model_validate_json(ruta.read_text(encoding="utf-8"))
    x.archivos = [n for n in x.archivos if es_generado(n)]   # las ejecuciones antiguas pudieron registrar .json internos
    return x


def _guardar(x: dto_reportes.Ejecucion) -> None:
    with _candado:
        _ruta(x.id, "json").write_text(x.model_dump_json(indent=2), encoding="utf-8")


def encolar(reporte: str, argumentos: list[str]) -> dto_reportes.Ejecucion:
    DIR.mkdir(parents=True, exist_ok=True)
    x = dto_reportes.Ejecucion(id=uuid.uuid4().hex[:12], reporte=reporte, argumentos=argumentos, estado="en_cola", codigo=None, inicio=_ahora(), fin=None)
    _guardar(x)
    _cola.put(x.id)
    return x


def obtener(id_: str) -> dto_reportes.EjecucionDetalle:
    x = _leer(id_)
    log = _ruta(id_, "log")
    texto = log.read_text(encoding="utf-8", errors="replace")[-MAX_LOG:] if log.exists() else ""
    return dto_reportes.EjecucionDetalle(**x.model_dump(), log=texto)


def eliminar(ids: list[str]) -> int:
    """Quita del historial las ejecuciones (estado y log); los archivos generados no se tocan.
    KeyError si alguna no existe; ValueError si alguna sigue en cola o corriendo (nada se borra en ese caso)."""
    xs = [_leer(i) for i in dict.fromkeys(ids)]
    if activas := [x.id for x in xs if x.estado in {"en_cola", "ejecutando"}]:
        raise ValueError(f"Siguen en curso y no se pueden eliminar: {', '.join(activas)}")
    with _candado:
        for x in xs:
            for ext in ("json", "log"):
                _ruta(x.id, ext).unlink(missing_ok=True)
    return len(xs)


def historial(reporte: str | None = None, limite: int = 100) -> list[dto_reportes.Ejecucion]:
    if not DIR.is_dir():
        return []
    # ponytail: lee todos los .json en cada consulta; pasar a SQLite si el historial crece a miles
    todas = sorted((_leer(p.stem) for p in DIR.glob("*.json")), key=lambda x: x.inicio, reverse=True)
    return [x for x in todas if reporte in (None, x.reporte)][:limite]


def _anotar(id_: str, texto: str) -> None:
    with _ruta(id_, "log").open("a", encoding="utf-8") as log:
        log.write(texto)


def carpeta_salida(comando: str) -> Path:
    """Carpeta de salida por defecto del reporte (la misma que usa el ejecutor)."""
    return DIR_OUTPUTS / REPORTES[comando].carpeta


def _foto(carpeta: Path) -> dict[str, float]:
    return {f.name: f.stat().st_mtime for f in carpeta.iterdir() if f.is_file() and es_generado(f.name)} if carpeta.is_dir() else {}


def _correr(id_: str) -> None:
    x = _leer(id_)
    carpeta = carpeta_salida(x.reporte)
    antes = _foto(carpeta)
    x.estado, x.inicio = "ejecutando", _ahora()
    _guardar(x)
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    try:
        with _ruta(id_, "log").open("w", encoding="utf-8") as log:
            codigo = subprocess.run([sys.executable, "main.py", *x.argumentos], cwd=RAIZ, stdout=log, stderr=subprocess.STDOUT, env=entorno).returncode
    except OSError as exc:
        _anotar(id_, f"✗ No se pudo lanzar el proceso: {exc}\n")
        codigo = 1
    despues = _foto(carpeta)
    x.archivos = sorted(n for n, t in despues.items() if antes.get(n) != t)
    x.codigo, x.estado, x.fin = codigo, ESTADO_POR_CODIGO.get(codigo, "error"), _ahora()
    _guardar(x)


def _trabajador() -> None:
    while True:
        id_ = _cola.get()
        try:
            _correr(id_)
        except Exception as exc:  # noqa: BLE001 - el trabajador no debe morir; se registra en el log de esa ejecución
            _anotar(id_, f"\n✗ Error interno de la API: {exc}\n")
        finally:
            _cola.task_done()


def iniciar() -> None:
    """Marca como interrumpidas las que quedaron a medias (la API se reinició) y arranca el trabajador."""
    for x in historial(limite=10_000):
        if x.estado in {"en_cola", "ejecutando"}:
            x.estado, x.fin = "error", _ahora()
            _guardar(x)
            _anotar(x.id, "\n✗ Interrumpida: la API se reinició durante la ejecución.\n")
    threading.Thread(target=_trabajador, daemon=True, name="ejecuciones").start()
