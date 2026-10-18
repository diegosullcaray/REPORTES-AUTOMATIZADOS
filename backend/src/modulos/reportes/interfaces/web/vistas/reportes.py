"""Catálogo de reportes, su detalle, verificación de tablas, archivos generados y envío por correo o Chat."""

from __future__ import annotations

from django.http import FileResponse, HttpRequest, HttpResponse
from django.views import View

from core import http as h
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion.casos_uso import archivos, catalogo, correo_reporte, crear_reporte, ejecuciones, etiquetas, verificacion


class Catalogo(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(catalogo.catalogo())

    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(crear_reporte.crear(h.cuerpo(request, dto_reportes.PedidoReporteNuevo)), status=201)


class Detalle(View):
    def get(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(catalogo.detalle(nombre))


class Script(View):
    def get(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(catalogo.script(nombre))

    def put(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(catalogo.guardar_script(nombre, h.cuerpo(request, dto_reportes.PedidoScript)))


class Grupos(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(crear_reporte.listar_grupos())

    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(crear_reporte.crear_grupo(h.cuerpo(request, dto_reportes.PedidoGrupo)), status=201)


class GrupoDetalle(View):
    def delete(self, request: HttpRequest, id_: str) -> HttpResponse:
        crear_reporte.eliminar_grupo(id_)
        return h.json({"ok": True})


class Chat(View):
    def put(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(catalogo.guardar_chat(nombre, h.cuerpo(request, dto_reportes.PedidoChat)))


class CorreoDestinos(View):
    def put(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(correo_reporte.guardar_destinos(nombre, h.cuerpo(request, dto_reportes.PedidoDestinosCorreo)))


class CorreoEnviar(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(correo_reporte.enviar(nombre, h.cuerpo(request, dto_reportes.PedidoEnvioArchivos)))


class Verificacion(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(verificacion.verificar(nombre, h.cuerpo(request, dto_reportes.PedidoCorte).fecha_corte))


class Solicitud(View):
    def post(self, request: HttpRequest, nombre: str) -> HttpResponse:
        return h.json(verificacion.guardar_solicitud(nombre, h.cuerpo(request, dto_reportes.PedidoCorte).fecha_corte))


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


class Etiquetas(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return h.json(etiquetas.listar())

    def post(self, request: HttpRequest) -> HttpResponse:
        return h.json(etiquetas.crear(h.cuerpo(request, dto_reportes.PedidoEtiqueta)), status=201)


class EtiquetaDetalle(View):
    def put(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(etiquetas.actualizar(id_, h.cuerpo(request, dto_reportes.PedidoEtiqueta)))

    def delete(self, request: HttpRequest, id_: str) -> HttpResponse:
        etiquetas.eliminar(id_)
        return h.json({"ok": True})


class GrupoEtiquetas(View):
    def put(self, request: HttpRequest, id_: str) -> HttpResponse:
        return h.json(crear_reporte.asignar_etiquetas(id_, h.cuerpo(request, dto_reportes.PedidoEtiquetasGrupo)))
