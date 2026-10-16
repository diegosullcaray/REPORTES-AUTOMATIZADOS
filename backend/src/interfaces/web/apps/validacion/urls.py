from django.urls import path

from . import views

urlpatterns = [
    path("api/validacion/<str:grupo>", views.Verificar.as_view()),
    path("api/validacion/<str:grupo>/historial", views.Historial.as_view()),
    path("api/validacion/<str:grupo>/chat", views.Chat.as_view()),
    path("api/validacion/<str:grupo>/chat/enviar", views.ChatEnviar.as_view()),
    path("api/validacion/<str:grupo>/solicitud", views.Solicitud.as_view()),
]
