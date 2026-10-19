"""Diccionario de datos de los reportes MIS: resumen, reportes, tablas, calidad, lo que aporta a los reportes propios y sus procesos."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.diccionario.aplicacion.casos_uso import diccionario, procesos


class Resumen(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(diccionario.resumen())


class Potencial(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(diccionario.potencial())


class Hallazgos(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(diccionario.hallazgos())


class Bases(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(diccionario.bases())


class BaseDetalle(View):
    def get(self, request: HttpRequest, base: str) -> HttpResponse:
        return h.json(diccionario.base(base))


class ReporteDetalle(View):
    def get(self, request: HttpRequest, codigo: str) -> HttpResponse:
        return h.json(diccionario.reporte(codigo))


class TablaDetalle(View):
    def get(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(diccionario.tabla(nombre))


class Procesos(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(procesos.catalogo())


class ProcesoDetalle(View):
    def get(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(procesos.detalle(id_))


class ProcesoEjecutar(View):
    def post(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(procesos.ejecutar(id_), status=202)


class Ejecuciones(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(procesos.historial(request.GET.get("proceso") or None))


class EjecucionDetalle(View):
    def get(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(procesos.obtener(id_))
