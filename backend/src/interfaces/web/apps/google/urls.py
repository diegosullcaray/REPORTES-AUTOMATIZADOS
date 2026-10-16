from django.urls import path

from . import views

urlpatterns = [
    path("api/google/firma", views.Firma.as_view()),
    path("api/mcp/google", views.Mcp.as_view()),
    path("api/mcp/google/autorizar", views.Autorizar.as_view()),
    path("api/mcp/google/codigo", views.Codigo.as_view()),
    path("api/mcp/google/autorizacion", views.Autorizacion.as_view()),
    path("api/mcp/google/<str:servicio>/herramientas", views.Herramientas.as_view()),
    path("api/mcp/google/<str:servicio>/ejecutar", views.Ejecutar.as_view()),
    path("api/mcp/google/<str:servicio>/enviar", views.Enviar.as_view()),
]
