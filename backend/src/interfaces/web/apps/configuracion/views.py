"""Configuración editable desde la web: perfil, ajustes generales, bases de datos y notificaciones (correo y Google Chat)."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from aplicacion import dto as e
from aplicacion.casos_uso import configuracion, notificaciones
from interfaces.web import http as h


class Perfil(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.perfil())


class Configuracion(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.configuracion())

    def put(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.guardar_configuracion(h.cuerpo(request, e.PedidoConfiguracion)))


class Servidores(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.servidores())


class ServidorPrueba(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(configuracion.probar_servidor(nombre))


class Notificaciones(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(notificaciones.leer())

    def put(self, request: HttpRequest) -> HttpResponse:
        return h.json(notificaciones.guardar(h.cuerpo(request, e.PedidoNotificaciones)))


class NotificacionPrueba(View):
    def post(self, request: HttpRequest, canal: str) -> HttpResponse:
        return h.json(notificaciones.probar(canal))
