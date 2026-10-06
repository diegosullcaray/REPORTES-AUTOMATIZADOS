"""
Clientes extranjeros · Créditos, Pasivos y Seguros.

Cuenta clientes persona natural por país y nacionalidad (según tipo de documento)
para un corte mensual y genera un Excel con un consolidado y una hoja por bloque.

Uso:
    python clientes_extranjeros.py --fecha-corte 2026-07-31
    python clientes_extranjeros.py --fecha-corte 2026-07-31 --fecha-seguros 2026-06-30
    python clientes_extranjeros.py --fecha-corte 2026-07-31 --pasivos-directo --copiar consolidado

Conexiones:
    SLC (172.24.2.213): autenticación de Windows. Créditos, Seguros y, por defecto, Pasivos
                        a través del linked server rcc_cd.
    RCC (172.20.0.70):  solo con --pasivos-directo. Credenciales en variables de entorno
                        o archivo .env: RCC_DB_USER, RCC_DB_PASSWORD.
"""

from __future__ import annotations

import argparse
import calendar
import logging
import sys
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from ..comun.fechas import resolver_corte
from ..config import DIR_OUTPUTS, ConfiguracionError
from ..db import leer_sql

# =============================================================================
# Configuración
# =============================================================================
SERVIDOR_SLC = "slc"  # servidor 172.24.2.213 (+ INTCOM, DWH, csd por 3 partes)
SERVIDOR_RCC = "rcc"  # servidor 172.20.0.70
BASE_POR_SERVIDOR = {"slc": "slc", "rcc": "DBRCC"}  # base de datos que abre cada servidor
LINKED_SERVER_RCC = "rcc_cd"

DIR_SALIDA_DEFECTO = DIR_OUTPUTS / "clientes_extranjeros"
COLUMNAS = ["CIERRE", "TIPO", "COD_PAIS", "NACIONALIDAD", "CLIENTES"]
HOJAS = ("consolidado", "creditos", "pasivos", "seguros")

log = logging.getLogger("clientes_extranjeros")


# =============================================================================
# Periodo y conexiones
# =============================================================================
@dataclass(frozen=True)
class Periodo:
    """Deriva fechas y sufijos de tabla a partir de un corte de fin de mes."""

    fecha_corte: date

    def __post_init__(self) -> None:
        ultimo_dia = calendar.monthrange(self.fecha_corte.year, self.fecha_corte.month)[1]
        if self.fecha_corte.day != ultimo_dia:
            raise ValueError(f"La fecha debe ser fin de mes; se recibió {self.fecha_corte}")

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


@contextmanager
def cronometro(etapa: str) -> Iterator[None]:
    inicio = time.perf_counter()
    log.info("▶ %s…", etapa)
    yield
    log.info("✓ %s: %.1f s", etapa, time.perf_counter() - inicio)


# =============================================================================
# Consultas SQL
# =============================================================================
# Todas devuelven ya agregado: CIERRE, TIPO, COD_PAIS, NACIONALIDAD, CLIENTES.
# Un cliente = combinación distinta de (tipo_doc, num_doc) dentro de cada país y nacionalidad,
# con la misma regla de nulos del script original ('-999' / '00000000').
# DISTINCT + COUNT(*) equivale al COUNT(DISTINCT CONCAT_WS(...)) original, sin construir strings.

SQL_CREDITOS = """
WITH llaves AS (
    SELECT DISTINCT
        EOMONTH(fecha_cierre)          AS cierre,
        codigo_pais                    AS cod_pais,
        ISNULL(tipo_doc, '-999')       AS tipo_doc_k,
        ISNULL(num_doc, '00000000')    AS num_doc_k,
        CASE WHEN tipo_doc NOT IN ('21', '9', '15') THEN 'Extranjero' ELSE 'Peru' END AS nacionalidad
    FROM INTCOM.dbo.ccd
    WHERE fecha_cierre = :fecha_cierre
      AND tipo_persona = 'F'
)
SELECT cierre AS CIERRE, 'Creditos' AS TIPO, cod_pais AS COD_PAIS, nacionalidad AS NACIONALIDAD,
       COUNT(*) AS CLIENTES
FROM llaves
GROUP BY cierre, cod_pais, nacionalidad;
"""


def sql_pasivos(p: Periodo, via_linked_server: bool) -> str:
    # Nombre de tabla derivado de una fecha validada: seguro para f-string.
    prefijo = f"{LINKED_SERVER_RCC}." if via_linked_server else ""
    tabla = f"{prefijo}db{p.yyyymm}.dbo.ccp{p.yyyymmdd}"
    return f"""
WITH clientes AS (
    -- Se conserva el cliente si tiene alguna cuenta activa o saldo total > PEN 1.00.
    -- Equivale al filtro original NOT (INACTIVAS AND saldo <= 1.00) sin la tabla #temp001.
    SELECT
        EOMONTH(fecha_cierre) AS cierre,
        tipo_doc,
        numero_doc,
        cod_pais
    FROM {tabla}
    WHERE tipo_persona = 'F'
    GROUP BY EOMONTH(fecha_cierre), tipo_doc, numero_doc, cod_pais
    HAVING MAX(CASE WHEN desc_estado <> 'INACTIVAS' THEN 1 ELSE 0 END) = 1
        OR SUM(saldo_mn) > 1.0
),
llaves AS (
    SELECT DISTINCT
        cierre,
        cod_pais,
        ISNULL(tipo_doc, '-999')       AS tipo_doc_k,
        ISNULL(numero_doc, '00000000') AS num_doc_k,
        CASE WHEN tipo_doc NOT IN ('21', '9', '15') THEN 'Extranjero' ELSE 'Peru' END AS nacionalidad
    FROM clientes
)
SELECT cierre AS CIERRE, 'Pasivos' AS TIPO, cod_pais AS COD_PAIS, nacionalidad AS NACIONALIDAD,
       COUNT(*) AS CLIENTES
FROM llaves
GROUP BY cierre, cod_pais, nacionalidad;
"""


SQL_SEGUROS = """
WITH llaves AS (
    SELECT DISTINCT
        EOMONTH(fecha_reporte)         AS cierre,
        pais                           AS cod_pais,
        ISNULL(tipo_doc, '-999')       AS tipo_doc_k,
        ISNULL(num_doc, '00000000')    AS num_doc_k,
        CASE WHEN tipo_doc IN ('21', '9', '15') THEN 'Peru'
             WHEN tipo_doc = '99' THEN 'Juridico'
             ELSE 'Extranjero' END     AS nacionalidad
    FROM INTCOM.dbo.CCS_FUND_F
    WHERE desc_estado IN ('ACTIVO', 'VIGENTE')
      AND fecha_reporte >= :inicio_mes AND fecha_reporte < :inicio_mes_sig  -- rango: usa índices
)
SELECT cierre AS CIERRE, 'Seguros' AS TIPO, cod_pais AS COD_PAIS, nacionalidad AS NACIONALIDAD,
       COUNT(*) AS CLIENTES
FROM llaves
GROUP BY cierre, cod_pais, nacionalidad;
"""


# =============================================================================
# Bloques
# =============================================================================
@dataclass(frozen=True)
class Bloque:
    nombre: str
    servidor: dict
    consulta: str
    params: dict = field(default_factory=dict)
    sql_ultima_fecha: str | None = None  # Para sugerir un corte disponible si no hay datos


def definir_bloques(corte: Periodo, corte_seguros: Periodo, pasivos_directo: bool) -> list[Bloque]:
    return [
        Bloque(
            nombre="creditos",
            servidor=SERVIDOR_SLC,
            consulta=SQL_CREDITOS,
            params={"fecha_cierre": corte.fecha_corte},
            sql_ultima_fecha="SELECT MAX(fecha_cierre) FROM INTCOM.dbo.ccd",
        ),
        Bloque(
            nombre="pasivos",
            servidor=SERVIDOR_RCC if pasivos_directo else SERVIDOR_SLC,
            consulta=sql_pasivos(corte, via_linked_server=not pasivos_directo),
        ),
        Bloque(
            nombre="seguros",
            servidor=SERVIDOR_SLC,
            consulta=SQL_SEGUROS,
            params={"inicio_mes": corte_seguros.inicio_mes, "inicio_mes_sig": corte_seguros.inicio_mes_siguiente},
            sql_ultima_fecha="SELECT MAX(fecha_reporte) FROM INTCOM.dbo.CCS_FUND_F",
        ),
    ]


def ejecutar_bloque(bloque: Bloque) -> pd.DataFrame:
    with cronometro(f"Consultando {bloque.nombre}"):
        df = leer_sql(bloque.servidor, bloque.consulta, bloque.params, base=BASE_POR_SERVIDOR[bloque.servidor])

    if df.empty:
        mensaje = f"{bloque.nombre}: la consulta no devolvió filas"
        if bloque.sql_ultima_fecha:
            ultima = leer_sql(bloque.servidor, bloque.sql_ultima_fecha, base=BASE_POR_SERVIDOR[bloque.servidor]).iloc[0, 0]
            mensaje += f" (última fecha disponible: {pd.Timestamp(ultima).date()})"
        raise ValueError(mensaje)

    return formatear(df)


def formatear(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.rename(columns=str.upper)[COLUMNAS]
        .assign(
            CIERRE=lambda d: pd.to_datetime(d["CIERRE"]).dt.normalize(),
            CLIENTES=lambda d: d["CLIENTES"].astype("int64"),
        )
        .sort_values(["NACIONALIDAD", "COD_PAIS"], na_position="first", kind="stable")
        .reset_index(drop=True)
    )


def ejecutar(bloques: list[Bloque]) -> tuple[dict[str, pd.DataFrame], list[str]]:
    """Corre los bloques en paralelo; un bloque con error no detiene a los demás."""
    resultados: dict[str, pd.DataFrame] = {}
    errores: list[str] = []

    with ThreadPoolExecutor(max_workers=len(bloques)) as pool:
        futuros = {bloque.nombre: pool.submit(ejecutar_bloque, bloque) for bloque in bloques}
        for nombre, futuro in futuros.items():
            try:
                resultados[nombre] = futuro.result()
            except ValueError as exc:
                errores.append(str(exc))
            except Exception as exc:  # noqa: BLE001 - se reporta y se sigue con los demás bloques
                log.debug("Detalle del error en %s", nombre, exc_info=True)
                errores.append(f"{nombre}: {type(exc).__name__}: {exc}")

    return resultados, errores


def construir_hojas(resultados: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    hojas = {"consolidado": pd.concat(resultados.values(), ignore_index=True)} if resultados else {}
    return hojas | resultados


def exportar_excel(hojas: dict[str, pd.DataFrame], ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(ruta, engine="openpyxl", datetime_format="yyyy-mm-dd") as writer:
        for nombre, df in hojas.items():
            df.to_excel(writer, sheet_name=nombre[:31], index=False)
    return ruta


# =============================================================================
# CLI
# =============================================================================
def fecha_iso(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Fecha inválida '{valor}', usa AAAA-MM-DD") from exc


def parsear_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clientes por nacionalidad: Créditos, Pasivos y Seguros.")
    parser.add_argument("--fecha-corte", type=fecha_iso, help="Fin de mes AAAA-MM-DD (defecto: FECHA_CORTE_MENSUAL del .env)")
    parser.add_argument(
        "--fecha-seguros", type=fecha_iso, help="Corte distinto para Seguros (defecto: el mismo --fecha-corte)"
    )
    parser.add_argument(
        "--pasivos-directo",
        action="store_true",
        help="Consulta Pasivos directo en el servidor RCC en vez de vía linked server",
    )
    parser.add_argument("--salida", type=Path, default=DIR_SALIDA_DEFECTO, help="Carpeta de salida (defecto: data/outputs/<reporte>)")
    parser.add_argument("--copiar", choices=HOJAS, help="Copia una hoja al portapapeles (sin encabezados)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Log detallado")
    args = parser.parse_args(argv)
    try:
        args.fecha_corte, origen = resolver_corte("mensual", args.fecha_corte)
    except ConfiguracionError as exc:
        parser.error(str(exc))
    print(f"Fecha de corte: {args.fecha_corte:%Y-%m-%d} ({origen})")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parsear_argumentos(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        corte = Periodo(args.fecha_corte)
        corte_seguros = Periodo(args.fecha_seguros or args.fecha_corte)
        bloques = definir_bloques(corte, corte_seguros, args.pasivos_directo)
    except (ConfiguracionError, ValueError) as exc:
        log.error("%s", exc)
        return 1

    log.info(
        "Corte %s · Seguros %s · Pasivos %s",
        corte.fecha_corte,
        corte_seguros.fecha_corte,
        "directo RCC" if args.pasivos_directo else f"vía {LINKED_SERVER_RCC}",
    )

    resultados, errores = ejecutar(bloques)
    for mensaje in errores:
        log.error("%s", mensaje)
    if not resultados:
        return 1

    hojas = construir_hojas(resultados)
    for nombre, df in resultados.items():
        log.info("=== %s (%d filas, %s clientes) ===\n%s", nombre, len(df), f"{df['CLIENTES'].sum():,}",
                 df.to_string(index=False))

    try:
        ruta = exportar_excel(hojas, args.salida / f"ClientesExtranjeros_{corte.yyyymmdd}.xlsx")
        log.info("Excel guardado en: %s", ruta.resolve())
        if args.copiar:
            if args.copiar not in hojas:
                raise ValueError(f"No se puede copiar '{args.copiar}': el bloque falló")
            hojas[args.copiar].to_clipboard(index=False, header=False)
            log.info("'%s' copiado al portapapeles", args.copiar)
    except (ValueError, OSError) as exc:  # OSError: p. ej. el Excel está abierto
        log.error("%s", exc)
        return 1

    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
