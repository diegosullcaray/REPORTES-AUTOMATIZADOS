"""¿Están las tablas de un reporte al día para el corte? + mensaje para pedir la actualización a Producción.

Solo hace SELECT MAX(<col_fecha>) / comprueba existencia; no modifica nada.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum

from .config import ConfiguracionError
from .db import leer_sql
from .tablas import Tabla, tablas_de


class Estado(str, Enum):
    OK = "OK"
    DESACTUALIZADA = "DESACTUALIZADA"
    NO_EXISTE = "NO EXISTE"
    ERROR = "ERROR"
    SIN_CONTROL = "SIN CONTROL"  # referencia / vista / destino: no se valida por fecha


@dataclass(frozen=True)
class Resultado:
    tabla: Tabla
    estado: Estado
    ultima_fecha: date | None = None
    detalle: str = ""


def fecha_esperada(frecuencia: str, hoy: date | None = None, fecha_corte: date | None = None) -> date:
    """Mensual: el corte indicado. Diaria: día anterior (lunes -> sábado), igual que CMG Mora."""
    if fecha_corte:
        return fecha_corte
    if frecuencia == "mensual":
        raise ConfiguracionError("Indica --fecha-corte AAAA-MM-DD (fin de mes) para un reporte mensual")
    hoy = hoy or date.today()
    return hoy - timedelta(days=2 if hoy.weekday() == 0 else 1)


def nombre_resuelto(tabla: Tabla, fecha: date) -> str:
    return tabla.nombre.replace("{yyyymmdd}", f"{fecha:%Y%m%d}").replace("{yyyymm}", f"{fecha:%Y%m}")


def _a_fecha(valor) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    return valor if isinstance(valor, date) else None


_SEGURO = re.compile(r"^[\w.${}]+$")


def verificar_tabla(tabla: Tabla, fecha: date) -> Resultado:
    if not tabla.verificable:
        return Resultado(tabla, Estado.SIN_CONTROL)
    nombre = nombre_resuelto(tabla, fecha)
    if not _SEGURO.match(nombre) or (tabla.col_fecha and not re.match(r"^\w+$", tabla.col_fecha)):
        return Resultado(tabla, Estado.ERROR, detalle="nombre de tabla/columna inválido en el registro")
    try:
        if tabla.tipo == "dinamica":
            leer_sql(tabla.servidor, f"SELECT TOP 0 1 AS x FROM {nombre}")
            return Resultado(tabla, Estado.OK, detalle="existe")
        df = leer_sql(tabla.servidor, f"SELECT MAX({tabla.col_fecha}) AS ultima FROM {nombre}")
        ultima = _a_fecha(df.iloc[0, 0])
        if ultima is None:
            return Resultado(tabla, Estado.DESACTUALIZADA, detalle="tabla sin datos")
        return Resultado(tabla, Estado.OK if ultima >= fecha else Estado.DESACTUALIZADA, ultima)
    except ConfiguracionError:
        raise
    except Exception as exc:  # noqa: BLE001 - se informa por tabla, no se aborta todo
        texto = str(exc)
        faltante = "Invalid object name" in texto or "no es válido" in texto or "42S02" in texto
        return Resultado(tabla, Estado.NO_EXISTE if faltante else Estado.ERROR, detalle=texto[:100])


def verificar_reporte(reporte: str, fecha: date) -> list[Resultado]:
    return [verificar_tabla(t, fecha) for t in tablas_de(reporte)]


def mensaje_solicitud(reporte: str, fecha: date, resultados: list[Resultado] | None = None) -> str:
    """Texto listo para enviar a quien actualiza en Producción."""
    if resultados is None:
        pedir = [(t, None) for t in tablas_de(reporte) if t.verificable]
    else:
        pedir = [(r.tabla, r) for r in resultados if r.estado in {Estado.DESACTUALIZADA, Estado.NO_EXISTE}]
    if not pedir:
        return f"Todas las tablas de '{reporte}' están al día al {fecha:%d/%m/%Y}; no hace falta pedir actualización."
    L = [f"Hola, para generar el reporte «{reporte}» con corte al {fecha:%d/%m/%Y} necesito que, por favor, "
         "actualices (o confirmes que ya cargó el cierre en) las siguientes tablas de producción:", ""]
    for t, r in pedir:
        extra = ""
        if r is not None:
            extra = f" — última fecha cargada: {r.ultima_fecha:%d/%m/%Y}" if r.ultima_fecha else f" — {r.estado.value.lower()}"
        col = f" (columna de fecha: {t.col_fecha})" if t.col_fecha else ""
        L.append(f"  • {nombre_resuelto(t, fecha)}  [conexión {t.servidor}]{col}{extra}")
    otras = [nombre_resuelto(t, fecha) for t in tablas_de(reporte) if not t.verificable and t.tipo in {"otro", "referencia"}]
    if otras:
        L += ["", "Si alguna de estas vistas/catálogos que también usa el reporte depende de esas cargas, valida que se refresque: "
              + ", ".join(otras[:8]) + ("…" if len(otras) > 8 else "")]
    L += ["", f"Necesito que lleguen hasta el {fecha:%d/%m/%Y}. Cuando estén listas me avisas y ejecuto el reporte. ¡Gracias!"]
    return "\n".join(L)
