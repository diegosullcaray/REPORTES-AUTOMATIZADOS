"""
Indicadores de clientes para el Directorio · Créditos, Nuevos, Pasivos y Seguros.

Reemplaza a creditosql.sql, pasivos.sql y Seguros.sql. Para cada reporte calcula el mes
actual y el mismo mes del año anterior, y genera un Excel con:
    resumen  Indicador por categoría: clientes, participación sobre el total y variación anual
    detalle  Resultado de cada consulta en formato largo

Uso:
    python indicadores_clientes.py --mes 2026-07
    python indicadores_clientes.py --mes 2026-07 --reportes pasivos seguros
    python indicadores_clientes.py --mes 2026-07 --desfase seguros=2 --copiar resumen

Fechas:
    --mes es el mes de Créditos y Pasivos. Nuevos y Seguros usan un mes antes (desfase 1),
    configurable con --desfase. La fecha de cierre se detecta sola: se toma la última fecha
    cargada dentro del mes, así que un cierre al 29 o 30 no requiere cambios.
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
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

# =============================================================================
# Configuración
# =============================================================================
# Ambos apuntan al 213 (ahí se consultó INTCOM en los scripts anteriores).
# Si INTCOM/DWH están en otro servidor, cambia solo SERVIDOR_INTCOM.
SERVIDOR_INTCOM = {"servidor": "172.24.2.213", "base": "INTCOM"}  # INTCOM y DWH
SERVIDOR_213 = {"servidor": "172.24.2.213", "base": "slc"}  # csd.dbo.Clientes_DS

DIR_SALIDA_DEFECTO = Path("salidas")
HILOS_DEFECTO = 4  # Consultas simultáneas contra el servidor
ORDEN_INDICADORES = ["TOTAL", "GENERO", "RURALIDAD", "EDAD", "BANCARIZACION"]
COLUMNAS_SQL = ["FECHA", "INDICADOR", "CATEGORIA", "CLIENTES"]
COLUMNAS_DETALLE = ["REPORTE", "PERIODO", "MES", *COLUMNAS_SQL]

log = logging.getLogger("indicadores_clientes")


class SinDatosError(ValueError):
    """La consulta no encontró datos para el mes pedido."""


# =============================================================================
# Meses y conexiones
# =============================================================================
@dataclass(frozen=True, order=True)
class Mes:
    anio: int
    mes: int

    def __post_init__(self) -> None:
        if not 1 <= self.mes <= 12:
            raise ValueError(f"Mes inválido: {self.mes}")

    @classmethod
    def desde_texto(cls, valor: str) -> Mes:
        for formato in ("%Y-%m", "%Y-%m-%d"):
            try:
                fecha = datetime.strptime(valor, formato)
            except ValueError:
                continue
            return cls(fecha.year, fecha.month)
        raise ValueError(f"Mes inválido '{valor}', usa AAAA-MM")

    def desplazar(self, meses: int) -> Mes:
        total = self.anio * 12 + (self.mes - 1) + meses
        return Mes(total // 12, total % 12 + 1)

    @property
    def inicio(self) -> date:
        return date(self.anio, self.mes, 1)

    @property
    def inicio_siguiente(self) -> date:
        return self.desplazar(1).inicio

    def __str__(self) -> str:
        return f"{self.anio:04d}-{self.mes:02d}"


def crear_engine(servidor: str, base: str) -> Engine:
    """Engine de SQL Server con autenticación de Windows."""
    odbc = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={servidor};DATABASE={base};Trusted_Connection=yes"
    return create_engine(URL.create("mssql+pyodbc", query={"odbc_connect": odbc}), pool_pre_ping=True)


def leer_sql(config_servidor: dict, consulta: str, params: dict | None = None) -> pd.DataFrame:
    engine = crear_engine(**config_servidor)
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(consulta), conn, params=params or {})
    finally:
        engine.dispose()


@contextmanager
def cronometro(etapa: str) -> Iterator[None]:
    inicio = time.perf_counter()
    log.info("▶ %s…", etapa)
    yield
    log.info("✓ %s: %.1f s", etapa, time.perf_counter() - inicio)


# =============================================================================
# SQL
# =============================================================================
# Cada consulta devuelve FECHA, INDICADOR, CATEGORIA, CLIENTES para un solo mes.
# Sin tablas temporales: una sola instrucción por reporte, con parámetros enlazados.


def declarar_fecha(tabla: str, columna: str) -> str:
    """Última fecha cargada dentro del mes: resuelve cierres al 29/30 sin tocar el código."""
    return f"""SET NOCOUNT ON;
DECLARE @fecha DATETIME = (
    SELECT MAX({columna}) FROM {tabla}
    WHERE {columna} >= :inicio_mes AND {columna} < :inicio_mes_sig
);
"""


def ubigeo6(expresion: str) -> str:
    """Ubigeo como texto de 6 dígitos (con cero a la izquierda) y collation común."""
    return f"RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(20), {expresion}))), 6) COLLATE DATABASE_DEFAULT"


CTE_RURAL = f"""rural AS (
    -- Un registro por distrito, con el ubigeo normalizado igual que en el otro lado del cruce
    SELECT ubigeo6, MAX(Tipo) AS tipo
    FROM (
        SELECT {ubigeo6('Ubigeo')} AS ubigeo6, Tipo COLLATE DATABASE_DEFAULT AS Tipo
        FROM INTCOM.dbo.distritos_rural_alv
        WHERE Ubigeo IS NOT NULL
    ) AS d
    GROUP BY ubigeo6
)"""


SQL_CREDITOS = f"""
WITH {CTE_RURAL},
docs_rurales AS (
    SELECT DISTINCT u.sngc13ndoc AS num_doc
    FROM INTCOM.bt.sngc13 AS u
    INNER JOIN rural AS r ON r.ubigeo6 = {ubigeo6('u.sngc13ugeo')}
    WHERE r.tipo = 'Rural'
),
docs_menores_30 AS (
    -- Misma regla que el original, DATEDIFF(YEAR, nacimiento, cierre) < 30, escrita para usar índices
    SELECT DISTINCT f.PFNDOC AS num_doc
    FROM INTCOM.bt.fsd002 AS f
    WHERE f.pffnac >= DATEFROMPARTS(YEAR(@fecha) - 29, 1, 1)
),
clientes AS (
    SELECT
        c.Cta_Cliente,
        MAX(CASE WHEN c.Genero_Persona = 'F' THEN 1 ELSE 0 END) AS mujer,
        MAX(CASE WHEN dr.num_doc IS NULL THEN 0 ELSE 1 END)     AS rural,
        MAX(CASE WHEN dm.num_doc IS NULL THEN 0 ELSE 1 END)     AS menor_30
    FROM INTCOM.dbo.ccd AS c
    -- COLLATE solo del lado de ccd: el lado buscado conserva su índice
    LEFT JOIN docs_rurales AS dr    ON dr.num_doc = c.Num_Doc COLLATE Modern_Spanish_CI_AS
    LEFT JOIN docs_menores_30 AS dm ON dm.num_doc = c.Num_Doc COLLATE Modern_Spanish_CI_AS
    WHERE c.Fecha_Cierre = @fecha
      AND c.Cta_Cliente IS NOT NULL
    GROUP BY c.Cta_Cliente
),
totales AS (
    SELECT COUNT(*) AS total, SUM(mujer) AS mujeres, SUM(rural) AS rurales, SUM(menor_30) AS menores_30
    FROM clientes
    HAVING COUNT(*) > 0
)
SELECT @fecha AS FECHA, v.INDICADOR, v.CATEGORIA, v.CLIENTES
FROM totales
CROSS APPLY (VALUES
    ('TOTAL',     'TOTAL', total),
    ('GENERO',    'F',     mujeres),
    ('RURALIDAD', 'Rural', rurales),
    ('EDAD',      '< 30',  menores_30)
) AS v (INDICADOR, CATEGORIA, CLIENTES);
"""


SQL_NUEVOS = """
WITH clientes AS (
    SELECT
        HCTACLI,
        MAX(CASE WHEN HINDBANC = '1' THEN 1 ELSE 0 END)    AS bancarizado,
        MAX(CASE WHEN HINDBANCEXC = '1' THEN 1 ELSE 0 END) AS exclusivo
    FROM csd.dbo.Clientes_DS
    WHERE HFECPRO = @fecha
      AND HCTACLI IS NOT NULL
    GROUP BY HCTACLI
),
totales AS (
    SELECT COUNT(*) AS nuevos, SUM(bancarizado) AS bancarizados, SUM(exclusivo) AS exclusivos
    FROM clientes
    HAVING COUNT(*) > 0
)
SELECT @fecha AS FECHA, v.INDICADOR, v.CATEGORIA, v.CLIENTES
FROM totales
CROSS APPLY (VALUES
    ('TOTAL',         'NUEVOS',       nuevos),
    ('BANCARIZACION', 'BANCARIZADOS', bancarizados),
    ('BANCARIZACION', 'EXCLUSIVOS',   exclusivos)
) AS v (INDICADOR, CATEGORIA, CLIENTES);
"""


SQL_PASIVOS = f"""
WITH {CTE_RURAL},
clientes AS (
    -- Una fila por cliente. El original agrupaba también por edad y podía contar dos veces al mismo cliente.
    SELECT
        P.BTIPDOC, P.BPAIS, P.BNUMDOC,
        MAX(S3.SGENPER) AS genero,
        MAX(S3.SCODUBI) AS ubigeo,
        MAX(S3.SFECCRE) AS fecha_nac
    FROM DWH.dbo.HCARCAP001 AS H
    INNER JOIN DWH.dbo.BREGPER001 AS P ON P.BIDPER = H.BIDCLI
    LEFT JOIN DWH.dbo.SCARCAP001 AS S1 ON S1.SIDS001 = H.SIDS001
    LEFT JOIN DWH.dbo.SCARCAP003 AS S3 ON S3.SIDS003 = H.SIDS003
    WHERE H.HFECPRO = @fecha
    GROUP BY P.BTIPDOC, P.BPAIS, P.BNUMDOC
    -- Equivale a NOT (todas INACTIVAS AND saldo <= PEN 1.00), sin tablas temporales
    HAVING MAX(CASE WHEN S1.SDESEST <> 'INACTIVAS' THEN 1 ELSE 0 END) = 1
        OR SUM(H.HSDOMN) > 1.0
),
atributos AS (
    SELECT
        ISNULL(CONVERT(VARCHAR(20), c.genero) COLLATE DATABASE_DEFAULT, 'SIN DATO') AS genero,
        ISNULL(r.tipo, 'SIN DATO') AS ruralidad,
        -- Regla original de Pasivos: edad exacta, 30 años cuenta como MENOR 30, sin fecha cuenta como MAYOR 30
        CASE WHEN e.edad <= 30 THEN 'MENOR 30' ELSE 'MAYOR 30' END AS rango_edad
    FROM clientes AS c
    CROSS APPLY (
        SELECT DATEDIFF(YEAR, c.fecha_nac, @fecha)
             - CASE WHEN DATEADD(YEAR, DATEDIFF(YEAR, c.fecha_nac, @fecha), c.fecha_nac) > @fecha
                    THEN 1 ELSE 0 END AS edad
    ) AS e
    LEFT JOIN rural AS r ON r.ubigeo6 = {ubigeo6('c.ubigeo')}
)
SELECT
    @fecha AS FECHA,
    CASE WHEN GROUPING(genero) = 0 THEN 'GENERO'
         WHEN GROUPING(ruralidad) = 0 THEN 'RURALIDAD'
         WHEN GROUPING(rango_edad) = 0 THEN 'EDAD'
         ELSE 'TOTAL' END AS INDICADOR,
    CASE WHEN GROUPING(genero) = 0 THEN genero
         WHEN GROUPING(ruralidad) = 0 THEN ruralidad
         WHEN GROUPING(rango_edad) = 0 THEN rango_edad
         ELSE 'TOTAL' END AS CATEGORIA,
    COUNT(*) AS CLIENTES
FROM atributos
GROUP BY GROUPING SETS ((), (genero), (ruralidad), (rango_edad))  -- los 4 indicadores en una sola pasada
HAVING COUNT(*) > 0;
"""


SQL_SEGUROS = f"""
WITH {CTE_RURAL},
clientes AS (
    -- El filtro de estado ahora aplica a todos los indicadores, no solo al total
    SELECT DISTINCT tipo_doc, num_doc
    FROM INTCOM.dbo.CCS_FUND_F
    WHERE fecha_reporte = @fecha
      AND DESC_ESTADO IN ('ACTIVO', 'VIGENTE')
      AND num_doc IS NOT NULL
)
SELECT @fecha AS FECHA, 'TOTAL' AS INDICADOR, 'TOTAL' AS CATEGORIA, COUNT(DISTINCT num_doc) AS CLIENTES
FROM clientes
HAVING COUNT(*) > 0

UNION ALL

SELECT @fecha, 'GENERO', g.genero, COUNT(*)
FROM (
    SELECT DISTINCT c.tipo_doc, c.num_doc, f.pfcant COLLATE DATABASE_DEFAULT AS genero
    FROM clientes AS c
    INNER JOIN INTCOM.bt.fsd002 AS f ON f.PFNDOC = c.num_doc
    WHERE f.pfcant IN ('M', 'F')
) AS g
GROUP BY g.genero

UNION ALL

SELECT @fecha, 'RURALIDAD', x.tipo, COUNT(*)
FROM (
    SELECT DISTINCT c.tipo_doc, c.num_doc, r.tipo
    FROM clientes AS c
    INNER JOIN INTCOM.bt.sngc13 AS u ON u.sngc13ndoc = c.num_doc
    INNER JOIN rural AS r ON r.ubigeo6 = {ubigeo6('u.sngc13ugeo')}
    WHERE r.tipo IN ('Rural', 'Urbano')
) AS x
GROUP BY x.tipo

UNION ALL

SELECT @fecha, 'EDAD', e.rango_edad, COUNT(*)
FROM (
    -- Regla original de Seguros: DATEDIFF(YEAR), solo edades > 0
    SELECT DISTINCT c.tipo_doc, c.num_doc,
        CASE WHEN DATEDIFF(YEAR, f.pffnac, @fecha) < 30 THEN '< 30' ELSE '>=30' END AS rango_edad
    FROM clientes AS c
    INNER JOIN INTCOM.bt.fsd002 AS f ON f.PFNDOC = c.num_doc
    WHERE DATEDIFF(YEAR, f.pffnac, @fecha) > 0
) AS e
GROUP BY e.rango_edad;
"""


# =============================================================================
# Reportes y planificación
# =============================================================================
@dataclass(frozen=True)
class Reporte:
    nombre: str
    servidor: dict
    tabla: str
    columna_fecha: str
    cuerpo_sql: str
    desfase_meses: int = 0  # Meses antes de --mes

    @property
    def sql(self) -> str:
        return declarar_fecha(self.tabla, self.columna_fecha) + self.cuerpo_sql

    @property
    def sql_ultima_fecha(self) -> str:
        return f"SELECT MAX({self.columna_fecha}) AS ULTIMA FROM {self.tabla}"


REPORTES: dict[str, Reporte] = {
    r.nombre: r
    for r in (
        Reporte("creditos", SERVIDOR_INTCOM, "INTCOM.dbo.ccd", "Fecha_Cierre", SQL_CREDITOS, 0),
        Reporte("nuevos", SERVIDOR_213, "csd.dbo.Clientes_DS", "HFECPRO", SQL_NUEVOS, 1),
        Reporte("pasivos", SERVIDOR_INTCOM, "DWH.dbo.HCARCAP001", "HFECPRO", SQL_PASIVOS, 0),
        Reporte("seguros", SERVIDOR_INTCOM, "INTCOM.dbo.CCS_FUND_F", "fecha_reporte", SQL_SEGUROS, 1),
    )
}


@dataclass(frozen=True)
class Tarea:
    reporte: Reporte
    periodo: str  # ACTUAL | ANTERIOR
    mes: Mes

    def __str__(self) -> str:
        return f"{self.reporte.nombre} {self.periodo.lower()} ({self.mes})"


def planificar(mes: Mes, nombres: list[str], desfases: dict[str, int]) -> list[Tarea]:
    tareas = []
    for nombre in nombres:
        reporte = REPORTES[nombre]
        mes_actual = mes.desplazar(-desfases.get(nombre, reporte.desfase_meses))
        tareas += [
            Tarea(reporte, "ACTUAL", mes_actual),
            Tarea(reporte, "ANTERIOR", mes_actual.desplazar(-12)),
        ]
    return tareas


# =============================================================================
# Ejecución
# =============================================================================
def ejecutar_tarea(tarea: Tarea) -> pd.DataFrame:
    reporte = tarea.reporte
    params = {"inicio_mes": tarea.mes.inicio, "inicio_mes_sig": tarea.mes.inicio_siguiente}

    with cronometro(str(tarea)):
        df = leer_sql(reporte.servidor, reporte.sql, params)

    if df.empty:
        ultima = leer_sql(reporte.servidor, reporte.sql_ultima_fecha).iloc[0, 0]
        disponible = pd.Timestamp(ultima).date() if pd.notna(ultima) else "ninguna"
        raise SinDatosError(f"{tarea}: sin datos en {reporte.tabla} (última fecha disponible: {disponible})")

    df = df.rename(columns=str.upper)[COLUMNAS_SQL]
    return df.assign(
        REPORTE=reporte.nombre,
        PERIODO=tarea.periodo,
        MES=str(tarea.mes),
        FECHA=pd.to_datetime(df["FECHA"]).dt.normalize(),
        CLIENTES=pd.to_numeric(df["CLIENTES"]).fillna(0).astype("int64"),
    )[COLUMNAS_DETALLE]


def ejecutar_tareas(tareas: list[Tarea], hilos: int) -> tuple[pd.DataFrame, list[str]]:
    """Corre las consultas en paralelo; una tarea con error no detiene a las demás."""
    resultados, errores = [], []
    with ThreadPoolExecutor(max_workers=max(1, hilos)) as pool:
        futuros = [(tarea, pool.submit(ejecutar_tarea, tarea)) for tarea in tareas]
        for tarea, futuro in futuros:
            try:
                resultados.append(futuro.result())
            except SinDatosError as exc:
                errores.append(str(exc))
            except Exception as exc:  # noqa: BLE001 - se reporta y siguen las demás tareas
                log.debug("Detalle del error en %s", tarea, exc_info=True)
                errores.append(f"{tarea}: {type(exc).__name__}: {exc}")

    detalle = pd.concat(resultados, ignore_index=True) if resultados else pd.DataFrame(columns=COLUMNAS_DETALLE)
    return detalle, errores


def validar(detalle: pd.DataFrame) -> None:
    for (reporte, periodo), grupo in detalle.groupby(["REPORTE", "PERIODO"], sort=False):
        fecha = grupo["FECHA"].iloc[0]
        if fecha != fecha + pd.offsets.MonthEnd(0):
            log.info("%s %s: cierre al %s (no es fin de mes calendario)", reporte, periodo, fecha.date())

        total = grupo.loc[grupo["INDICADOR"] == "TOTAL", "CLIENTES"].sum()
        exceden = grupo[(grupo["INDICADOR"] != "TOTAL") & (grupo["CLIENTES"] > total)]
        for fila in exceden.itertuples():
            log.warning(
                "%s %s: %s/%s (%s) supera al total (%s)",
                reporte, periodo, fila.INDICADOR, fila.CATEGORIA, f"{fila.CLIENTES:,}", f"{total:,}",
            )


def construir_resumen(detalle: pd.DataFrame) -> pd.DataFrame:
    claves = ["REPORTE", "INDICADOR", "CATEGORIA"]
    periodos = ["ANTERIOR", "ACTUAL"]

    clientes = (
        detalle.pivot_table(index=claves, columns="PERIODO", values="CLIENTES", aggfunc="sum", fill_value=0)
        .reindex(columns=periodos)
        .add_prefix("CLIENTES_")
        .reset_index()
    )
    por_reporte = detalle.groupby(["REPORTE", "PERIODO"]).agg(FECHA=("FECHA", "first"))
    por_reporte["TOTAL"] = detalle[detalle["INDICADOR"] == "TOTAL"].groupby(["REPORTE", "PERIODO"])["CLIENTES"].sum()
    por_reporte = por_reporte.unstack("PERIODO").reindex(columns=periodos, level=1)
    por_reporte.columns = [f"{campo}_{periodo}" for campo, periodo in por_reporte.columns]

    resumen = clientes.merge(por_reporte.reset_index(), on="REPORTE", how="left")
    for periodo in periodos:
        resumen[f"PART_{periodo}"] = resumen[f"CLIENTES_{periodo}"] / resumen[f"TOTAL_{periodo}"]
    resumen["VAR_ABS"] = resumen["CLIENTES_ACTUAL"] - resumen["CLIENTES_ANTERIOR"]
    resumen["VAR_PCT"] = resumen["VAR_ABS"] / resumen["CLIENTES_ANTERIOR"].where(resumen["CLIENTES_ANTERIOR"] > 0)

    orden_reporte = {nombre: i for i, nombre in enumerate(REPORTES)}
    orden_indicador = {nombre: i for i, nombre in enumerate(ORDEN_INDICADORES)}
    return (
        resumen.assign(
            _r=resumen["REPORTE"].map(orden_reporte),
            _i=resumen["INDICADOR"].map(orden_indicador).fillna(len(orden_indicador)),
        )
        .sort_values(["_r", "_i", "CATEGORIA"], kind="stable")
        .reset_index(drop=True)[
            [
                *claves,
                "FECHA_ANTERIOR", "CLIENTES_ANTERIOR", "PART_ANTERIOR",
                "FECHA_ACTUAL", "CLIENTES_ACTUAL", "PART_ACTUAL",
                "VAR_ABS", "VAR_PCT",
            ]
        ]
    )


def exportar_excel(hojas: dict[str, pd.DataFrame], ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(ruta, engine="openpyxl", datetime_format="yyyy-mm-dd", date_format="yyyy-mm-dd") as writer:
        for nombre, df in hojas.items():
            df.to_excel(writer, sheet_name=nombre, index=False)
            hoja = writer.sheets[nombre]
            hoja.freeze_panes = "A2"
            for i, columna in enumerate(df.columns, start=1):
                letra = get_column_letter(i)
                hoja.column_dimensions[letra].width = max(12, len(columna) + 2)
                if columna.startswith(("PART_", "VAR_PCT")):
                    formato = "0.0%"
                elif columna.startswith(("CLIENTES", "VAR_ABS")):
                    formato = "#,##0"
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


def tipo_desfase(valor: str) -> tuple[str, int]:
    nombre, _, meses = valor.partition("=")
    if nombre not in REPORTES or not meses.lstrip("-").isdigit():
        raise argparse.ArgumentTypeError(f"Usa REPORTE=MESES con REPORTE en {', '.join(REPORTES)}; recibido '{valor}'")
    return nombre, int(meses)


def parsear_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Indicadores de clientes para el Directorio.")
    parser.add_argument("--mes", type=tipo_mes, required=True, help="Mes de Créditos y Pasivos, AAAA-MM")
    parser.add_argument("--reportes", nargs="+", choices=list(REPORTES), default=list(REPORTES),
                        help="Reportes a ejecutar (defecto: todos)")
    parser.add_argument("--desfase", type=tipo_desfase, action="append", default=[], metavar="REPORTE=MESES",
                        help="Cambia el desfase de un reporte (defecto: nuevos=1, seguros=1)")
    parser.add_argument("--hilos", type=int, default=HILOS_DEFECTO,
                        help=f"Consultas simultáneas (defecto: {HILOS_DEFECTO})")
    parser.add_argument("--salida", type=Path, default=DIR_SALIDA_DEFECTO, help="Carpeta de salida (defecto: salidas)")
    parser.add_argument("--copiar", choices=["resumen", "detalle"],
                        help="Copia una hoja al portapapeles (sin encabezados)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Log detallado")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parsear_argumentos(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    tareas = planificar(args.mes, args.reportes, dict(args.desfase))
    log.info("Plan: %s", " · ".join(str(t) for t in tareas))

    detalle, errores = ejecutar_tareas(tareas, args.hilos)
    for mensaje in errores:
        log.error("%s", mensaje)
    if detalle.empty:
        return 1

    validar(detalle)
    resumen = construir_resumen(detalle)
    with pd.option_context("display.width", 200, "display.max_columns", None, "display.float_format", "{:.3f}".format):
        log.info("Resumen:\n%s", resumen.to_string(index=False))

    try:
        ruta = exportar_excel(
            {"resumen": resumen, "detalle": detalle},
            args.salida / f"IndicadoresClientes_{args.mes.anio:04d}{args.mes.mes:02d}.xlsx",
        )
        log.info("Excel guardado en: %s", ruta.resolve())
        if args.copiar:
            {"resumen": resumen, "detalle": detalle}[args.copiar].to_clipboard(index=False, header=False)
            log.info("'%s' copiado al portapapeles", args.copiar)
    except OSError as exc:  # p. ej. el Excel está abierto
        log.error("%s", exc)
        return 1

    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
