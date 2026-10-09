"""Acceso único a los 3 servidores (mish, slc, rcc). Cada llamada puede pedir su base de datos con `base=`."""

from __future__ import annotations

from contextlib import closing, contextmanager
from typing import Any, Iterator

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

from .config import ConfiguracionError, obtener_servidor


def crear_engine(servidor: str, base: str | None = None, timeout: int | None = None) -> Engine:
    """Engine SQLAlchemy para uno de los 3 servidores ('mish', 'slc', 'rcc'); `base` = catálogo opcional; `timeout` = segundos máximos de inicio de sesión."""
    url = URL.create("mssql+pyodbc", query={"odbc_connect": obtener_servidor(servidor).cadena_odbc(base)})
    try:
        return create_engine(url, pool_pre_ping=True, connect_args={"timeout": timeout} if timeout else {})
    except ImportError as exc:
        raise ConfiguracionError("Falta el driver ODBC / pyodbc: instala «ODBC Driver 17 for SQL Server» y `pip install -r requirements.txt`") from exc


def leer_sql(servidor: str, consulta: str, params: dict | None = None, base: str | None = None, timeout: int | None = None) -> pd.DataFrame:
    engine = crear_engine(servidor, base, timeout)
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(consulta), conn, params=params or {})
    finally:
        engine.dispose()


@contextmanager
def conexion_pyodbc(servidor: str, base: str | None = None, autocommit: bool = True) -> Iterator[Any]:
    """Conexión pyodbc cruda (lotes con tablas temporales, TRUNCATE/INSERT, etc.)."""
    try:
        import pyodbc  # import local: el resto del paquete funciona sin el driver instalado
    except ImportError as exc:
        raise ConfiguracionError("Falta el driver ODBC / pyodbc: instala «ODBC Driver 17 for SQL Server» y `pip install -r requirements.txt`") from exc

    with closing(pyodbc.connect(obtener_servidor(servidor).cadena_odbc(base), autocommit=autocommit)) as conn:
        yield conn


def leer_ultimo_resultado(servidor: str, sql: str, params: tuple = (), base: str | None = None) -> pd.DataFrame:
    """Ejecuta un lote en una sola sesión y devuelve el último conjunto de resultados."""
    resultado = None
    with conexion_pyodbc(servidor, base) as conn, closing(conn.cursor()) as cursor:
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


def ejecutar_lote(servidor: str, sql: str, base: str | None = None) -> list[pd.DataFrame]:
    """Ejecuta un script T-SQL completo en UNA sesión (tablas temporales, USE, EXEC) y devuelve cada resultado con filas/columnas.

    Un resultado sin filas pero con columnas se devuelve como DataFrame vacío (vacío válido); las sentencias sin resultado
    (INSERT, SELECT INTO, PRINT…) se ignoran.
    """
    resultados: list[pd.DataFrame] = []
    with conexion_pyodbc(servidor, base) as conn, closing(conn.cursor()) as cursor:
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
    """Devuelve 'OK' o el error de cada uno de los 3 servidores."""
    from .config import SERVIDORES

    estado = {}
    for nombre in SERVIDORES:
        try:
            leer_sql(nombre, "SELECT 1 AS ok")
            estado[nombre] = "OK"
        except Exception as exc:  # noqa: BLE001 - diagnóstico
            estado[nombre] = f"ERROR: {type(exc).__name__}: {str(exc)[:120]}"
    return estado
