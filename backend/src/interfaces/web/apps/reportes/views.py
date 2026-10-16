"""Catálogo de reportes, su detalle, verificación de tablas, archivos generados y envío por correo o Chat."""

from __future__ import annotations

from django.http import FileResponse, HttpRequest, HttpResponse
from django.views import View

from aplicacion import dto as e
from aplicacion.casos_uso import archivos, catalogo, correo_reporte, ejecuciones, verificacion
from interfaces.web import http as h


class Catalogo(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(catalogo.catalogo())


class Detalle(View):
    def get(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(catalogo.detalle(nombre))


class Chat(View):
    def put(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(catalogo.guardar_chat(nombre, h.cuerpo(request, e.PedidoChat)))


class CorreoDestinos(View):
    def put(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(correo_reporte.guardar_destinos(nombre, h.cuerpo(request, e.PedidoDestinosCorreo)))


class CorreoEnviar(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(correo_reporte.enviar(nombre, h.cuerpo(request, e.PedidoEnvioArchivos)))


class Verificacion(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(verificacion.verificar(nombre, h.cuerpo(request, e.PedidoCorte).fecha_corte))


class Solicitud(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(verificacion.guardar_solicitud(nombre, h.cuerpo(request, e.PedidoCorte).fecha_corte))


class Archivos(View):
    def get(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(archivos.archivos(nombre))


class VistaPrevia(View):
    def get(self, request: HttpRequest, nombre: str, archivo: str) -> HttpResponse:
        return h.json(archivos.vista_previa(nombre, archivo))


class Descarga(View):
    def get(self, request: HttpRequest, nombre: str, archivo: str) -> HttpResponse:
        ruta = archivos.ruta_descarga(nombre, archivo)
        return FileResponse(open(ruta, "rb"), as_attachment=not h.booleano(request, "en_linea"), filename=ruta.name)


class Envio(View):
    """Estado del correo del reporte (prueba → conforme → todos)."""

    def get(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(ejecuciones.estado_envio(nombre, h.fecha(request, "fecha_corte")))
