"""¿Están las tablas de un reporte al día para el corte? Estados, causas legibles y mensaje para pedir la actualización a Producción.

Reglas puras: la consulta a la base de datos es un caso de uso (`aplicacion/verificacion.py`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from core.excepciones import ConfiguracionError
from modulos.reportes.dominio.reglas_fecha import regla_de
from modulos.reportes.dominio.tablas import Tabla, tablas_de


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
    sin_conexion: bool = False   # el servidor no respondió o faltan sus credenciales/driver: sus demás tablas fallarían igual


def nombre_resuelto(tabla: Tabla, fecha: date) -> str:
    return tabla.nombre.replace("{yyyymmdd}", f"{fecha:%Y%m%d}").replace("{yyyymm}", f"{fecha:%Y%m}")


def causa_de(exc: Exception, servidor: str) -> tuple[str, bool]:
    """Mensaje corto y accionable + si el fallo es de conexión (no de la tabla)."""
    texto = str(exc)
    if isinstance(exc, ConfiguracionError):
        return texto[:220], True
    if any(c in texto for c in ("08001", "08S01", "HYT00", "DBNETLIB", "10060", "10061")):
        return f"No se pudo conectar al servidor «{servidor}»: sin red o VPN, nombre inexistente o tiempo agotado", True
    if "28000" in texto or "Login failed" in texto:
        return f"El servidor «{servidor}» rechazó el inicio de sesión (usuario o contraseña)", True
    if "IM002" in texto:
        return "No hay un driver ODBC de SQL Server instalado (o DB_ODBC_DRIVER apunta a uno que no existe)", True
    return texto[:160], False


def mensaje_solicitud_grupo(titulo: str, fecha: date, pendientes: list[tuple[Tabla, Resultado, list[str]]]) -> str:
    """Un solo pedido a Producción para varios reportes: cada tabla pendiente una vez, con los reportes que la usan."""
    if not pendientes:
        return f"Todas las tablas de «{titulo}» están al día al {fecha:%d/%m/%Y}; no hace falta pedir actualización."
    L = [f"Hola, para generar los reportes mensuales de «{titulo}» con corte al {fecha:%d/%m/%Y} necesito que, por favor, "
         "actualices (o confirmes que ya cargó el cierre en) las siguientes tablas de producción:", ""]
    for t, r, reportes in pendientes:
        extra = f" — última fecha cargada: {r.ultima_fecha:%d/%m/%Y}" if r.ultima_fecha else f" — {r.estado.value.lower()}"
        col = f" (columna de fecha: {t.col_fecha})" if t.col_fecha else ""
        L.append(f"  • {nombre_resuelto(t, fecha)}  [conexión {t.servidor}]{col}{extra}")
        L.append(f"      la usan: {', '.join(reportes)}")
    L += ["", f"Necesito que lleguen hasta el {fecha:%d/%m/%Y}. Cuando estén listas me avisas y ejecuto los reportes. ¡Gracias!"]
    return "\n".join(L)


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
        regla = regla_de(reporte, t.nombre)
        if regla:
            L.append(f"      el reporte filtra: {regla}")
    otras = [nombre_resuelto(t, fecha) for t in tablas_de(reporte) if not t.verificable and t.tipo in {"otro", "referencia"}]
    if otras:
        L += ["", "Si alguna de estas vistas/catálogos que también usa el reporte depende de esas cargas, valida que se refresque: "
              + ", ".join(otras[:8]) + ("…" if len(otras) > 8 else "")]
    L += ["", f"Necesito que lleguen hasta el {fecha:%d/%m/%Y}. Cuando estén listas me avisas y ejecuto el reporte. ¡Gracias!"]
    return "\n".join(L)
