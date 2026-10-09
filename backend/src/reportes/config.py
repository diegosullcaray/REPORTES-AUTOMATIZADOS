"""Configuración central: rutas del proyecto y definición de las 3 bases de datos.

Los secretos NUNCA van en el código: se leen de variables de entorno / archivo `.env`
(ver `.env.example`).
"""

from __future__ import annotations

import os
import re
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
        descripcion="Servidor MISHWBDDES01 (Windows): storage, staging, mod_rep… (reportes de actividad: cartera, castigos, saldos, seguros)",
        servidor_defecto="MISHWBDDES01",
        windows_auth_defecto=True,
    ),
    "slc": Servidor(
        nombre="slc",
        prefijo="SLC",
        descripcion="Servidor 172.24.2.213 (Windows): dwh, dma, csd, intcom, slc… (clientes, desembolsos, productos)",
        servidor_defecto="172.24.2.213",
        windows_auth_defecto=True,
    ),
    "rcc": Servidor(
        nombre="rcc",
        prefijo="RCC",
        descripcion="Servidor 172.20.0.70 (SQL; usuario master): DBRCC, dbriesgos, DW_Raw_v2, DW_Metadata, DB<AAAAMM>…",
        servidor_defecto="172.20.0.70",
        windows_auth_defecto=False,
    ),
}


# --- Dónde vive cada base de datos -----------------------------------------------------
# Fuente: explorador de objetos de SSMS de cada servidor (capturas de 2026-10). Una consulta T-SQL solo puede
# nombrar (3 partes) bases de SU servidor: por eso cada reporte se conecta al servidor de las bases que usa.
BASES_DE: dict[str, tuple[str, ...]] = {
    "mish": ("app", "gitea", "government", "inme", "junk", "metadata", "mide", "mod_app", "mod_gpa", "mod_rep",
             "mod_sec", "mod_sys_admin", "mod_sys_login", "staging", "storage", "strategos",
             "appj"),  # appj NO aparece en las capturas: se asume en MISH (tapp lo escribe en la misma sesión que lee storage). Por confirmar
    "slc": ("abp", "aud", "crs", "csd", "dbs70", "dga", "dma", "dsa", "dwh", "etl", "intcom", "mds", "mla", "sla",
            "slb", "slc", "sld", "sle", "slf", "slg", "tdj", "test_temp", "tmp", "wks",
            "rcc_cd"),  # rcc_cd es un linked server definido en 172.24.2.213 que apunta a 172.20.0.70
    "rcc": ("dbfinanzas", "dbfsh", "dbrcc", "dbriesgos", "dw_application", "dw_metadata", "dw_raw", "dw_raw_v2",
            "dw_recycle", "dw_staging", "dw_staging_v2", "dw_summary", "dw_summary_v2", "gerencia_riesgos_bd",
            "reportserver", "reportservertempdb"),  # + las bases mensuales DB<AAAAMM> (patrón, ver servidor_de_base)
}
# "DBEstudios" aparece en 172.24.2.213 y en 172.20.0.70: ambigua, ningún reporte la usa y por eso no se mapea.
_SERVIDOR_DE_BASE = {b: srv for srv, bases in BASES_DE.items() for b in bases}


def servidor_de_base(base: str) -> str:
    """Servidor (mish | slc | rcc) donde vive una base de datos. Lanza ConfiguracionError si no se conoce."""
    b = base.lower().strip("[]")
    if re.fullmatch(r"db\d{6}|db\{yyyymm\}", b):
        return "rcc"  # DB202511 … DB202610: bases mensuales del servidor 172.20.0.70
    try:
        return _SERVIDOR_DE_BASE[b]
    except KeyError:
        raise ConfiguracionError(f"No sé en qué servidor vive la base '{base}': añádela a config.BASES_DE") from None


def servidor_de_tabla(nombre: str) -> str:
    """Servidor de una tabla por su nombre de 3 partes (`base.esquema.tabla`)."""
    return servidor_de_base(nombre.split(".")[0])


def obtener_servidor(nombre: str) -> Servidor:
    try:
        return SERVIDORES[nombre.lower()]
    except KeyError:
        raise ConfiguracionError(f"Servidor desconocido '{nombre}'. Opciones: {', '.join(SERVIDORES)}") from None
