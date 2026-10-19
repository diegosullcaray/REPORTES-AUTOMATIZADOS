"""Puertos del módulo diccionario: el diccionario guardado, el catálogo, los metadatos de SQL Server y el lanzador de procesos."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from core.puertos import Registro
from modulos.diccionario.aplicacion import dto


class Lector(Protocol):
    def leer(self) -> dict:
        """El diccionario generado desde la base. NoEncontrado si todavía no se generó."""
        ...
    def origen(self) -> str | None:
        """Fecha (ISO) en que se guardó el diccionario, o None si no hay."""
        ...
    def guardar(self, datos: dict) -> None:
        """Guarda el diccionario generado desde la base."""
        ...


class Catalogo(Protocol):
    FUENTE: str   # de dónde se lee (tabla), para mostrarlo
    CONSULTA: str  # la consulta que se ejecuta, para mostrarla en la pestaña Script

    def leer(self, forzar: bool = False) -> list[dict]:
        """Los reportes de `mod_rep.rep.RREGREP01` como `{codigo, descripcion, procedimiento, parametros}`. Lanza si no hay conexión."""
        ...


class Generador(Protocol):
    """Lo que SQL Server sabe de los procedimientos y las tablas (solo metadatos)."""

    def dependencias(self, base: str, sps: list[tuple[str, str]]) -> list[dict]: ...
    def parametros(self, base: str) -> list[dict]: ...
    def cuerpos(self, base: str, sps: list[tuple[str, str]]) -> list[dict]: ...
    def estructura(self, base: str, tablas: list[tuple[str, str]]) -> list[dict]: ...
    def scripts(self) -> list[dto.ScriptArchivo]:
        """Las consultas que ejecuta, tal cual, para mostrarlas."""
        ...


class Lanzador(Protocol):
    def ejecutar_tarea(self, proceso: str, tarea: Callable[[Callable[[str], None]], int]) -> dto.Ejecucion:
        """Un proceso propio de la API: `tarea(emitir)` escribe su log con `emitir(texto)` y devuelve el código de salida. PeticionInvalida si ya hay uno en curso."""
        ...
    def historial(self, limite: int = 30) -> list[dto.Ejecucion]: ...
    def obtener(self, id_: str) -> dto.EjecucionDetalle:
        """KeyError si no existe."""
        ...


@dataclass
class Puertos:
    lector: Lector
    lanzador: Lanzador
    catalogo: Catalogo
    generador: Generador


puertos: Registro[Puertos] = Registro("diccionario")
