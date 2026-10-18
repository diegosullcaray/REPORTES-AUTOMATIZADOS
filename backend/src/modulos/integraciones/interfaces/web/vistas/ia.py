"""Conexiones con proveedores de IA por API key."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.integraciones.aplicacion import dto as dto_integraciones
from modulos.integraciones.aplicacion.casos_uso import ia


class Conexiones(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(ia.listar())

    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(ia.crear(h.cuerpo(request, dto_integraciones.PedidoIA)), status=201)


class Conexion(View):
    def put(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(ia.actualizar(id_, h.cuerpo(request, dto_integraciones.PedidoIAActualizar)))

    def delete(self, request: HttpRequest, id_: str) -> HttpResponse:
        ia.eliminar(id_)
        return h.json({"ok": True})


class Modelos(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(ia.modelos(h.cuerpo(request, dto_integraciones.PedidoModelos)))


class Probar(View):
    def post(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(ia.probar(id_))
