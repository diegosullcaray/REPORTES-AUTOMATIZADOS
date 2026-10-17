"""Rutas del módulo de integraciones (Google Workspace y MCP)."""

from django.urls import path

from .vistas import google

urlpatterns = [
    path("api/mcp/google", google.Mcp.as_view()),
    path("api/mcp/google/autorizar", google.Autorizar.as_view()),
    path("api/mcp/google/codigo", google.Codigo.as_view()),
    path("api/mcp/google/autorizacion", google.Autorizacion.as_view()),
    path("api/mcp/google/<str:servicio>/herramientas", google.Herramientas.as_view()),
    path("api/mcp/google/<str:servicio>/ejecutar", google.Ejecutar.as_view()),
    path("api/mcp/google/<str:servicio>/enviar", google.Enviar.as_view()),
]
