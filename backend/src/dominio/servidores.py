"""Dónde vive cada base de datos: conocimiento del negocio (qué servidor de los 3 aloja cada base), sin credenciales ni conexiones.

Las credenciales y la cadena de conexión de cada servidor son de la infraestructura (`infraestructura/configuracion.py`).
"""

from __future__ import annotations

import re

from .errores import ConfiguracionError

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
        raise ConfiguracionError(f"No sé en qué servidor vive la base '{base}': añádela a dominio/servidores.py (BASES_DE)") from None


def servidor_de_tabla(nombre: str) -> str:
    """Servidor de una tabla por su nombre de 3 partes (`base.esquema.tabla`)."""
    return servidor_de_base(nombre.split(".")[0])
