"""Correo de los archivos generados de un reporte, con la cuenta de Google autorizada (API de Gmail) y su firma.

Destinatarios por reporte en el .env (editables en la pestaña Correo). El envío es siempre a pedido de una persona;
`prueba` manda solo a CORREO_PRUEBA y sin copia, para revisar antes de enviar a la lista.
"""

from __future__ import annotations

from modulos.notificaciones.aplicacion import destinatarios
from core.excepciones import PeticionInvalida
from modulos.notificaciones.dominio import entregas
from core.excepciones import ErrorIntegracion

from modulos.reportes.aplicacion.casos_uso.archivos import archivos, ruta_descarga
from modulos.reportes.aplicacion.casos_uso.catalogo import detalle, reporte
from core import dto as dto_nucleo
from core.puertos import nucleo
from modulos.integraciones.aplicacion import mensajeria as google
from modulos.reportes.aplicacion import dto as dto_reportes

MAX_CORREOS = 20
MAX_ADJUNTOS = 10
MAX_BYTES = 25 * 1024 * 1024
MAX_ASUNTO, MAX_MENSAJE = 200, 10_000


def _correos(texto: str) -> list[str]:
    return destinatarios.normalizar(texto, MAX_CORREOS)


def guardar_destinos(nombre: str, p: dto_reportes.PedidoDestinosCorreo) -> dto_reportes.ReporteDetalle:
    """Guarda en el .env a quién se envían los archivos del reporte y a quién va con copia."""
    reporte(nombre)
    nucleo().entorno.guardar({entregas.variable_correo_para(nombre): ",".join(_correos(p.para)),
                               entregas.variable_correo_cc(nombre): ",".join(_correos(p.cc))})
    return detalle(nombre)


def firma() -> dto_reportes.FirmaGmail:
    try:
        return dto_reportes.FirmaGmail(html=google.firma_gmail(google.token_de_acceso()))
    except ErrorIntegracion as exc:
        raise PeticionInvalida(str(exc)) from exc


def enviar(nombre: str, p: dto_reportes.PedidoEnvioArchivos) -> dto_nucleo.PruebaNotificacion:
    reporte(nombre)
    asunto, mensaje = p.asunto.strip(), p.mensaje.strip()
    if not asunto or len(asunto) > MAX_ASUNTO or len(mensaje) > MAX_MENSAJE:
        raise PeticionInvalida(f"Escribe un asunto (máx. {MAX_ASUNTO} caracteres) y un mensaje de hasta {MAX_MENSAJE}.")
    if not p.archivos or len(p.archivos) > MAX_ADJUNTOS:
        raise PeticionInvalida(f"Elige de 1 a {MAX_ADJUNTOS} archivos.")
    if p.prueba:
        para, cc, asunto = [nucleo().entorno.leer("CORREO_PRUEBA", entregas.CORREO_PRUEBA_DEFECTO).strip()], [], f"[PRUEBA] {asunto}"
    else:
        para, cc = _correos(",".join(p.para)), _correos(",".join(p.cc))
        if not para:
            raise PeticionInvalida("Indica al menos un destinatario.")
    generados = {a.nombre for a in archivos(nombre)}
    if desconocidos := [a for a in p.archivos if a not in generados]:
        raise PeticionInvalida(f"No es un archivo generado del reporte: {', '.join(desconocidos)}")
    rutas = [ruta_descarga(nombre, a) for a in dict.fromkeys(p.archivos)]
    if sum(r.stat().st_size for r in rutas) > MAX_BYTES:
        raise PeticionInvalida(f"Los adjuntos pesan más de {MAX_BYTES // 1024 // 1024} MB.")
    try:
        token = google.token_de_acceso()
        html_firma = google.firma_gmail(token) if p.con_firma else ""
        google.enviar_mensaje(token, google.armar_correo(para, cc, asunto, mensaje, html_firma, rutas))
    except ErrorIntegracion as exc:
        return dto_nucleo.PruebaNotificacion(ok=False, detalle=str(exc))
    return dto_nucleo.PruebaNotificacion(ok=True, detalle=f"Correo enviado a {', '.join(para)}" + (f" (copia: {', '.join(cc)})" if cc else ""))
