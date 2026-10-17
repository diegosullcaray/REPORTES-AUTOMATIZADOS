"""Firma de Gmail para el correo de los archivos de un reporte."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.reportes.aplicacion.casos_uso import correo_reporte


class Firma(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(correo_reporte.firma())
