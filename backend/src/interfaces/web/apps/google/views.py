"""MCP de Google Workspace: cliente OAuth, autorización, servidores MCP oficiales, envío directo y firma de Gmail."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from aplicacion import dto as e
from aplicacion.casos_uso import correo_reporte, google
from interfaces.web import http as h


class Firma(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(correo_reporte.firma())


class Mcp(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.leer())

    def put(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.guardar(h.cuerpo(request, e.PedidoGoogleMcp)))


class Autorizar(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.autorizar(h.cuerpo(request, e.PedidoAutorizacion)))


class Codigo(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.canjear(h.cuerpo(request, e.PedidoCodigo)))


class Autorizacion(View):
    def delete(self, request: HttpRequest) -> HttpResponse:
        return h.json(google.desconectar())


class Herramientas(View):
    def post(self, request: HttpRequest, servicio: str) -> HttpResponse:
        return h.json(google.herramientas(servicio))


class Ejecutar(View):
    def post(self, request: HttpRequest, servicio: str) -> HttpResponse:
        return h.json(google.ejecutar(servicio, h.cuerpo(request, e.PedidoEjecutarMcp)))


class Enviar(View):
    def post(self, request: HttpRequest, servicio: str) -> HttpResponse:
        return h.json(google.enviar(servicio, h.cuerpo(request, e.PedidoPruebaGoogle)))
