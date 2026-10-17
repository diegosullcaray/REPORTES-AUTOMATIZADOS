"""Ejecuciones: encolar un reporte, ver el historial y eliminar ejecuciones."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion.casos_uso import ejecuciones


class Ejecuciones(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(ejecuciones.encolar(h.cuerpo(request, dto_reportes.PedidoEjecucion)), 202)

    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(ejecuciones.historial(request.GET.get("reporte"), h.entero(request, "limite", 200, 1, 2000)))


class Eliminar(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        pedido = h.cuerpo(request, dto_reportes.PedidoEliminarEjecuciones)
        return h.json(dto_reportes.EjecucionesEliminadas(eliminadas=ejecuciones.eliminar(pedido.ids)))


class Detalle(View):
    def get(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(ejecuciones.obtener(id_))
