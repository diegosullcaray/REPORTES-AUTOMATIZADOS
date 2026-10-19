"""Puertos del módulo diccionario: la lectura del diccionario.json y el lanzador de procesos del repo DICCIONARIO."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.puertos import Registro
from modulos.diccionario.aplicacion import dto


class Lector(Protocol):
    def carpeta(self) -> Path: ...
    def leer(self) -> dict:
        """El diccionario ya cargado: el generado desde la base o el diccionario.json del repo, el que se haya escrito último. NoEncontrado si no hay ninguno."""
        ...
    def origen(self) -> tuple[str, str] | None:
        """(`bd` | `repo`, fecha de modificación) del diccionario que se está usando, o None si no hay."""
        ...
    def guardar(self, datos: dict) -> None:
        """Guarda el diccionario generado desde la base (fuera del repo DICCIONARIO)."""
        ...
    def repo_disponible(self) -> bool:
        """¿Está el repo DICCIONARIO (con su package.json)? Sin él no hay procesos de npm."""
        ...
    def archivos(self, patrones: tuple[str, ...]) -> list[dto.ArchivoProceso]: ...
    def texto(self, ruta: str, patrones: tuple[str, ...]) -> dto.VistaArchivo:
        """NoEncontrado si `ruta` no es uno de los archivos que dejan los patrones."""
        ...
    def script_npm(self, nombre: str) -> list[dto.ScriptArchivo]: ...


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
    def estructura(self, base: str, tablas: list[tuple[str, str]]) -> list[dict]: ...
    def scripts(self) -> list[dto.ScriptArchivo]:
        """Las consultas que ejecuta, tal cual, para mostrarlas."""
        ...


class Lanzador(Protocol):
    def ejecutar(self, proceso: str, comando: tuple[str, ...], carpeta: Path) -> dto.Ejecucion:
        """PeticionInvalida si ya hay un proceso en curso."""
        ...
    def ejecutar_tarea(self, proceso: str, tarea: Callable[[Callable[[str], None]], int]) -> dto.Ejecucion:
        """Un proceso propio de la API: `tarea(emitir)` escribe su log con `emitir(texto)` y devuelve el código de salida."""
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
