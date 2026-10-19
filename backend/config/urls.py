"""Rutas de la API: cada módulo aporta las suyas (`modulos/<módulo>/interfaces/web/urls.py`) bajo /api."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.urls import include, path

urlpatterns = [
    path("", include("modulos.sistema.interfaces.web.urls")),
    path("", include("modulos.reportes.interfaces.web.urls")),
    path("", include("modulos.notificaciones.interfaces.web.urls")),
    path("", include("modulos.integraciones.interfaces.web.urls")),
    path("", include("modulos.diccionario.interfaces.web.urls")),
]


def _no_encontrada(request: HttpRequest, exception: Exception) -> JsonResponse:
    return JsonResponse({"detail": "Not Found"}, status=404)


def _error_interno(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"detail": "Error interno de la API: revisa su consola."}, status=500)


handler404 = _no_encontrada
handler500 = _error_interno
