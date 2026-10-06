"""Acceso único a las 3 bases de datos (dw_raw, rcc, slc)."""

from __future__ import annotations

from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

from .config import ConfiguracionError, obtener_base


def crear_engine(base: str) -> Engine:
    """Engine SQLAlchemy para una de las 3 bases ('dw_raw', 'rcc', 'slc')."""
    url = URL.create("mssql+pyodbc", query={"odbc_connect": obtener_base(base).cadena_odbc()})
    try:
        return create_engine(url, pool_pre_ping=True)
    except ImportError as exc:
        raise ConfiguracionError("Falta el driver ODBC / pyodbc: instala «ODBC Driver 17 for SQL Server» y `pip install -r requirements.txt`") from exc


def leer_sql(base: str, consulta: str, params: dict | None = None) -> pd.DataFrame:
    engine = crear_engine(base)
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(consulta), conn, params=params or {})
    finally:
        engine.dispose()


@contextmanager
def conexion_pyodbc(base: str, autocommit: bool = True) -> Iterator[Any]:
    """Conexión pyodbc cruda (lotes con tablas temporales, TRUNCATE/INSERT, etc.)."""
    try:
        import pyodbc  # import local: el resto del paquete funciona sin el driver instalado
    except ImportError as exc:
        raise ConfiguracionError("Falta el driver ODBC / pyodbc: instala «ODBC Driver 17 for SQL Server» y `pip install -r requirements.txt`") from exc

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


def partir_lotes(sql: str) -> list[str]:
    """Separa un script T-SQL en lotes por las líneas `GO` (que no es T-SQL: es separador de SSMS)."""
    import re

    return [b for b in re.split(r"(?im)^\s*GO\s*(?:--.*)?$", sql) if b.strip()]


def _columnas_unicas(nombres: list[str]) -> list[str]:
    """Excel/pandas toleran mal columnas sin nombre (COUNT(*) sin alias) o repetidas."""
    vistos: dict[str, int] = {}
    salida = []
    for i, n in enumerate(nombres, 1):
        n = n or f"col{i}"
        vistos[n] = vistos.get(n, 0) + 1
        salida.append(n if vistos[n] == 1 else f"{n}_{vistos[n]}")
    return salida


def ejecutar_lote(base: str, sql: str) -> list[pd.DataFrame]:
    """Ejecuta un script T-SQL completo en UNA sesión (tablas temporales, USE, EXEC) y devuelve cada resultado con filas/columnas.

    Un resultado sin filas pero con columnas se devuelve como DataFrame vacío (vacío válido); las sentencias sin resultado
    (INSERT, SELECT INTO, PRINT…) se ignoran.
    """
    resultados: list[pd.DataFrame] = []
    with conexion_pyodbc(base) as conn, closing(conn.cursor()) as cursor:
        for i, lote in enumerate(partir_lotes(sql)):
            cursor.execute(("SET NOCOUNT ON;\n" if i == 0 else "") + lote)
            while True:
                if cursor.description:
                    columnas = _columnas_unicas([c[0] for c in cursor.description])
                    resultados.append(pd.DataFrame.from_records([tuple(f) for f in cursor.fetchall()], columns=columnas))
                if not cursor.nextset():
                    break
    return resultados


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
