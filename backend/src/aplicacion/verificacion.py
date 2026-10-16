"""¿Están las tablas de un reporte al día para el corte? Solo hace SELECT MAX(<col_fecha>) / comprueba existencia; no modifica nada."""

from __future__ import annotations

import re
from datetime import date, datetime

from dominio.tablas import Tabla, tablas_de
from dominio.verificacion import Estado, Resultado, causa_de, nombre_resuelto

from .cortes import resolver_corte
from .puertos import puertos

TIMEOUT_CONEXION = 10  # segundos; un servidor inalcanzable no debe retener la verificación
_SEGURO = re.compile(r"^[\w.${}]+$")


def fecha_esperada(frecuencia: str, hoy: date | None = None, fecha_corte: date | None = None, lunes_sabado: bool = True) -> date:
    """Corte a validar. Prioridad: argumento > .env (FECHA_CORTE_DIARIA/MENSUAL) > diaria: día anterior (lunes -> sábado)."""
    return resolver_corte(frecuencia, fecha_corte, hoy, lunes_sabado)[0]


def _a_fecha(valor) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    return valor if isinstance(valor, date) else None


def verificar_tabla(tabla: Tabla, fecha: date) -> Resultado:
    if not tabla.verificable:
        return Resultado(tabla, Estado.SIN_CONTROL)
    nombre = nombre_resuelto(tabla, fecha)
    if not _SEGURO.match(nombre) or (tabla.col_fecha and not re.match(r"^\w+$", tabla.col_fecha)):
        return Resultado(tabla, Estado.ERROR, detalle="nombre de tabla/columna inválido en el registro")
    bd = puertos().bd
    try:
        if tabla.tipo == "dinamica":
            bd.leer_sql(tabla.servidor, f"SELECT TOP 0 1 AS x FROM {nombre}", timeout=TIMEOUT_CONEXION)
            return Resultado(tabla, Estado.OK, detalle="existe")
        df = bd.leer_sql(tabla.servidor, f"SELECT MAX({tabla.col_fecha}) AS ultima FROM {nombre}", timeout=TIMEOUT_CONEXION)
        ultima = _a_fecha(df.iloc[0, 0])
        if ultima is None:
            return Resultado(tabla, Estado.DESACTUALIZADA, detalle="tabla sin datos")
        return Resultado(tabla, Estado.OK if ultima >= fecha else Estado.DESACTUALIZADA, ultima)
    except Exception as exc:  # incluye ConfiguracionError (p. ej. falta RCC_USER): esa tabla queda en ERROR, las demás se verifican  # noqa: BLE001 - se informa por tabla, no se aborta todo
        texto = str(exc)
        faltante = "Invalid object name" in texto or "no es válido" in texto or "42S02" in texto
        if faltante:
            return Resultado(tabla, Estado.NO_EXISTE, detalle=texto[:100])
        causa, sin_conexion = causa_de(exc, tabla.servidor)
        return Resultado(tabla, Estado.ERROR, detalle=causa, sin_conexion=sin_conexion)


def verificar_reporte(reporte: str, fecha: date) -> list[Resultado]:
    return [verificar_tabla(t, fecha) for t in tablas_de(reporte)]
