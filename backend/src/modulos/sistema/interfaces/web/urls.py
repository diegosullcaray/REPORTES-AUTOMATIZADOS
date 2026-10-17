"""Rutas del módulo de sistema (sesión, cuenta, perfil, ajustes y servidores)."""

from django.urls import path

from .vistas import configuracion, sesion

urlpatterns = [
    path("api/sesion", sesion.Sesion.as_view()),
    path("api/cuenta", sesion.Cuenta.as_view()),
    path("api/perfil", configuracion.Perfil.as_view()),
    path("api/configuracion", configuracion.Configuracion.as_view()),
    path("api/servidores", configuracion.Servidores.as_view()),
    path("api/servidores/<str:nombre>/prueba", configuracion.ServidorPrueba.as_view()),
]
