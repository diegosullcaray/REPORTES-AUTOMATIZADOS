"""Listas de correos de entrega (Chat, correo, validación): viven en el .env; el valor lo da el puerto de entorno."""

from __future__ import annotations

from dominio.entregas import CORREO, correos_validos

from .errores import PeticionInvalida
from .puertos import puertos


def leer(variable: str) -> list[str]:
    """Los correos válidos guardados en esa variable del .env."""
    return correos_validos(puertos().entorno.leer(variable))


def normalizar(texto: str, maximo: int | None = None) -> list[str]:
    """La lista escrita por la persona, sin repetidos; lanza PeticionInvalida si algún correo no es válido o son demasiados."""
    lista = list(dict.fromkeys(c.strip() for c in texto.split(",") if c.strip()))
    if malos := [c for c in lista if not CORREO.match(c)]:
        raise PeticionInvalida(f"Correo no válido: {', '.join(malos)}")
    if maximo is not None and len(lista) > maximo:
        raise PeticionInvalida(f"Máximo {maximo} correos por campo.")
    return lista


def guardar(variable: str, texto: str, maximo: int | None = None) -> list[str]:
    """Valida y guarda la lista en el .env (vacía = quita la variable)."""
    lista = normalizar(texto, maximo)
    puertos().entorno.guardar({variable: ",".join(lista)})
    return lista
