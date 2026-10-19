"""Procesos del repo DICCIONARIO que se lanzan desde la web (regenerar, verificar, probar): lista cerrada, uno a la vez, con su historial y log."""

from __future__ import annotations

from core.excepciones import NoEncontrado
from modulos.diccionario.aplicacion import dto
from modulos.diccionario.aplicacion.puertos import puertos
from modulos.diccionario.dominio.columnas import PROCESOS


def catalogo() -> list[dto.ProcesoDef]:
    return [dto.ProcesoDef(id=p.id, nombre=p.nombre, descripcion=p.descripcion, comando=" ".join(p.comando), escribe=p.escribe) for p in PROCESOS.values()]


def ejecutar(id_: str) -> dto.Ejecucion:
    if id_ not in PROCESOS:  # el comando sale solo de PROCESOS, nunca de la petición
        raise NoEncontrado(f"No existe el proceso «{id_}».")
    # «uno a la vez» lo garantiza el lanzador (comprueba y anota bajo un mismo candado)
    return puertos().lanzador.ejecutar(id_, PROCESOS[id_].comando, puertos().lector.carpeta())


def historial() -> list[dto.Ejecucion]:
    return puertos().lanzador.historial()


def obtener(id_: str) -> dto.EjecucionDetalle:
    try:
        return puertos().lanzador.obtener(id_)
    except KeyError:
        raise NoEncontrado("No existe esa ejecución.") from None
