"""Configuración central: rutas del proyecto y definición de las 3 bases de datos.

Los secretos NUNCA van en el código: se leen de variables de entorno / archivo `.env`
(ver `.env.example`).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")  # antes de leer REPORTES_DIR_*
DIR_SQL = RAIZ / "sql"
# data/ no se versiona: inputs = archivos que entran (Excel, CSV, plantillas base); outputs = lo que generan los reportes
DIR_INPUTS = Path(os.getenv("REPORTES_DIR_INPUTS", RAIZ / "data" / "inputs"))
DIR_OUTPUTS = Path(os.getenv("REPORTES_DIR_OUTPUTS", RAIZ / "data" / "outputs"))

DRIVER_ODBC = os.getenv("DB_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")


class ConfiguracionError(RuntimeError):
    """Falta configuración necesaria (p. ej. credenciales)."""


@dataclass(frozen=True)
class BaseDatos:
    """Una de las 3 conexiones del proyecto.

    `prefijo` es el prefijo de las variables de entorno (p. ej. DW_RAW -> DW_RAW_SERVER).
    `usuario`/`clave` vacíos => autenticación de Windows (Trusted_Connection).
    """

    nombre: str
    prefijo: str
    descripcion: str
    servidor_defecto: str
    base_defecto: str
    windows_auth_defecto: bool

    @property
    def servidor(self) -> str:
        return os.getenv(f"{self.prefijo}_SERVER", self.servidor_defecto)

    @property
    def base(self) -> str:
        return os.getenv(f"{self.prefijo}_DATABASE", self.base_defecto)

    @property
    def usuario(self) -> str | None:
        return os.getenv(f"{self.prefijo}_USER") or None

    @property
    def clave(self) -> str | None:
        return os.getenv(f"{self.prefijo}_PASSWORD") or None

    def cadena_odbc(self) -> str:
        partes = [f"DRIVER={{{DRIVER_ODBC}}}", f"SERVER={self.servidor}", f"DATABASE={self.base}"]
        if self.usuario or self.clave:
            if not (self.usuario and self.clave):
                raise ConfiguracionError(
                    f"Define {self.prefijo}_USER y {self.prefijo}_PASSWORD (o ninguno para autenticación de Windows)"
                )
            partes += [f"UID={self.usuario}", "PWD={" + self.clave.replace("}", "}}") + "}"]
        elif self.windows_auth_defecto:
            partes.append("Trusted_Connection=yes")
        else:
            raise ConfiguracionError(
                f"La conexión {self.nombre} requiere {self.prefijo}_USER y {self.prefijo}_PASSWORD en el .env"
            )
        return ";".join(partes)


# --- Las 3 bases de datos -------------------------------------------------------
BASES: dict[str, BaseDatos] = {
    "dw_raw": BaseDatos(
        nombre="dw_raw",
        prefijo="DW_RAW",
        descripcion="DW_Raw_v2 (staging CMG Mora); desde aquí también se consulta dbriesgos (nombres de 3 partes)",
        servidor_defecto="172.20.0.70",
        base_defecto="DW_Raw_v2",
        windows_auth_defecto=False,
    ),
    "rcc": BaseDatos(
        nombre="rcc",
        prefijo="RCC",
        descripcion="DBRCC (Registro Consolidado de Créditos / deuda sistema financiero)",
        servidor_defecto="172.20.0.70",
        base_defecto="DBRCC",
        windows_auth_defecto=False,
    ),
    "slc": BaseDatos(
        nombre="slc",
        prefijo="SLC",
        descripcion="slc (servidor 213); desde aquí también INTCOM, DWH y csd (nombres de 3 partes)",
        servidor_defecto="172.24.2.213",
        base_defecto="slc",
        windows_auth_defecto=True,
    ),
}


def obtener_base(nombre: str) -> BaseDatos:
    try:
        return BASES[nombre.lower()]
    except KeyError:
        raise ConfiguracionError(f"Base desconocida '{nombre}'. Opciones: {', '.join(BASES)}") from None
