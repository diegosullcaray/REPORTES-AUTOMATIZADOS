"""Middleware de la API: sesión obligatoria y traducción de errores de los casos de uso a códigos HTTP."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from aplicacion.casos_uso import sesion
from aplicacion.errores import NoEncontrado, PeticionInvalida

from .http import ErrorHttp, error


def sesion_obligatoria(get_response):
    """Todo /api exige cookie de sesión válida salvo iniciar sesión y consultar si la hay (/api/sesion)."""

    def middleware(request: HttpRequest) -> HttpResponse:
        if request.path.startswith("/api") and request.path != "/api/sesion" and not sesion.leer(request.COOKIES.get(sesion.COOKIE)):
            return error(401, "Inicia sesión para continuar")
        return get_response(request)

    return middleware


class TraducirErrores:
    """PeticionInvalida → 422, NoEncontrado → 404 y ErrorHttp → su código; cualquier otra excepción sigue como error 500."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exc: Exception) -> HttpResponse | None:
        if isinstance(exc, PeticionInvalida):
            return error(422, str(exc))
        if isinstance(exc, NoEncontrado):
            return error(404, str(exc))
        if isinstance(exc, ErrorHttp):
            return error(exc.status, exc.detalle)
        return None
