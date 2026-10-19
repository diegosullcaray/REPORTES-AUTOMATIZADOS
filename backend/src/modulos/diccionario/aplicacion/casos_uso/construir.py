"""Genera el diccionario desde la base: el catálogo de reportes (mod_rep.rep.RREGREP01) y lo que SQL Server sabe de cada procedimiento. Sin el repo DICCIONARIO."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from core.excepciones import ConfiguracionError
from core.servidores import servidor_de_base
from modulos.diccionario.aplicacion.puertos import puertos
from modulos.diccionario.dominio.armado import armar, tablas_referidas
from modulos.reportes.dominio.verificacion import causa_de


def _causa(exc: Exception, base: str) -> str:
    try:
        return causa_de(exc, servidor_de_base(base))[0]
    except ConfiguracionError:
        return str(exc)[:160]


def construir(emitir: Callable[[str], None]) -> int:
    """Lee el catálogo, pide a cada base las dependencias de sus procedimientos y la estructura de las tablas que usan, y guarda el diccionario.

    Va escribiendo su avance. Código 0 si se guardó; 1 si no se pudo leer el catálogo o ninguna base contestó (entonces no se toca el diccionario anterior).
    """
    g = puertos().generador
    emitir("▶ Leyendo el catálogo de reportes (mod_rep.rep.RREGREP01)…\n")
    try:
        reportes = puertos().catalogo.leer()
    except Exception as exc:  # noqa: BLE001 - sin VPN o sin permiso: se dice por qué y no se toca nada
        emitir(f"✗ No pude leer el catálogo: {_causa(exc, 'mod_rep')}\n")
        return 1
    sps: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for r in reportes:
        partes = r["procedimiento"].split(".")
        if len(partes) == 3 and all(partes):
            sps[partes[0]].add((partes[1], partes[2]))
    emitir(f"✓ {len(reportes)} reportes · {sum(len(v) for v in sps.values())} procedimientos en {len(sps)} bases\n")

    dependencias: list[dict] = []
    parametros: list[dict] = []
    con_sp: set[str] = set()
    for base, lista in sorted(sps.items()):
        emitir(f"▶ {base}: dependencias y parámetros de {len(lista)} procedimientos…\n")
        try:
            filas, pars = g.dependencias(base, sorted(lista)), g.parametros(base)
        except Exception as exc:  # noqa: BLE001 - una base caída no impide generar las demás
            emitir(f"✗ {base}: {_causa(exc, base)}\n")
            continue
        dependencias += filas
        parametros += pars
        con_sp.add(base.lower())
        emitir(f"✓ {base}: {len(filas)} dependencias\n")
    if not con_sp:
        emitir("✗ Ninguna base contestó: no se guardó nada (queda el diccionario anterior, si había).\n")
        return 1

    estructura: list[dict] = []
    con_estructura: set[str] = set()
    for base, tablas in sorted(tablas_referidas(dependencias).items()):
        try:
            servidor_de_base(base)
        except ConfiguracionError:
            emitir(f"AVISO {base}: no sé en qué servidor vive; sus {len(tablas)} tablas quedan sin estructura\n")
            continue
        emitir(f"▶ {base}: estructura de {len(tablas)} tablas…\n")
        try:
            estructura += g.estructura(base, sorted(tablas))
        except Exception as exc:  # noqa: BLE001
            emitir(f"AVISO {base}: {_causa(exc, base)}; sus tablas quedan sin estructura\n")
            continue
        con_estructura.add(base.lower())

    datos = armar(reportes, dependencias, parametros, estructura, con_sp, con_estructura)
    puertos().lector.guardar(datos)
    r = datos["resumen"]
    emitir(f"✓ Diccionario guardado: {r['reportes']} reportes · {r['procedimientos']} procedimientos ({r['validados']} validados por el motor) · {r['tablas']} tablas · "
           f"{len(datos['hallazgos'])} hallazgos\n")
    return 0
