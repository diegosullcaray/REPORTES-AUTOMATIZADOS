from django.urls import path

from . import views

urlpatterns = [
    path("api/reportes", views.Catalogo.as_view()),
    path("api/reportes/<str:nombre>", views.Detalle.as_view()),
    path("api/reportes/<str:nombre>/chat", views.Chat.as_view()),
    path("api/reportes/<str:nombre>/correo-destinos", views.CorreoDestinos.as_view()),
    path("api/reportes/<str:nombre>/correo/enviar", views.CorreoEnviar.as_view()),
    path("api/reportes/<str:nombre>/verificacion", views.Verificacion.as_view()),
    path("api/reportes/<str:nombre>/solicitud", views.Solicitud.as_view()),
    path("api/reportes/<str:nombre>/archivos", views.Archivos.as_view()),
    path("api/reportes/<str:nombre>/archivos/<str:archivo>/vista-previa", views.VistaPrevia.as_view()),
    path("api/reportes/<str:nombre>/archivos/<str:archivo>", views.Descarga.as_view()),
    path("api/reportes/<str:nombre>/envio", views.Envio.as_view()),
]
