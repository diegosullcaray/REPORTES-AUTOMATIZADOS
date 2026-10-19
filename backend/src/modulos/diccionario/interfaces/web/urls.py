"""Rutas del módulo diccionario."""

from django.urls import path

from .vistas import diccionario

urlpatterns = [
    path("api/diccionario/resumen", diccionario.Resumen.as_view()),
    path("api/diccionario/potencial", diccionario.Potencial.as_view()),
    path("api/diccionario/hallazgos", diccionario.Hallazgos.as_view()),
    path("api/diccionario/bases", diccionario.Bases.as_view()),
    path("api/diccionario/bases/<str:base>", diccionario.BaseDetalle.as_view()),
    path("api/diccionario/reportes/<str:codigo>", diccionario.ReporteDetalle.as_view()),
    path("api/diccionario/tablas/<str:nombre>", diccionario.TablaDetalle.as_view()),
    path("api/diccionario/procesos", diccionario.Procesos.as_view()),
    path("api/diccionario/procesos/<str:id_>", diccionario.ProcesoDetalle.as_view()),
    path("api/diccionario/procesos/<str:id_>/ejecutar", diccionario.ProcesoEjecutar.as_view()),
    path("api/diccionario/ejecuciones", diccionario.Ejecuciones.as_view()),
    path("api/diccionario/ejecuciones/<str:id_>", diccionario.EjecucionDetalle.as_view()),
]
