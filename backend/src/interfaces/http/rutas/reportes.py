"""Catálogo de reportes, su detalle, verificación de tablas, archivos generados y envío por correo o Chat."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter
from fastapi.responses import FileResponse

from aplicacion import dto as e
from aplicacion.casos_uso import archivos, catalogo, correo_reporte, ejecuciones, verificacion

router = APIRouter(prefix="/api")


@router.get("/reportes", response_model=list[e.ReporteResumen])
def listar_reportes():
    return catalogo.catalogo()


@router.get("/reportes/{nombre}", response_model=e.ReporteDetalle)
def detalle_reporte(nombre: str):
    return catalogo.detalle(nombre)


@router.put("/reportes/{nombre}/chat", response_model=e.ReporteDetalle)
def guardar_chat_reporte(nombre: str, pedido: e.PedidoChat):
    return catalogo.guardar_chat(nombre, pedido)


@router.put("/reportes/{nombre}/correo-destinos", response_model=e.ReporteDetalle)
def guardar_destinos_correo(nombre: str, pedido: e.PedidoDestinosCorreo):
    return correo_reporte.guardar_destinos(nombre, pedido)


@router.post("/reportes/{nombre}/correo/enviar", response_model=e.PruebaNotificacion)
def enviar_archivos_correo(nombre: str, pedido: e.PedidoEnvioArchivos):
    return correo_reporte.enviar(nombre, pedido)


@router.get("/google/firma", response_model=e.FirmaGmail)
def firma_gmail():
    return correo_reporte.firma()


# ---- validación de tablas y solicitud a Producción (solo SELECT)
@router.post("/reportes/{nombre}/verificacion", response_model=e.Verificacion)
def verificar(nombre: str, pedido: e.PedidoCorte):
    return verificacion.verificar(nombre, pedido.fecha_corte)


@router.post("/reportes/{nombre}/solicitud", response_model=e.Solicitud)
def solicitud(nombre: str, pedido: e.PedidoCorte):
    return verificacion.guardar_solicitud(nombre, pedido.fecha_corte)


# ---- archivos generados
@router.get("/reportes/{nombre}/archivos", response_model=list[e.Archivo])
def listar_archivos(nombre: str):
    return archivos.archivos(nombre)


@router.get("/reportes/{nombre}/archivos/{archivo}/vista-previa", response_model=e.VistaPrevia)
def vista_previa(nombre: str, archivo: str):
    return archivos.vista_previa(nombre, archivo)


@router.get("/reportes/{nombre}/archivos/{archivo}")
def descargar(nombre: str, archivo: str, en_linea: bool = False):
    ruta = archivos.ruta_descarga(nombre, archivo)
    return FileResponse(ruta, filename=ruta.name, content_disposition_type="inline" if en_linea else "attachment")


# ---- correo (prueba -> conforme -> todos)
@router.get("/reportes/{nombre}/envio", response_model=e.EstadoEnvio)
def estado_envio(nombre: str, fecha_corte: date | None = None):
    return ejecuciones.estado_envio(nombre, fecha_corte)
