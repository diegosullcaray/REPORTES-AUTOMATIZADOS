"""Puertos: lo que la aplicación necesita del mundo exterior, como interfaces (Protocol) sin nombrar ninguna librería de I/O.

La infraestructura las implementa (`infraestructura/`) y `composicion.py` las conecta al arrancar (API web o consola).
Así los casos de uso y las reglas del dominio se prueban con dobles, y cambiar de base de datos, correo o proveedor no los toca.
Los adaptadores pueden ser módulos: un módulo con las funciones correctas cumple el puerto.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

import pandas as pd  # tipo de datos tabular de los resultados (no es una dependencia de I/O)

from aplicacion import dto


class AccesoBD(Protocol):
    """Los 3 servidores SQL Server (mish, slc, rcc); cada llamada puede pedir su base con `base=`."""

    def leer_sql(self, servidor: str, consulta: str, params: dict | None = None, base: str | None = None, timeout: int | None = None) -> pd.DataFrame: ...
    def ejecutar_lote(self, servidor: str, sql: str, base: str | None = None) -> list[pd.DataFrame]: ...
    def probar_conexiones(self) -> dict[str, str]: ...


@dataclass(frozen=True)
class InfoServidor:
    """Lo que la pantalla de bases de datos muestra de un servidor (nunca las credenciales)."""

    nombre: str
    servidor: str
    autenticacion: str            # SQL | Windows
    credenciales_en_env: bool
    descripcion: str


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


class CorreoSMTP(Protocol):
    """Correo corporativo (cuenta MIS) y aviso al webhook de Google Chat."""

    PUERTO_DEFECTO: int
    HOST_DEFECTO: str

    def config_desde_env(self) -> Any: ...
    def leer_destinatarios(self, ruta: Path | None = None) -> list[str]: ...
    def construir_mensaje(self, cfg: Any, asunto: str, html: str, destinatarios: list[str], **opciones: Any) -> Any: ...
    def enviar(self, cfg: Any, msg: Any, destinatarios: list[str]) -> None: ...
    def notificar_chat(self, url: str, texto: str) -> None: ...


class GoogleWorkspace(Protocol):
    """Google con OAuth de usuario: Gmail, Chat y los servidores MCP oficiales. Los fallos son `ErrorIntegracion`."""

    SERVICIOS: Mapping[str, Any]

    def servicios_activos(self) -> list[str]: ...
    def falta_consentimiento(self, servicio: str) -> bool: ...
    def url_autorizacion(self, redirect_uri: str, state: str, desafio: str, servicios: list[str]) -> str: ...
    def canjear_codigo(self, codigo: str, redirect_uri: str, verificador: str) -> dict: ...
    def token_de_acceso(self) -> str: ...
    def correo_de(self, token: str) -> str: ...
    def revocar(self, token: str) -> None: ...
    def firma_gmail(self, token: str) -> str: ...
    def armar_correo(self, para: list[str], cc: list[str], asunto: str, texto: str, firma_html: str = "", adjuntos: list[Path] | None = None) -> Any: ...
    def enviar_correo(self, token: str, para: str, asunto: str, cuerpo: str) -> str: ...
    def enviar_mensaje(self, token: str, msg: Any) -> str: ...
    def enviar_chat(self, token: str, para: str, texto: str, adjuntos: list[Path] | None = None) -> str: ...
    def espacios_chat(self, token: str, cantidad: int = 20) -> list[dict]: ...
    def enviar(self, servicio: str, destinatario: str, texto: str) -> str: ...
    def mcp_herramientas(self, servicio: str) -> list[dict]: ...
    def mcp_ejecutar(self, servicio: str, herramienta: str, argumentos: dict) -> tuple[bool, str]: ...


@dataclass
class Puertos:
    bd: AccesoBD
    entorno: Entorno
    excel: ExportadorExcel
    cola: ColaEjecuciones
    historial_validacion: HistorialValidacion
    lector_archivos: LectorArchivos
    correo: CorreoSMTP
    google: GoogleWorkspace


_puertos: Puertos | None = None
fabrica: Callable[[], Puertos] | None = None   # la asigna `composicion` al importarse: crea los adaptadores reales la primera vez que hacen falta


def registrar(p: Puertos | None) -> None:
    """Conecta (o, con None, desconecta) los adaptadores. Las pruebas registran dobles."""
    global _puertos
    _puertos = p


def puertos() -> Puertos:
    global _puertos
    if _puertos is None:
        if fabrica is None:
            raise RuntimeError("Los puertos no están conectados: importa `composicion` (la API y la consola lo hacen al arrancar).")
        _puertos = fabrica()
    return _puertos
