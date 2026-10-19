"""Puertos del módulo diccionario: la lectura del diccionario.json y el lanzador de procesos del repo DICCIONARIO."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.puertos import Registro
from modulos.diccionario.aplicacion import dto


class Lector(Protocol):
    def carpeta(self) -> Path: ...
    def leer(self) -> dict:
        """El diccionario.json ya cargado. NoEncontrado con una pista si no está."""
        ...
    def generado(self) -> str: ...


class Lanzador(Protocol):
    def ejecutar(self, proceso: str, comando: tuple[str, ...], carpeta: Path) -> dto.Ejecucion:
        """PeticionInvalida si ya hay un proceso en curso."""
        ...
    def historial(self, limite: int = 30) -> list[dto.Ejecucion]: ...
    def obtener(self, id_: str) -> dto.EjecucionDetalle:
        """KeyError si no existe."""
        ...


@dataclass
class Puertos:
    lector: Lector
    lanzador: Lanzador


puertos: Registro[Puertos] = Registro("diccionario")
