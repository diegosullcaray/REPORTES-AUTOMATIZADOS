"""Adaptador del puerto de entorno: variables del `.env` y del proceso, carpetas de datos y corte configurado.

Edición acotada del .env: cambia o quita solo las claves indicadas y deja intacto el resto (secretos incluidos).
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

from dotenv import dotenv_values

from aplicacion.puertos import InfoServidor
from dominio import fechas

from . import configuracion as cfg

ENV = cfg.RAIZ / ".env"

_CLAVE = re.compile(r"\s*([A-Z][A-Z0-9_]*)\s*=")


def escribir(ruta: Path, cambios: dict[str, str]) -> None:
    """`cambios[clave] = valor`; valor vacío quita la línea. Los valores ya vienen validados (sin saltos de línea, `#` ni comillas)."""
    pendientes = dict(cambios)
    salida: list[str] = []
    for linea in ruta.read_text(encoding="utf-8").splitlines() if ruta.exists() else []:
        m = _CLAVE.match(linea)
        if m and m.group(1) in pendientes:
            valor = pendientes.pop(m.group(1))
            if valor:
                salida.append(f"{m.group(1)}={valor}")
        else:
            salida.append(linea)
    salida += [f"{k}={v}" for k, v in pendientes.items() if v]
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_text("\n".join(salida) + "\n", encoding="utf-8")
    os.replace(temporal, ruta)  # reemplazo atómico: nunca queda un .env a medias


# ---------------------------------------------------------------- puerto Entorno
def leer(variable: str, defecto: str = "") -> str:
    return os.getenv(variable, defecto)


def guardar(cambios: dict[str, str], al_proceso: list[str] | None = None) -> None:
    """Escribe en el .env y, en el proceso, las variables de `al_proceso` (todas si es None): las ejecuciones heredan el entorno de la API."""
    escribir(ENV, cambios)
    for variable in cambios if al_proceso is None else al_proceso:
        if cambios.get(variable):
            os.environ[variable] = cambios[variable]
        else:
            os.environ.pop(variable, None)


def guardado() -> dict[str, str | None]:
    return dotenv_values(ENV) if ENV.exists() else {}


def corte(frecuencia: str) -> date | None:
    return fechas.corte_desde_texto(frecuencia, os.getenv(fechas.VAR_CORTE[frecuencia], ""))


def raiz() -> Path:
    return cfg.RAIZ


def dir_inputs() -> Path:
    return cfg.DIR_INPUTS


def dir_outputs() -> Path:
    return cfg.DIR_OUTPUTS


def driver_odbc() -> str:
    return cfg.DRIVER_ODBC


def servidores() -> list[InfoServidor]:
    return [
        InfoServidor(nombre=s.nombre, servidor=s.servidor, autenticacion="SQL" if (s.usuario or not s.windows_auth_defecto) else "Windows",
                     credenciales_en_env=bool(s.usuario and s.clave), descripcion=s.descripcion)
        for s in cfg.SERVIDORES.values()
    ]
