"""Etiquetas (como los «tags» de Dokploy): un nombre y un color (#rrggbb) que se pegan a los grupos de reportes para organizarlos.

Las validaciones lanzan `PeticionInvalida` (422) o `NoEncontrado` (404); la capa HTTP solo las traduce.
"""

from __future__ import annotations

import re
import uuid

from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion.puertos import puertos

_COLOR = re.compile(r"#[0-9a-f]{6}")
_NOMBRE = re.compile(r"[\w][\w .-]{0,48}[\w]|[\w]")   # empieza y termina en letra/número/_; admite espacios, puntos y guiones en medio


def _nombre(valor: str) -> str:
    nombre = " ".join(valor.split())
    if not _NOMBRE.fullmatch(nombre):
        raise PeticionInvalida("El nombre de la etiqueta (hasta 50 caracteres) empieza y termina con letra o número; admite espacios, puntos y guiones.")
    return nombre


def _color(valor: str) -> str:
    color = valor.strip().lower()
    if not _COLOR.fullmatch(color):
        raise PeticionInvalida("El color va como #rrggbb (por ejemplo #3b82f6).")
    return color


def listar() -> list[dto_reportes.Etiqueta]:
    return puertos().etiquetas.leer().etiquetas


def _repetida(nombre: str, catalogo: dto_reportes.CatalogoEtiquetas, salvo: str | None = None) -> None:
    if any(e.nombre.casefold() == nombre.casefold() and e.id != salvo for e in catalogo.etiquetas):
        raise PeticionInvalida(f"Ya existe la etiqueta «{nombre}».")


def crear(p: dto_reportes.PedidoEtiqueta) -> dto_reportes.Etiqueta:
    catalogo, nombre, color = puertos().etiquetas.leer(), _nombre(p.nombre), _color(p.color)
    _repetida(nombre, catalogo)
    nueva = dto_reportes.Etiqueta(id=uuid.uuid4().hex[:8], nombre=nombre, color=color)
    catalogo.etiquetas.append(nueva)
    puertos().etiquetas.escribir(catalogo)
    return nueva


def actualizar(id_: str, p: dto_reportes.PedidoEtiqueta) -> dto_reportes.Etiqueta:
    catalogo, nombre, color = puertos().etiquetas.leer(), _nombre(p.nombre), _color(p.color)
    actual = next((e for e in catalogo.etiquetas if e.id == id_), None)
    if actual is None:
        raise NoEncontrado(f"No existe la etiqueta {id_}.")
    _repetida(nombre, catalogo, salvo=id_)
    actual.nombre, actual.color = nombre, color
    puertos().etiquetas.escribir(catalogo)
    return actual


def eliminar(id_: str) -> None:
    """Quita la etiqueta y la desprende de todos los grupos."""
    catalogo = puertos().etiquetas.leer()
    if not any(e.id == id_ for e in catalogo.etiquetas):
        raise NoEncontrado(f"No existe la etiqueta {id_}.")
    catalogo.etiquetas = [e for e in catalogo.etiquetas if e.id != id_]
    catalogo.grupos = {g: [t for t in ids if t != id_] for g, ids in catalogo.grupos.items()}
    puertos().etiquetas.escribir(catalogo)


def de_grupo(grupo: str, catalogo: dto_reportes.CatalogoEtiquetas | None = None) -> list[dto_reportes.Etiqueta]:
    catalogo = catalogo or puertos().etiquetas.leer()
    ids = catalogo.grupos.get(grupo, [])
    return [e for e in catalogo.etiquetas if e.id in ids]


def asignar(grupo: str, ids: list[str]) -> list[dto_reportes.Etiqueta]:
    """Deja en el grupo exactamente estas etiquetas (el grupo ya fue validado por quien llama)."""
    catalogo = puertos().etiquetas.leer()
    desconocidas = [i for i in ids if not any(e.id == i for e in catalogo.etiquetas)]
    if desconocidas:
        raise PeticionInvalida(f"Etiquetas desconocidas: {', '.join(desconocidas)}")
    catalogo.grupos[grupo] = list(dict.fromkeys(ids))
    puertos().etiquetas.escribir(catalogo)
    return de_grupo(grupo, catalogo)


def quitar_grupo(grupo: str) -> None:
    catalogo = puertos().etiquetas.leer()
    if catalogo.grupos.pop(grupo, None) is not None:
        puertos().etiquetas.escribir(catalogo)
