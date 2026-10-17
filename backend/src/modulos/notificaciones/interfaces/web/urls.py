"""Rutas del módulo de notificaciones."""

from django.urls import path

from .vistas import notificaciones

urlpatterns = [
    path("api/notificaciones", notificaciones.Notificaciones.as_view()),
    path("api/notificaciones/<str:canal>/prueba", notificaciones.NotificacionPrueba.as_view()),
]
