"""Acceso único a las 3 bases de datos (dw_raw, rcc, slc)."""

from __future__ import annotations

from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

from .config import DIR_SQL, obtener_base


def crear_engine(base: str) -> Engine:
    """Engine SQLAlchemy para una de las 3 bases ('dw_raw', 'rcc', 'slc')."""
    url = URL.create("mssql+pyodbc", query={"odbc_connect": obtener_base(base).cadena_odbc()})
    return create_engine(url, pool_pre_ping=True)


def leer_sql(base: str, consulta: str, params: dict | None = None) -> pd.DataFrame:
    engine = crear_engine(base)
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(consulta), conn, params=params or {})
    finally:
        engine.dispose()


def cargar_sql(ruta_relativa: str | Path) -> str:
    """Lee un archivo de `sql/` (ruta relativa a esa carpeta)."""
    return (DIR_SQL / ruta_relativa).read_text(encoding="utf-8")


@contextmanager
def conexion_pyodbc(base: str, autocommit: bool = True) -> Iterator[Any]:
    """Conexión pyodbc cruda (lotes con tablas temporales, TRUNCATE/INSERT, etc.)."""
    import pyodbc  # import local: el resto del paquete funciona sin el driver instalado

    with closing(pyodbc.connect(obtener_base(base).cadena_odbc(), autocommit=autocommit)) as conn:
        yield conn


def leer_ultimo_resultado(base: str, sql: str, params: tuple = ()) -> pd.DataFrame:
    """Ejecuta un lote en una sola sesión y devuelve el último conjunto de resultados."""
    resultado = None
    with conexion_pyodbc(base) as conn, closing(conn.cursor()) as cursor:
        cursor.execute(sql, *params)
        while True:
            if cursor.description:
                columnas = [c[0] for c in cursor.description]
                resultado = pd.DataFrame.from_records([tuple(f) for f in cursor.fetchall()], columns=columnas)
            if not cursor.nextset():
                break
    if resultado is None:
        raise RuntimeError("El lote SQL no devolvió resultados")
    return resultado


def probar_conexiones() -> dict[str, str]:
    """Devuelve 'OK' o el error de cada una de las 3 conexiones."""
    from .config import BASES

    estado = {}
    for nombre in BASES:
        try:
            leer_sql(nombre, "SELECT 1 AS ok")
            estado[nombre] = "OK"
        except Exception as exc:  # noqa: BLE001 - diagnóstico
            estado[nombre] = f"ERROR: {type(exc).__name__}: {str(exc)[:120]}"
    return estado
