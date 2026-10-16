from django.urls import path

from . import views

urlpatterns = [
    path("api/perfil", views.Perfil.as_view()),
    path("api/configuracion", views.Configuracion.as_view()),
    path("api/servidores", views.Servidores.as_view()),
    path("api/servidores/<str:nombre>/prueba", views.ServidorPrueba.as_view()),
    path("api/notificaciones", views.Notificaciones.as_view()),
    path("api/notificaciones/<str:canal>/prueba", views.NotificacionPrueba.as_view()),
]
