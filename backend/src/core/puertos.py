"""Puertos del núcleo (base de datos y entorno) y el registro de adaptadores que usa cada módulo.

Cada módulo declara los puertos que necesita en su `aplicacion/puertos.py` y los pide con su propio `puertos()`; el núcleo ofrece
lo que todos comparten (`nucleo().bd`, `nucleo().entorno`). `config/composicion.py` conecta los adaptadores reales al arrancar y las
pruebas registran dobles. Los adaptadores pueden ser módulos: un módulo con las funciones correctas cumple el `Protocol`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Generic, Protocol, TypeVar

import pandas as pd  # tipo de datos tabular de los resultados (no es una dependencia de I/O)


class AccesoBD(Protocol):
    """Los 3 servidores SQL Server (mish, slc, rcc); cada llamada puede pedir su base con `base=`."""

    def leer_sql(self, servidor: str, consulta: str, params: dict | None = None, base: str | None = None, timeout: int | None = None) -> pd.DataFrame: ...
    def ejecutar_lote(self, servidor: str, sql: str, base: str | None = None) -> list[pd.DataFrame]: ...
    def probar_conexiones(self) -> dict[str, str]: ...


@dataclass(frozen=True)
class InfoServidor:
    """Un servidor SQL del `.env` (nunca sus credenciales): su nombre y su dirección."""

    nombre: str
    servidor: str


class Entorno(Protocol):
    """Configuración del proceso: variables del `.env`, carpetas de datos y fecha de corte configurada."""

    def leer(self, variable: str, defecto: str = "") -> str: ...
    def guardar(self, cambios: dict[str, str], al_proceso: list[str] | None = None) -> None:
        """Escribe en el .env (valor vacío = quita la variable) y, en el proceso, las variables de `al_proceso` (todas si es None)."""
        ...
    def guardado(self) -> Mapping[str, str | None]:
        """Lo que hay escrito hoy en el .env (puede diferir de lo que el proceso cargó al arrancar)."""
        ...
    def corte(self, frecuencia: str) -> date | None:
        """Fecha de corte del .env (FECHA_CORTE_DIARIA / FECHA_CORTE_MENSUAL) o None."""
        ...
    def raiz(self) -> Path: ...
    def dir_inputs(self) -> Path: ...
    def dir_outputs(self) -> Path: ...
    def driver_odbc(self) -> str: ...
    def servidores(self) -> list[InfoServidor]: ...


T = TypeVar("T")


class Registro(Generic[T]):
    """Los adaptadores de un módulo: se registran al arrancar y se piden con `registro()`."""

    def __init__(self, nombre: str):
        self.nombre = nombre
        self._valor: T | None = None
        self.fabrica: Callable[[], T] | None = None   # la asigna `config.composicion`: crea los adaptadores reales la primera vez que hacen falta

    def registrar(self, valor: T | None) -> None:
        """Conecta (o, con None, desconecta) los adaptadores. Las pruebas registran dobles."""
        self._valor = valor

    def __call__(self) -> T:
        if self._valor is None:
            if self.fabrica is None:
                raise RuntimeError(f"Los puertos de «{self.nombre}» no están conectados: importa `config.composicion` (la API y la consola lo hacen al arrancar).")
            self._valor = self.fabrica()
        return self._valor


@dataclass
class Nucleo:
    bd: AccesoBD
    entorno: Entorno


nucleo: Registro[Nucleo] = Registro("core")
