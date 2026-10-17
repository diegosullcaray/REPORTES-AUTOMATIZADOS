"""Puertos del módulo de reportes: lo que necesita del mundo exterior (Excel, cola de ejecuciones, historial de validación, lectura de archivos)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd  # tipo de datos tabular de los resultados (no es una dependencia de I/O)

from core.puertos import Registro
from modulos.reportes.aplicacion import dto


class ExportadorExcel(Protocol):
    def guardar_libro(self, ruta: Path, hojas: list[tuple[str, pd.DataFrame]], resumenes: list = (), compartido: bool = False) -> Path: ...


class ColaEjecuciones(Protocol):
    """Una ejecución a la vez, como subproceso de `main.py`; el historial sobrevive a reinicios."""

    def iniciar(self) -> None: ...
    def encolar(self, reporte: str, argumentos: list[str]) -> dto.Ejecucion: ...
    def obtener(self, id_: str) -> dto.EjecucionDetalle: ...
    def historial(self, reporte: str | None = None, limite: int = 100) -> list[dto.Ejecucion]: ...
    def eliminar(self, ids: list[str]) -> int: ...


class HistorialValidacion(Protocol):
    def guardar(self, x: dto.EntradaValidacion) -> None: ...
    def podar(self, grupo: str, maximo: int) -> None: ...
    def listar(self, grupo: str, limite: int) -> list[dto.EntradaValidacion]: ...


class LectorArchivos(Protocol):
    def hojas_excel(self, ruta: Path, max_filas: int) -> list[dto.HojaPrevia]: ...


@dataclass
class Puertos:
    excel: ExportadorExcel
    cola: ColaEjecuciones
    historial_validacion: HistorialValidacion
    lector_archivos: LectorArchivos


puertos: Registro[Puertos] = Registro("reportes")
