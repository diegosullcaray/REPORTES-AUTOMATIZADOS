"""Ejecuciones: encolar un reporte, ver el historial y eliminar ejecuciones."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from aplicacion import dto as e
from aplicacion.casos_uso import ejecuciones
from interfaces.web import http as h


class Ejecuciones(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(ejecuciones.encolar(h.cuerpo(request, e.PedidoEjecucion)), 202)

    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(ejecuciones.historial(request.GET.get("reporte"), h.entero(request, "limite", 200, 1, 2000)))


class Eliminar(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        pedido = h.cuerpo(request, e.PedidoEliminarEjecuciones)
        return h.json(e.EjecucionesEliminadas(eliminadas=ejecuciones.eliminar(pedido.ids)))


class Detalle(View):
    def get(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(ejecuciones.obtener(id_))
