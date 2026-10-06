"""
Bancarizados · Clientes exclusivos de Financiera Confianza.

Para un corte mensual genera un Excel con cuatro reportes:
    exclusivos_total  Clientes cuya deuda crediticia en el RCC está 100 % en la empresa
    productos_total   Exclusivos por producto (cartera Nuevo + Stock)
    productos_nuevos  Exclusivos por producto, solo cartera Nuevo
    territorio        Exclusivos por territorio del sectorista principal

Uso:
    python bancarizados.py --fecha-corte 2026-06-30
    python bancarizados.py --fecha-corte 2026-06-30 --sin-cache --copiar productos_nuevos

Conexiones: RCC (DBRCC) y SLC, definidas en reportes.config / .env (ver .env.example).
"""

from __future__ import annotations

import argparse
import calendar
import logging
import sys
import time
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from ..config import DIR_SALIDAS, ConfiguracionError
from ..db import leer_sql as _leer_sql

# =============================================================================
# Configuración
# =============================================================================
EMPRESA = "FINANCIERA CONFIANZA"

SERVIDOR_RCC = "rcc"  # DBRCC
SERVIDOR_SLC = "slc"  # slc (+ INTCOM, DWH, csd)

DIR_SALIDA_DEFECTO = DIR_SALIDAS / "bancarizados"
LLAVE = ["TIPO_DOC", "NUM_DOC"]
REPORTES = ("exclusivos_total", "productos_total", "productos_nuevos", "territorio")

log = logging.getLogger("bancarizados")


# =============================================================================
# Periodo, conexiones y caché
# =============================================================================
@dataclass(frozen=True)
class Periodo:
    """Deriva todas las fechas y sufijos de tabla a partir del corte mensual."""

    fecha_corte: date

    def __post_init__(self) -> None:
        ultimo_dia = calendar.monthrange(self.fecha_corte.year, self.fecha_corte.month)[1]
        if self.fecha_corte.day != ultimo_dia:
            raise ValueError(f"La fecha de corte debe ser fin de mes; se recibió {self.fecha_corte}")

    @property
    def inicio_mes(self) -> date:
        return self.fecha_corte.replace(day=1)

    @property
    def inicio_mes_siguiente(self) -> date:
        return self.fecha_corte + timedelta(days=1)

    @property
    def yyyymmdd(self) -> str:
        return f"{self.fecha_corte:%Y%m%d}"

    @property
    def yyyymm(self) -> str:
        return f"{self.fecha_corte:%Y%m}"

    @property
    def params_sql(self) -> dict[str, date]:
        return {"inicio_mes": self.inicio_mes, "inicio_mes_sig": self.inicio_mes_siguiente}


def leer_sql(base: str, consulta: str, params: dict) -> pd.DataFrame:
    return _leer_sql(base, consulta, params)


@contextmanager
def cronometro(etapa: str) -> Iterator[None]:
    inicio = time.perf_counter()
    log.info("▶ %s…", etapa)
    yield
    log.info("✓ %s: %.1f s", etapa, time.perf_counter() - inicio)


def leer_con_cache(
    nombre: str,
    extraer: Callable[[Periodo], pd.DataFrame],
    periodo: Periodo,
    usar_cache: bool,
    dir_salida: Path,
) -> pd.DataFrame:
    """Evita repetir consultas pesadas al volver a correr el mismo corte."""
    ruta = dir_salida / "cache" / f"{nombre}_{periodo.yyyymmdd}.pkl"
    if usar_cache and ruta.exists():
        log.info("↺ %s: leído de caché (%s)", nombre, ruta)
        return pd.read_pickle(ruta)

    with cronometro(f"Extrayendo {nombre}"):
        df = extraer(periodo)
    log.info("  %s: %s filas", nombre, f"{len(df):,}")

    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(ruta)
    return df


# =============================================================================
# Consultas SQL
# =============================================================================
def sql_clientes_exclusivos(p: Periodo) -> str:
    """Un registro por cliente exclusivo con su CARTERA (Nuevo/Stock) y TERRITORIO.

    Solo los nombres de tabla van por f-string (derivados de una fecha validada);
    los valores van como parámetros enlazados.
    """
    return f"""
WITH deuda AS (
    SELECT
        A.FECHA,
        T.TIPO_DOC,
        D.NUM_DOC,
        A.DESC_EMPRESA,
        A.SALDO
    FROM DBRCC.dbo.RCCDET{p.yyyymmdd} AS A
    LEFT JOIN DBRCC.dbo.RCCCAB{p.yyyymmdd} AS B
        ON B.CODIGOSBS = A.CODIGOSBS
    CROSS APPLY (
        SELECT
            ISNULL(B.TDOC_IDENT, B.TDOC_TRIB) AS TDOC,
            ISNULL(B.NDOC_IDENT, B.NDOC_TRIB) AS NUM_DOC
    ) AS D
    CROSS APPLY (
        SELECT CASE WHEN D.TDOC = 1 THEN 21
                    WHEN D.TDOC = 3 THEN 9
                    ELSE D.TDOC END AS TIPO_DOC
    ) AS T
    WHERE A.GRUPO1 = 'CREDITO'
      AND (B.TDOC_IDENT IS NULL OR (B.TDOC_IDENT NOT LIKE '%A%' AND B.TDOC_IDENT NOT LIKE '%B%'))
      AND D.NUM_DOC IS NOT NULL  -- Deuda sin documento no es un cliente identificable
),
exclusivos AS (
    SELECT FECHA, TIPO_DOC, NUM_DOC
    FROM deuda
    GROUP BY FECHA, TIPO_DOC, NUM_DOC
    HAVING SUM(CASE WHEN DESC_EMPRESA = CAST(:empresa AS VARCHAR(100)) THEN SALDO ELSE 0 END) = SUM(SALDO)
       AND SUM(CASE WHEN DESC_EMPRESA = CAST(:empresa AS VARCHAR(100)) THEN SALDO ELSE 0 END) > 0
),
sectorista AS (
    SELECT
        TIPO_DOC,
        NUM_DOC,
        SECTORISTA_OPERATIVO AS SECTORISTA,
        ROW_NUMBER() OVER (
            PARTITION BY TIPO_DOC, NUM_DOC
            ORDER BY SUM(SAL_CAPITAL_MN) DESC, SECTORISTA_OPERATIVO  -- desempate determinístico
        ) AS NRO
    FROM DB{p.yyyymm}.dbo.CCD{p.yyyymmdd}
    WHERE FECHA_CIERRE >= :inicio_mes AND FECHA_CIERRE < :inicio_mes_sig
    GROUP BY TIPO_DOC, NUM_DOC, SECTORISTA_OPERATIVO
),
territorio AS (
    -- Un territorio por sectorista: evita duplicar clientes si hay varias filas en el mes
    SELECT RCODSEC, MAX(RDESTER) AS TERRITORIO
    FROM DW_Metadata.dbo.WJERCOR03
    WHERE RFECPRO >= :inicio_mes AND RFECPRO < :inicio_mes_sig
    GROUP BY RCODSEC
)
SELECT
    E.FECHA,
    CAST(E.TIPO_DOC AS VARCHAR(5)) AS TIPO_DOC,
    E.NUM_DOC,
    CASE WHEN EXISTS (
        SELECT 1
        FROM DW_RAW.dbo.CLIENTES AS C
        WHERE C.HTIPDOC = E.TIPO_DOC
          AND C.HNUMDOC = E.NUM_DOC
          AND C.HCODGRU IN ('CC', 'CA')
          AND C.HFECPRO < DATEADD(MONTH, DATEDIFF(MONTH, 0, E.FECHA), 0)  -- antes del mes de corte
    ) THEN 'Stock' ELSE 'Nuevo' END AS CARTERA,
    T.TERRITORIO
FROM exclusivos AS E
LEFT JOIN sectorista AS S
    ON S.TIPO_DOC = E.TIPO_DOC AND S.NUM_DOC = E.NUM_DOC AND S.NRO = 1
LEFT JOIN territorio AS T
    ON T.RCODSEC = S.SECTORISTA;
"""


SQL_PRODUCTOS = """
SELECT DISTINCT
    C.TIPO_DOC,
    C.NUM_DOC,
    P.PRODUCTO
FROM INTCOM.dbo.ccd AS C
INNER JOIN INTCOM.dbo.AN_PRODUCTOS AS P
    ON P.MODULO = C.MODULO AND P.TIPO_OPE = C.TIPO_OPE
WHERE C.FECHA_CIERRE >= :inicio_mes AND C.FECHA_CIERRE < :inicio_mes_sig
  AND P.PRODUCTO IS NOT NULL;
"""


def extraer_clientes(p: Periodo) -> pd.DataFrame:
    return leer_sql(SERVIDOR_RCC, sql_clientes_exclusivos(p), {**p.params_sql, "empresa": EMPRESA})


def extraer_productos(p: Periodo) -> pd.DataFrame:
    return leer_sql(SERVIDOR_SLC, SQL_PRODUCTOS, p.params_sql)


# =============================================================================
# Transformaciones y validaciones
# =============================================================================
def normalizar_llaves(df: pd.DataFrame) -> pd.DataFrame:
    """Llave como texto limpio (sin espacios ni '.0') para cruzar datos de servidores distintos."""
    return df.assign(**{
        col: df[col].astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
        for col in LLAVE
    })


def preparar_clientes(df: pd.DataFrame) -> pd.DataFrame:
    return normalizar_llaves(df).assign(FECHA=lambda d: pd.to_datetime(d["FECHA"]).dt.normalize())


def preparar_productos(df: pd.DataFrame) -> pd.DataFrame:
    return normalizar_llaves(df).drop_duplicates([*LLAVE, "PRODUCTO"], ignore_index=True)


def validar_clientes(clientes: pd.DataFrame, p: Periodo) -> None:
    if clientes.empty:
        raise ValueError(f"La consulta de clientes no devolvió filas para {p.fecha_corte}")

    duplicados = int(clientes.duplicated(LLAVE).sum())
    if duplicados:
        raise ValueError(f"{duplicados:,} clientes duplicados: revisar joins de sectorista/territorio")

    fechas = set(clientes["FECHA"].dt.date.unique())
    if fechas != {p.fecha_corte}:
        log.warning("FECHA del RCC %s no coincide con el corte %s", sorted(fechas), p.fecha_corte)


def diagnostico_cruce(clientes: pd.DataFrame, productos: pd.DataFrame) -> pd.DataFrame:
    """% de exclusivos con al menos un producto. Un % muy bajo suele indicar llaves con formatos distintos."""
    llaves_con_producto = productos[LLAVE].drop_duplicates()
    marca = clientes[LLAVE].merge(llaves_con_producto, on=LLAVE, how="left", indicator=True)["_merge"]
    return (
        clientes.assign(CON_PRODUCTO=marca.eq("both").to_numpy())
        .groupby("CARTERA")
        .agg(CLIENTES=("NUM_DOC", "size"), CON_PRODUCTO=("CON_PRODUCTO", "sum"))
        .assign(PCT_CRUCE=lambda d: (d["CON_PRODUCTO"] / d["CLIENTES"]).round(4))
    )


def resumen_exclusivos(clientes: pd.DataFrame) -> pd.DataFrame:
    return clientes.groupby("FECHA").size().reset_index(name="CLIENTES")


def clientes_por_producto(
    clientes: pd.DataFrame, productos: pd.DataFrame, cartera: str | None = None
) -> pd.DataFrame:
    base = clientes if cartera is None else clientes[clientes["CARTERA"] == cartera]
    return (
        base[["FECHA", *LLAVE]]
        .merge(productos, on=LLAVE, how="inner", validate="one_to_many")
        .drop_duplicates(["FECHA", "PRODUCTO", *LLAVE])
        .groupby(["FECHA", "PRODUCTO"])
        .size()
        .reset_index(name="CLIENTES")
    )


def clientes_por_territorio(clientes: pd.DataFrame) -> pd.DataFrame:
    return (
        clientes.groupby(["FECHA", "TERRITORIO"], dropna=False)
        .size()
        .reset_index(name="CLIENTES")
        .sort_values(["FECHA", "TERRITORIO"], na_position="first", kind="stable")
        .fillna({"TERRITORIO": "NULL"})
        .reset_index(drop=True)
    )


def construir_reportes(clientes: pd.DataFrame, productos: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "exclusivos_total": resumen_exclusivos(clientes),
        "productos_total": clientes_por_producto(clientes, productos),
        "productos_nuevos": clientes_por_producto(clientes, productos, cartera="Nuevo"),
        "territorio": clientes_por_territorio(clientes),
    }


def exportar_excel(reportes: dict[str, pd.DataFrame], ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(ruta, engine="openpyxl", datetime_format="yyyy-mm-dd") as writer:
        for nombre, df in reportes.items():
            df.to_excel(writer, sheet_name=nombre[:31], index=False)
    return ruta


# =============================================================================
# Orquestación
# =============================================================================
def ejecutar(periodo: Periodo, dir_salida: Path, usar_cache: bool = True) -> dict[str, pd.DataFrame]:
    log.info("Corte %s · RCC%s · DB%s", periodo.fecha_corte, periodo.yyyymmdd, periodo.yyyymm)

    # Servidores distintos: en paralelo, el tiempo total es el de la consulta más lenta
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_clientes = pool.submit(
            leer_con_cache, "clientes_exclusivos", extraer_clientes, periodo, usar_cache, dir_salida
        )
        fut_productos = pool.submit(
            leer_con_cache, "productos_ccd", extraer_productos, periodo, usar_cache, dir_salida
        )
        clientes = preparar_clientes(fut_clientes.result())
        productos = preparar_productos(fut_productos.result())

    validar_clientes(clientes, periodo)
    log.info("Diagnóstico de cruce con productos:\n%s", diagnostico_cruce(clientes, productos).to_string())

    reportes = construir_reportes(clientes, productos)
    for nombre, df in reportes.items():
        log.info("=== %s (%d filas) ===\n%s", nombre, len(df), df.to_string(index=False))
    return reportes


def fecha_iso(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Fecha inválida '{valor}', usa AAAA-MM-DD") from exc


def parsear_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clientes exclusivos (bancarizados) por corte mensual.",
    )
    parser.add_argument("--fecha-corte", type=fecha_iso, required=True, help="Fin de mes, AAAA-MM-DD")
    parser.add_argument("--salida", type=Path, default=DIR_SALIDA_DEFECTO, help="Carpeta de salida (defecto: salidas)")
    parser.add_argument("--sin-cache", action="store_true", help="Fuerza re-extraer desde los servidores")
    parser.add_argument("--copiar", choices=REPORTES, help="Copia un reporte al portapapeles (sin encabezados)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Log detallado")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parsear_argumentos(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        periodo = Periodo(args.fecha_corte)
        reportes = ejecutar(periodo, args.salida, usar_cache=not args.sin_cache)
        ruta = exportar_excel(reportes, args.salida / f"Bancarizados_{periodo.yyyymmdd}.xlsx")
        log.info("Reportes guardados en: %s", ruta.resolve())

        if args.copiar:
            reportes[args.copiar].to_clipboard(index=False, header=False)
            log.info("'%s' copiado al portapapeles", args.copiar)
    except (ConfiguracionError, ValueError, OSError) as exc:  # OSError: p. ej. Excel abierto
        log.error("%s", exc)
        return 1
    except Exception:
        log.exception("Error inesperado")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
