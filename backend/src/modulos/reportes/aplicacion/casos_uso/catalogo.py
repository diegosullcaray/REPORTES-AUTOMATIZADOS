"""Catálogo de reportes: qué hay, cómo se describe cada uno, su fecha de corte y a quién se le entrega su archivo.

Las validaciones lanzan `PeticionInvalida` (422) o `NoEncontrado` (404); la capa HTTP solo las traduce.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from functools import lru_cache
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path

from modulos.notificaciones.aplicacion import destinatarios
from modulos.reportes.aplicacion.cortes import resolver_corte
from modulos.reportes.aplicacion.ejecucion import ReporteLote
from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.notificaciones.dominio import entregas
from core.excepciones import ConfiguracionError
from modulos.reportes.dominio.fechas import Cortes
from modulos.reportes.dominio.reglas_fecha import regla_de
from modulos.reportes.dominio.reportes import DIA_ANTERIOR_SIMPLE, REPORTES, Reporte, ordenados
from modulos.reportes.dominio.tablas import tablas_de
from modulos.reportes.dominio.verificacion import nombre_resuelto
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion import nuevo_reporte as nr


def reporte(nombre: str) -> Reporte:
    if nombre not in REPORTES:
        raise NoEncontrado(f"Reporte desconocido: {nombre}")
    return REPORTES[nombre]


@lru_cache
def lote(nombre: str) -> ReporteLote | None:
    """El `ReporteLote` del módulo, o None si el reporte tiene lógica propia (cmg-mora, bancarizados…)."""
    valor = getattr(import_module(reporte(nombre).modulo), "REPORTE", None)
    return valor if isinstance(valor, ReporteLote) else None


def olvidar(nombre: str) -> None:
    """El código del módulo cambió o se borró: la próxima consulta lo vuelve a importar en vez de usar la copia en memoria."""
    lote.cache_clear()
    sys.modules.pop(reporte(nombre).modulo, None)


# Reportes con lógica propia (sin ReporteLote): lo que la pantalla debe advertir antes de ejecutar.
AVISOS_PROPIOS = {
    "cmg-mora": [
        "Trunca y recarga DW_Raw_v2.CMGMora_Recaudo (rcc) y genera los INSERT de SBTVRIE001. Termina en error si no hay recaudo del día, "
        "falta la tabla PROV_PROY del día o las provisiones están en 0. No lo ejecutes a la vez desde la consola.",
    ],
}


# Reportes que envían su archivo por Google Chat (opción --chat).
ENVIAN_CHAT = {"cmg-mora"}


def _resumen(r: Reporte) -> dict:
    lt = lote(r.nombre)
    return dict(
        nombre=r.nombre, grupo=r.grupo, orden=r.orden, frecuencia=r.frecuencia, servidores=list(r.servidores),
        descripcion=r.descripcion, carpeta=r.carpeta, es_lote=lt is not None,
        escribe_en_bd=bool(lt and lt.escribe_en_bd), vacio_valido=bool(lt and lt.vacio_valido),
        envia_correo=bool(lt and lt.entrega is not None), envia_chat=r.nombre in ENVIAN_CHAT, avisos=list(lt.avisos) if lt else AVISOS_PROPIOS.get(r.nombre, []),
    )


def catalogo() -> list[dto_reportes.ReporteResumen]:
    return [dto_reportes.ReporteResumen(**_resumen(r)) for r in ordenados()]


def corte_por_defecto(nombre: str) -> dto_reportes.Corte:
    r = reporte(nombre)
    try:
        fecha, origen = resolver_corte(r.frecuencia, None, lunes_sabado=nombre not in DIA_ANTERIOR_SIMPLE)
        return dto_reportes.Corte(fecha=fecha, origen=origen)
    except ConfiguracionError as exc:
        return dto_reportes.Corte(fecha=None, origen=str(exc))


def detalle(nombre: str) -> dto_reportes.ReporteDetalle:
    r = reporte(nombre)
    corte = corte_por_defecto(nombre)
    ref = corte.fecha or date.today()
    tablas = [
        dto_reportes.TablaReporte(nombre=nombre_resuelto(t, ref), servidor=t.servidor, tipo=t.tipo, columna_fecha=t.col_fecha,
                       confianza=t.confianza, verificable=t.verificable, condicion=regla_de(nombre, t.nombre))
        for t in tablas_de(nombre)
    ]
    destinos = destinatarios.leer(entregas.variable_chat(nombre)) if nombre in ENVIAN_CHAT else []
    return dto_reportes.ReporteDetalle(**_resumen(r), corte=corte, tablas=tablas, chat_destinatarios=destinos,
                            correo_para=destinatarios.leer(entregas.variable_correo_para(nombre)),
                            correo_cc=destinatarios.leer(entregas.variable_correo_cc(nombre)))


def _archivo_script(nombre: str) -> Path:
    return Path(find_spec(reporte(nombre).modulo).origin)  # solo sale del registro REPORTES, nunca de la petición


def script(nombre: str) -> dto_reportes.Script:
    """Código fuente del módulo del reporte: el T-SQL y la lógica que ejecuta."""
    ruta = f"backend/src/{reporte(nombre).modulo.replace('.', '/')}.py"
    return dto_reportes.Script(ruta=ruta, codigo=_archivo_script(nombre).read_text(encoding="utf-8"))


def guardar_script(nombre: str, p: dto_reportes.PedidoScript) -> dto_reportes.Script:
    """Sobrescribe el módulo del reporte si compila. Rige desde la siguiente ejecución (git guarda la versión anterior)."""
    try:
        compile(p.codigo, nombre, "exec")
    except SyntaxError as exc:
        raise PeticionInvalida(f"Error de sintaxis en la línea {exc.lineno}: {exc.msg}") from exc
    archivo = _archivo_script(nombre)
    if nr.MARCA_WEB in p.codigo and nr.MARCA_WEB not in archivo.read_text(encoding="utf-8"):
        raise PeticionInvalida(f"«{nr.MARCA_WEB}» solo la llevan los reportes creados así: no se puede agregar a otro.")
    if nr.MARCA_WEB in p.codigo:  # los creados en la web son de solo lectura también al editar su Script
        for sql in re.findall(r'SQL = r"""(.*?)"""', p.codigo, re.S):
            nr.rechazar_escritura(sql)
    temporal = archivo.with_suffix(".py.tmp")
    temporal.write_text(p.codigo, encoding="utf-8", newline="")
    temporal.replace(archivo)  # atómico: nunca queda un módulo a medio escribir
    olvidar(nombre)
    return script(nombre)


def guardar_chat(nombre: str, p: dto_reportes.PedidoChat) -> dto_reportes.ReporteDetalle:
    """Guarda en el .env a quién se envía el archivo del reporte por Google Chat."""
    reporte(nombre)
    if nombre not in ENVIAN_CHAT:
        raise PeticionInvalida(f"«{nombre}» no envía su archivo por Google Chat.")
    destinatarios.guardar(entregas.variable_chat(nombre), p.destinatarios)
    return detalle(nombre)


# ---------------------------------------------------------------- validación de la fecha de corte

def validar_corte(nombre: str, fecha: date | None) -> date:
    """Misma regla que el ejecutor: --fecha-corte > .env > (diaria) día anterior; mensual = fin de mes."""
    r = reporte(nombre)
    try:
        corte, _ = resolver_corte(r.frecuencia, fecha, lunes_sabado=nombre not in DIA_ANTERIOR_SIMPLE)
        if r.frecuencia == "mensual":
            Cortes.mensual(corte)
    except ConfiguracionError as exc:
        raise PeticionInvalida(str(exc)) from exc
    if corte > date.today():
        raise PeticionInvalida(f"La fecha de corte {corte:%Y-%m-%d} está en el futuro.")
    return corte
