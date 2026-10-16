from django.urls import path

from . import views

urlpatterns = [
    path("api/sesion", views.Sesion.as_view()),
    path("api/cuenta", views.Cuenta.as_view()),
]
