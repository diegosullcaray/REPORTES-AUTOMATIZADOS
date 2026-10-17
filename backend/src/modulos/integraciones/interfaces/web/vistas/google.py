"""MCP de Google Workspace: cliente OAuth, autorización, servidores MCP oficiales y envío directo."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.integraciones.aplicacion import dto as dto_integraciones
from modulos.integraciones.aplicacion.casos_uso import google


class Mcp(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.leer())

    def put(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.guardar(h.cuerpo(request, dto_integraciones.PedidoGoogleMcp)))


class Autorizar(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.autorizar(h.cuerpo(request, dto_integraciones.PedidoAutorizacion)))


class Codigo(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.canjear(h.cuerpo(request, dto_integraciones.PedidoCodigo)))


class Autorizacion(View):
    def delete(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.desconectar())


class Herramientas(View):
    def post(self, request: HttpRequest, servicio: str) -> HttpResponse:
        return h.json(google.herramientas(servicio))


class Ejecutar(View):
    def post(self, request: HttpRequest, servicio: str) -> HttpResponse:
        return h.json(google.ejecutar(servicio, h.cuerpo(request, dto_integraciones.PedidoEjecutarMcp)))


class Enviar(View):
    def post(self, request: HttpRequest, servicio: str) -> HttpResponse:
        return h.json(google.enviar(servicio, h.cuerpo(request, dto_integraciones.PedidoPruebaGoogle)))
