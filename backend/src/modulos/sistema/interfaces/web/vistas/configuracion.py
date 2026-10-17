"""Ajustes generales, perfil y bases de datos (servidores SQL Server) editables desde la web."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.sistema.aplicacion import dto as dto_sistema
from modulos.sistema.aplicacion.casos_uso import configuracion


class Perfil(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.perfil())


class Configuracion(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.configuracion())

    def put(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.guardar_configuracion(h.cuerpo(request, dto_sistema.PedidoConfiguracion)))


class Servidores(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(configuracion.servidores())


class ServidorPrueba(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(configuracion.probar_servidor(nombre))
