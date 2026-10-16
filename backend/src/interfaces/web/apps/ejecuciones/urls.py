from django.urls import path

from . import views

urlpatterns = [
    path("api/ejecuciones", views.Ejecuciones.as_view()),
    path("api/ejecuciones/eliminar", views.Eliminar.as_view()),
    path("api/ejecuciones/<str:id_>", views.Detalle.as_view()),
]
