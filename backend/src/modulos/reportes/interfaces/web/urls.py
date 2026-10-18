"""Rutas del módulo de reportes (catálogo, validación de tablas y ejecuciones)."""

from django.urls import path

from .vistas import ejecuciones, firma, reportes, validacion

urlpatterns = [
    path("api/reportes", reportes.Catalogo.as_view()),
    path("api/grupos", reportes.Grupos.as_view()),
    path("api/grupos/<str:id_>", reportes.GrupoDetalle.as_view()),
    path("api/etiquetas", reportes.Etiquetas.as_view()),
    path("api/etiquetas/<str:id_>", reportes.EtiquetaDetalle.as_view()),
    path("api/grupos/<str:id_>/etiquetas", reportes.GrupoEtiquetas.as_view()),
    path("api/reportes/<str:nombre>", reportes.Detalle.as_view()),
    path("api/reportes/<str:nombre>/script", reportes.Script.as_view()),
    path("api/reportes/<str:nombre>/chat", reportes.Chat.as_view()),
    path("api/reportes/<str:nombre>/correo-destinos", reportes.CorreoDestinos.as_view()),
    path("api/reportes/<str:nombre>/correo/enviar", reportes.CorreoEnviar.as_view()),
    path("api/reportes/<str:nombre>/verificacion", reportes.Verificacion.as_view()),
    path("api/reportes/<str:nombre>/solicitud", reportes.Solicitud.as_view()),
    path("api/reportes/<str:nombre>/archivos", reportes.Archivos.as_view()),
    path("api/reportes/<str:nombre>/archivos/<str:archivo>/vista-previa", reportes.VistaPrevia.as_view()),
    path("api/reportes/<str:nombre>/archivos/<str:archivo>", reportes.Descarga.as_view()),
    path("api/reportes/<str:nombre>/envio", reportes.Envio.as_view()),
    path("api/google/firma", firma.Firma.as_view()),
    path("api/validacion/<str:grupo>", validacion.Verificar.as_view()),
    path("api/validacion/<str:grupo>/historial", validacion.Historial.as_view()),
    path("api/validacion/<str:grupo>/chat", validacion.Chat.as_view()),
    path("api/validacion/<str:grupo>/chat/enviar", validacion.ChatEnviar.as_view()),
    path("api/validacion/<str:grupo>/solicitud", validacion.Solicitud.as_view()),
    path("api/ejecuciones", ejecuciones.Ejecuciones.as_view()),
    path("api/ejecuciones/eliminar", ejecuciones.Eliminar.as_view()),
    path("api/ejecuciones/<str:id_>", ejecuciones.Detalle.as_view()),
]
