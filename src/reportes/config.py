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
# data/ no se versiona: inputs = archivos que entran (Excel, CSV, plantillas base); outputs = lo que generan los reportes
DIR_INPUTS = Path(os.getenv("REPORTES_DIR_INPUTS", RAIZ / "data" / "inputs"))
DIR_OUTPUTS = Path(os.getenv("REPORTES_DIR_OUTPUTS", RAIZ / "data" / "outputs"))

DRIVER_ODBC = os.getenv("DB_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")


class ConfiguracionError(RuntimeError):
    """Falta configuración necesaria (p. ej. credenciales)."""


@dataclass(frozen=True)
class Servidor:
    """Una de las 3 conexiones (SERVIDORES) del proyecto: un servidor SQL Server, no una base de datos.

    La base de datos (catálogo) la elige cada reporte con `base=` (o su propio `USE` / nombres de 3 partes);
    por eso el `.env` solo declara servidor y credenciales.

    `prefijo` es el prefijo de las variables de entorno (p. ej. SLC -> SLC_SERVER, SLC_USER, SLC_PASSWORD).
    `usuario`/`clave` vacíos => autenticación de Windows (Trusted_Connection) si el servidor la permite.
    """

    nombre: str
    prefijo: str
    descripcion: str
    servidor_defecto: str
    windows_auth_defecto: bool

    @property
    def servidor(self) -> str:
        return os.getenv(f"{self.prefijo}_SERVER", self.servidor_defecto)

    @property
    def base_defecto(self) -> str | None:
        """Catálogo inicial opcional para ese servidor (`<PREF>_DATABASE`); normalmente vacío."""
        return os.getenv(f"{self.prefijo}_DATABASE") or None

    @property
    def usuario(self) -> str | None:
        return os.getenv(f"{self.prefijo}_USER") or None

    @property
    def clave(self) -> str | None:
        return os.getenv(f"{self.prefijo}_PASSWORD") or None

    def cadena_odbc(self, base: str | None = None) -> str:
        """`base` (la que pide el reporte) manda sobre `<PREF>_DATABASE`; sin ninguna, se usa la base por defecto del login."""
        partes = [f"DRIVER={{{DRIVER_ODBC}}}", f"SERVER={self.servidor}"]
        catalogo = base or self.base_defecto
        if catalogo:
            partes.append(f"DATABASE={catalogo}")
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


# --- Las 3 conexiones (servidores) ------------------------------------------------
SERVIDORES: dict[str, Servidor] = {
    "mish": Servidor(
        nombre="mish",
        prefijo="MISH",
        descripcion="Servidor MISHWBDDES01 (autenticación de Windows). Aún sin reportes asignados",
        servidor_defecto="MISHWBDDES01",
        windows_auth_defecto=True,
    ),
    "slc": Servidor(
        nombre="slc",
        prefijo="SLC",
        descripcion="Servidor 172.24.2.213 (Windows): bases slc, storage, dwh, intcom, csd, dma, appj…",
        servidor_defecto="172.24.2.213",
        windows_auth_defecto=True,
    ),
    "rcc": Servidor(
        nombre="rcc",
        prefijo="RCC",
        descripcion="Servidor 172.20.0.70 (SQL; usuario master): bases DBRCC, DW_Raw_v2, dbriesgos, DW_Metadata…",
        servidor_defecto="172.20.0.70",
        windows_auth_defecto=False,
    ),
}


def obtener_servidor(nombre: str) -> Servidor:
    try:
        return SERVIDORES[nombre.lower()]
    except KeyError:
        raise ConfiguracionError(f"Servidor desconocido '{nombre}'. Opciones: {', '.join(SERVIDORES)}") from None
