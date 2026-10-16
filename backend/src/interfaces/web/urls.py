"""Rutas de la API: cada app de `apps/` aporta las suyas bajo /api."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.urls import include, path

urlpatterns = [
    path("", include("interfaces.web.apps.sesion.urls")),
    path("", include("interfaces.web.apps.reportes.urls")),
    path("", include("interfaces.web.apps.validacion.urls")),
    path("", include("interfaces.web.apps.ejecuciones.urls")),
    path("", include("interfaces.web.apps.configuracion.urls")),
    path("", include("interfaces.web.apps.google.urls")),
]


def _no_encontrada(request: HttpRequest, exception: Exception) -> JsonResponse:
    return JsonResponse({"detail": "Not Found"}, status=404)


def _error_interno(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"detail": "Error interno de la API: revisa su consola."}, status=500)


handler404 = _no_encontrada
handler500 = _error_interno
