"""Secciones de /reportes: carpetas visuales que agrupan tarjetas de reportes existentes (no crean ni cambian reportes)."""

from __future__ import annotations

import uuid

from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion.puertos import puertos
from modulos.reportes.dominio.reportes import REPORTES


def listar() -> list[dto_reportes.Seccion]:
    return puertos().secciones.leer()


def crear(p: dto_reportes.PedidoSeccion) -> dto_reportes.Seccion:
    nombre = p.nombre.strip()
    if not nombre:
        raise PeticionInvalida("Ponle un nombre a la sección.")
    desconocidos = [r for r in p.reportes if r not in REPORTES]
    if desconocidos:
        raise PeticionInvalida(f"Reportes desconocidos: {', '.join(desconocidos)}")
    existentes = listar()
    if any(s.nombre.casefold() == nombre.casefold() for s in existentes):
        raise PeticionInvalida(f"Ya existe una sección «{nombre}».")
    nueva = dto_reportes.Seccion(id=uuid.uuid4().hex[:8], nombre=nombre, descripcion=p.descripcion.strip(), reportes=list(dict.fromkeys(p.reportes)))
    puertos().secciones.escribir([*existentes, nueva])
    return nueva


def eliminar(id_: str) -> None:
    existentes = listar()
    if not any(s.id == id_ for s in existentes):
        raise NoEncontrado(f"No existe la sección {id_}.")
    puertos().secciones.escribir([s for s in existentes if s.id != id_])
