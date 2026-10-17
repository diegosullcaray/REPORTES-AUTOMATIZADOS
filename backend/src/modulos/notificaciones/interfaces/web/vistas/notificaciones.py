"""Notificaciones: cuenta SMTP del correo y webhook de Google Chat, con su prueba de envío."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.notificaciones.aplicacion import dto as dto_notificaciones
from modulos.notificaciones.aplicacion.casos_uso import notificaciones


class Notificaciones(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(notificaciones.leer())

    def put(self, request: HttpRequest) -> HttpResponse:
        return h.json(notificaciones.guardar(h.cuerpo(request, dto_notificaciones.PedidoNotificaciones)))


class NotificacionPrueba(View):
    def post(self, request: HttpRequest, canal: str) -> HttpResponse:
        return h.json(notificaciones.probar(canal))
