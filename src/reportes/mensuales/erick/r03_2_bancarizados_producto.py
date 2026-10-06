"""
Bancarizados por producto · Clientes nuevos con desembolso en el mes.

Reemplaza a Bancarizados.sql. Genera un Excel con:
    resumen        Por categoría de producto: clientes nuevos con desembolso, bancarizados y % bancarizados
    comparativo    Bancarizados por categoría y mes (solo si se piden varios meses)
    clientes       Un registro por cliente con el producto asignado (para auditar el conteo)
    multiproducto  Clientes con desembolsos de más de un producto en el mes

Uso:
    python bancarizados_producto.py --mes 2026-06
    python bancarizados_producto.py --mes 2026-06 2025-06
    python bancarizados_producto.py --mes 2026-06 --copiar

La fecha de cierre se detecta sola (última fecha cargada en Clientes_DS dentro del mes)
y es la misma que se envía al SP de desembolsos, como en el script original.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from openpyxl.utils import get_column_letter

from ...comun.fechas import resolver_corte
from ...config import ConfiguracionError
from ...registro import carpeta_salida
from ...db import leer_ultimo_resultado as _leer_ultimo

# =============================================================================
# Configuración
# =============================================================================
BASE = "slc"  # base en el servidor slc; csd.dbo.Clientes_DS y dwh (SP de desembolsos) van por 3 partes

# Agrupación de productos del reporte; los que no están aquí se reportan con su propio nombre
AGRUPACION_PRODUCTOS = {
    "CREDITO EDUCATIVO": "CONSUMO",
    "INICIANDO CONFIANZA PYME": "EMPRENDIENDO CONFIANZA",
}
SIN_PRODUCTO = "SIN PRODUCTO"

DIR_SALIDA_DEFECTO = carpeta_salida("bancarizados-producto")
MAX_HILOS = 4

log = logging.getLogger("bancarizados_producto")


class SinDatosError(ValueError):
    """No hay datos para el mes pedido."""


# =============================================================================
# Meses y conexión
# =============================================================================
@dataclass(frozen=True, order=True)
class Mes:
    anio: int
    mes: int

    @classmethod
    def desde_texto(cls, valor: str) -> Mes:
        for formato in ("%Y-%m", "%Y-%m-%d"):
            try:
                fecha = datetime.strptime(valor, formato)
            except ValueError:
                continue
            return cls(fecha.year, fecha.month)
        raise ValueError(f"Mes inválido '{valor}', usa AAAA-MM")

    @property
    def inicio(self) -> date:
        return date(self.anio, self.mes, 1)

    @property
    def inicio_siguiente(self) -> date:
        return date(self.anio + (self.mes == 12), self.mes % 12 + 1, 1)

    def __str__(self) -> str:
        return f"{self.anio:04d}-{self.mes:02d}"


def leer_ultimo_resultado(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Lote completo en una sola sesión (el SP llena una tabla temporal); devuelve el último resultado."""
    return _leer_ultimo("slc", sql, params, base=BASE)


@contextmanager
def cronometro(etapa: str) -> Iterator[None]:
    inicio = time.perf_counter()
    log.info("▶ %s…", etapa)
    yield
    log.info("✓ %s: %.1f s", etapa, time.perf_counter() - inicio)


# =============================================================================
# SQL
# =============================================================================
SQL_RESOLVER_MES = """
WITH cierre AS (
    SELECT MAX(HFECPRO) AS fecha
    FROM csd.dbo.Clientes_DS
    WHERE HFECPRO >= ? AND HFECPRO < ?
)
SELECT
    cierre.fecha                                                      AS FECHA,
    COUNT(DISTINCT c.HCTACLI)                                         AS NUEVOS,
    COUNT(DISTINCT CASE WHEN c.HINDBANC = 1 THEN c.HCTACLI END)       AS BANCARIZADOS
FROM cierre
LEFT JOIN csd.dbo.Clientes_DS AS c ON c.HFECPRO = cierre.fecha
GROUP BY cierre.fecha;
"""

SQL_ULTIMA_FECHA = "SELECT MAX(HFECPRO) AS ULTIMA FROM csd.dbo.Clientes_DS;"

# Se eliminó del original: el SP de jerarquía (#jer_ods) y la tabla #df, que no se usaban en el resultado.
SQL_PREPARAR_DESEMBOLSOS = """
SET NOCOUNT ON;

IF OBJECT_ID('tempdb..#desem') IS NOT NULL DROP TABLE #desem;

CREATE TABLE #desem (
    HFECPRO date, HCODOPE int, HNUMDOC varchar(20), HTIPDOC smallint, HPAIS smallint,
    HCODMOD smallint, HTIPOPE smallint, HSUBTIP smallint, HCTACLI int, HCODSUC smallint,
    HCODSEC varchar(10), HFECDESA date, HMONDES numeric(17,2), HSALCAPMN numeric(17,2),
    HCODMON smallint, HNUMTAS numeric(9,6), BIDMOD int, SIDS002 int, SIDS006 int
);

EXEC dwh.dbo.GDESEMCRE001 @tbl_temp = '#desem', @fecs = {fecha};
"""

SQL_CLIENTES_PRODUCTO = """
WITH nuevos AS (
    -- Un registro por cliente nuevo; bancarizado si alguna de sus filas lo indica
    SELECT HCTACLI, MAX(CASE WHEN HINDBANC = 1 THEN 1 ELSE 0 END) AS bancarizado
    FROM csd.dbo.Clientes_DS
    WHERE HFECPRO = {fecha}
      AND HCTACLI IS NOT NULL
    GROUP BY HCTACLI
),
operaciones AS (
    -- Producto de cada desembolso vía BIDMOD, igual que #prueba en el original
    SELECT DISTINCT d.HCTACLI, d.HCODOPE, d.HFECDESA, d.HMONDES, t3.RDESPROD
    FROM #desem AS d
    LEFT JOIN dwh.dbo.BREGMOD001 AS b ON b.BIDMOD = d.BIDMOD
    LEFT JOIN dwh.dbo.RTIPCRE001 AS t1 ON t1.RCODMOD = b.BCODMOD AND t1.RTIPOPE = b.BTIPOPE
    LEFT JOIN dwh.dbo.RTIPCRE002 AS t2
        ON t2.RCODMOD = b.BCODMOD AND t2.RTIPOPE = b.BTIPOPE AND t2.RSUBTIP = b.BSUBTIP
    LEFT JOIN dwh.dbo.RTIPCRE003 AS t3 ON t3.RCODPROD = COALESCE(t2.RCODPROD, t1.RCODPROD)
    WHERE d.HFECPRO = {fecha}
)
-- Un registro por cliente y producto; la elección del producto se hace en Python con una regla fija
SELECT
    o.HCTACLI,
    n.bancarizado        AS BANCARIZADO,
    o.RDESPROD           AS PRODUCTO,
    MIN(o.HFECDESA)      AS PRIMER_DESEMBOLSO,
    MIN(o.HCODOPE)       AS PRIMERA_OPERACION,
    COUNT(*)             AS OPERACIONES,
    SUM(o.HMONDES)       AS MONTO_DESEMBOLSADO
FROM operaciones AS o
INNER JOIN nuevos AS n ON n.HCTACLI = o.HCTACLI
GROUP BY o.HCTACLI, n.bancarizado, o.RDESPROD;
"""


def sql_lote(fecha: date) -> str:
    # Fecha como literal (viene de un date validado). Sin parámetros enlazados, el lote no se
    # ejecuta dentro de sp_executesql y la tabla #desem vive en la misma sesión que el SP.
    literal = f"'{fecha:%Y%m%d}'"
    return SQL_PREPARAR_DESEMBOLSOS.format(fecha=literal) + SQL_CLIENTES_PRODUCTO.format(fecha=literal)


# =============================================================================
# Extracción
# =============================================================================
@dataclass(frozen=True)
class Cierre:
    mes: Mes
    fecha: date
    nuevos: int
    bancarizados: int


def resolver_mes(mes: Mes) -> Cierre:
    df = leer_ultimo_resultado(SQL_RESOLVER_MES, (mes.inicio, mes.inicio_siguiente))
    if df.empty or pd.isna(df.iloc[0]["FECHA"]):
        ultima = leer_ultimo_resultado(SQL_ULTIMA_FECHA).iloc[0, 0]
        disponible = pd.Timestamp(ultima).date() if pd.notna(ultima) else "ninguna"
        raise SinDatosError(f"{mes}: sin datos en Clientes_DS (última fecha disponible: {disponible})")
    fila = df.iloc[0]
    return Cierre(mes, pd.Timestamp(fila["FECHA"]).date(), int(fila["NUEVOS"]), int(fila["BANCARIZADOS"]))


def extraer_mes(mes: Mes) -> tuple[Cierre, pd.DataFrame]:
    cierre = resolver_mes(mes)
    with cronometro(f"Desembolsos y productos {cierre.fecha}"):
        df = leer_ultimo_resultado(sql_lote(cierre.fecha))
    return cierre, preparar(df, cierre)


def preparar(df: pd.DataFrame, cierre: Cierre) -> pd.DataFrame:
    df = df.rename(columns=str.upper)
    return df.assign(
        MES=str(cierre.mes),
        FECHA=pd.Timestamp(cierre.fecha),
        PRODUCTO=df["PRODUCTO"].astype("string").str.strip(),  # CHAR con espacios no rompe la agrupación
        BANCARIZADO=pd.to_numeric(df["BANCARIZADO"]).fillna(0).astype("int64"),
        PRIMER_DESEMBOLSO=pd.to_datetime(df["PRIMER_DESEMBOLSO"]),
        OPERACIONES=pd.to_numeric(df["OPERACIONES"]).astype("int64"),
        MONTO_DESEMBOLSADO=pd.to_numeric(df["MONTO_DESEMBOLSADO"]).astype("float64"),
    )


# =============================================================================
# Transformación
# =============================================================================
def categorizar(productos: pd.Series) -> pd.Series:
    return productos.replace(AGRUPACION_PRODUCTOS).fillna(SIN_PRODUCTO).astype("object")


def asignar_producto(df: pd.DataFrame) -> pd.DataFrame:
    """Un producto por cliente: el de su primer desembolso con producto identificado.

    El original usaba ROW_NUMBER() ... ORDER BY (SELECT NULL): con varios productos,
    el elegido era arbitrario y podía cambiar entre ejecuciones.
    """
    llave = ["MES", "HCTACLI"]
    productos_en_mes = df.groupby(llave)["PRODUCTO"].nunique().rename("PRODUCTOS_EN_MES")
    return (
        df.assign(_sin_producto=df["PRODUCTO"].isna())
        .sort_values([*llave, "_sin_producto", "PRIMER_DESEMBOLSO", "PRIMERA_OPERACION"], kind="stable")
        .drop_duplicates(llave)
        .drop(columns="_sin_producto")
        .join(productos_en_mes, on=llave)
        .assign(CATEGORIA=lambda d: categorizar(d["PRODUCTO"]))
        .reset_index(drop=True)
    )


def resumen_por_categoria(clientes: pd.DataFrame) -> pd.DataFrame:
    metricas = {"CLIENTES_NUEVOS": ("HCTACLI", "size"), "BANCARIZADOS": ("BANCARIZADO", "sum")}
    por_categoria = clientes.groupby(["MES", "FECHA", "CATEGORIA"], as_index=False).agg(**metricas)
    total = clientes.groupby(["MES", "FECHA"], as_index=False).agg(**metricas).assign(CATEGORIA="TOTAL")
    return (
        pd.concat([por_categoria, total], ignore_index=True)
        .assign(
            PCT_BANCARIZADOS=lambda d: d["BANCARIZADOS"] / d["CLIENTES_NUEVOS"],
            _total=lambda d: d["CATEGORIA"].eq("TOTAL"),
        )
        .sort_values(["MES", "_total", "CATEGORIA"], ascending=[False, True, True], kind="stable")
        .drop(columns="_total")
        .reset_index(drop=True)
    )


def comparativo(resumen: pd.DataFrame) -> pd.DataFrame:
    tabla = resumen.pivot_table(index="CATEGORIA", columns="MES", values="BANCARIZADOS", aggfunc="sum", fill_value=0)
    orden = sorted(tabla.index.drop("TOTAL", errors="ignore")) + (["TOTAL"] if "TOTAL" in tabla.index else [])
    return tabla.reindex(orden).reset_index().rename_axis(columns=None)


def diagnosticar(cierre: Cierre, clientes: pd.DataFrame) -> None:
    del_mes = clientes[clientes["MES"] == str(cierre.mes)]
    bancarizados = int(del_mes["BANCARIZADO"].sum())
    multiproducto = int((del_mes["PRODUCTOS_EN_MES"] > 1).sum())
    sin_producto = int(((del_mes["CATEGORIA"] == SIN_PRODUCTO) & (del_mes["BANCARIZADO"] == 1)).sum())

    cobertura = bancarizados / cierre.bancarizados if cierre.bancarizados else float("nan")
    log.info(
        "%s (cierre %s): %s bancarizados con desembolso de %s bancarizados en Clientes_DS (%.1f%%)",
        cierre.mes, cierre.fecha, f"{bancarizados:,}", f"{cierre.bancarizados:,}", 100 * cobertura,
    )
    if multiproducto:
        log.info("  %s clientes con más de un producto en el mes: se asignó el del primer desembolso",
                 f"{multiproducto:,}")
    if sin_producto:
        log.warning("  %s bancarizados sin producto en RTIPCRE003 (se reportan como %s)",
                    f"{sin_producto:,}", SIN_PRODUCTO)


def exportar_excel(hojas: dict[str, pd.DataFrame], ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(ruta, engine="openpyxl", datetime_format="yyyy-mm-dd", date_format="yyyy-mm-dd") as writer:
        for nombre, df in hojas.items():
            df.to_excel(writer, sheet_name=nombre, index=False)
            hoja = writer.sheets[nombre]
            hoja.freeze_panes = "A2"
            for i, columna in enumerate(df.columns, start=1):
                letra = get_column_letter(i)
                hoja.column_dimensions[letra].width = max(12, len(str(columna)) + 2)
                if str(columna).startswith("PCT_"):
                    formato = "0.0%"
                elif columna == "MONTO_DESEMBOLSADO":
                    formato = "#,##0.00"
                else:
                    continue
                for celda in hoja[letra][1:]:
                    celda.number_format = formato
    return ruta


# =============================================================================
# CLI
# =============================================================================
def tipo_mes(valor: str) -> Mes:
    try:
        return Mes.desde_texto(valor)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def parsear_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bancarizados por producto (clientes nuevos con desembolso).")
    parser.add_argument("--mes", type=tipo_mes, nargs="+", help="Uno o más meses AAAA-MM (defecto: el mes de FECHA_CORTE_MENSUAL del .env)")
    parser.add_argument("--salida", type=Path, default=DIR_SALIDA_DEFECTO, help="Carpeta de salida (defecto: data/outputs/<reporte>)")
    parser.add_argument("--copiar", action="store_true",
                        help="Copia CATEGORIA y BANCARIZADOS del primer mes al portapapeles, como el SQL original")
    parser.add_argument("-v", "--verbose", action="store_true", help="Log detallado")
    args = parser.parse_args(argv)
    if not args.mes:
        try:
            corte, origen = resolver_corte("mensual")
        except ConfiguracionError as exc:
            parser.error(str(exc))
        args.mes = [tipo_mes(f"{corte:%Y-%m}")]
        print(f"Mes: {corte:%Y-%m} ({origen})")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parsear_argumentos(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    meses = list(dict.fromkeys(args.mes))  # sin repetidos, en el orden pedido

    cierres, partes, errores = [], [], []
    with ThreadPoolExecutor(max_workers=min(len(meses), MAX_HILOS)) as pool:
        futuros = [(mes, pool.submit(extraer_mes, mes)) for mes in meses]
        for mes, futuro in futuros:
            try:
                cierre, df = futuro.result()
                cierres.append(cierre)
                partes.append(df)
            except SinDatosError as exc:
                errores.append(str(exc))
            except Exception as exc:  # noqa: BLE001 - se reporta y siguen los demás meses
                log.debug("Detalle del error en %s", mes, exc_info=True)
                errores.append(f"{mes}: {type(exc).__name__}: {exc}")

    for mensaje in errores:
        log.error("%s", mensaje)
    if not partes:
        return 1

    clientes = asignar_producto(pd.concat(partes, ignore_index=True))
    for cierre in cierres:
        diagnosticar(cierre, clientes)

    resumen = resumen_por_categoria(clientes)
    log.info("Resumen:\n%s", resumen.to_string(index=False, float_format="{:.3f}".format))

    hojas = {"resumen": resumen}
    if len(cierres) > 1:
        hojas["comparativo"] = comparativo(resumen)
    hojas["clientes"] = clientes
    hojas["multiproducto"] = (
        pd.concat(partes, ignore_index=True)
        .merge(clientes.loc[clientes["PRODUCTOS_EN_MES"] > 1, ["MES", "HCTACLI"]], on=["MES", "HCTACLI"])
        .sort_values(["MES", "HCTACLI", "PRIMER_DESEMBOLSO"])
    )

    try:
        sufijo = "_".join(f"{c.fecha:%Y%m%d}" for c in cierres)
        ruta = exportar_excel(hojas, args.salida / f"BancarizadosProducto_{sufijo}.xlsx")
        log.info("Excel guardado en: %s", ruta.resolve())
        if args.copiar:
            primero = resumen[(resumen["MES"] == str(cierres[0].mes)) & (resumen["CATEGORIA"] != "TOTAL")]
            primero.loc[primero["BANCARIZADOS"] > 0, ["CATEGORIA", "BANCARIZADOS"]].to_clipboard(
                index=False, header=False
            )
            log.info("Bancarizados por categoría de %s copiados al portapapeles", cierres[0].mes)
    except OSError as exc:  # p. ej. el Excel está abierto
        log.error("%s", exc)
        return 1

    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
