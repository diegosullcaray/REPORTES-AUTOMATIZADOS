"""Validación masiva de las tablas de los reportes mensuales de un responsable (Piero / Erick): verificar, historial y mensaje por Chat."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion.casos_uso import validacion, verificacion


class Verificar(View):
    def post(self, request: HttpRequest, grupo: str) -> HttpResponse:
        return h.json(validacion.verificar(grupo, h.cuerpo(request, dto_reportes.PedidoCorte).fecha_corte))


class Historial(View):
    def get(self, request: HttpRequest, grupo: str) -> HttpResponse:
        return h.json(validacion.historial(grupo, h.entero(request, "limite", 20, 1, 200)))


class Chat(View):
    def get(self, request: HttpRequest, grupo: str) -> HttpResponse:
        return h.json(validacion.destinos(grupo))

    def put(self, request: HttpRequest, grupo: str) -> HttpResponse:
        return h.json(validacion.guardar_destinos(grupo, h.cuerpo(request, dto_reportes.PedidoChat)))


class ChatEnviar(View):
    def post(self, request: HttpRequest, grupo: str) -> HttpResponse:
        return h.json(validacion.enviar_chat(grupo))


class Solicitud(View):
    def post(self, request: HttpRequest, grupo: str) -> HttpResponse:
        return h.json(verificacion.guardar_solicitud_grupo(grupo, h.cuerpo(request, dto_reportes.PedidoCorte).fecha_corte))
