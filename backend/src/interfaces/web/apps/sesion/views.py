"""Inicio y cierre de sesión, y cambio de usuario o contraseña (credenciales en el .env)."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from aplicacion import dto as e
from aplicacion.casos_uso import configuracion, sesion
from interfaces.web import http as h


def _con_cookie(respuesta: HttpResponse, usuario: str) -> HttpResponse:
    respuesta.set_cookie(sesion.COOKIE, sesion.emitir(usuario), max_age=sesion.DURACION, httponly=True, samesite="Strict")
    return respuesta


class Sesion(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        pedido = h.cuerpo(request, e.PedidoSesion)
        try:
            usuario = sesion.iniciar(pedido.usuario, pedido.clave)
        except PermissionError as exc:
            raise h.ErrorHttp(429, str(exc)) from None
        if not usuario:
            raise h.ErrorHttp(401, "Usuario o contraseña incorrectos, o sin permiso para entrar")
        return _con_cookie(h.json(e.Sesion(usuario=usuario)), usuario)

    def get(self, request: HttpRequest) -> HttpResponse:
        usuario = sesion.leer(request.COOKIES.get(sesion.COOKIE))
        if not usuario:
            raise h.ErrorHttp(401, "Sin sesión")
        return h.json(e.Sesion(usuario=usuario))

    def delete(self, request: HttpRequest) -> HttpResponse:
        respuesta = HttpResponse(status=204)
        respuesta.delete_cookie(sesion.COOKIE)
        return respuesta


class Cuenta(View):
    def put(self, request: HttpRequest) -> HttpResponse:
        actual = sesion.leer(request.COOKIES.get(sesion.COOKIE)) or ""
        usuario = configuracion.actualizar_cuenta(actual, h.cuerpo(request, e.PedidoCuenta))
        return _con_cookie(h.json(e.Sesion(usuario=usuario)), usuario)  # el nombre puede haber cambiado
