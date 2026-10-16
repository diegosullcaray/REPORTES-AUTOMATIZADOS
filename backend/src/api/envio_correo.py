"""Correo de los archivos generados de un reporte, con la cuenta de Google autorizada (API de Gmail) y su firma.

Destinatarios por reporte en el .env (editables en la pestaña Correo). El envío es siempre a pedido de una persona;
`prueba` manda solo a CORREO_PRUEBA y sin copia, para revisar antes de enviar a la lista.
"""

from __future__ import annotations

import os

from mcp_google import cliente as g
from reportes.comun import correo, entrega_chat, entrega_gmail

from . import entorno
from . import esquemas as e
from . import servicios

MAX_CORREOS = 20
MAX_ADJUNTOS = 10
MAX_BYTES = 25 * 1024 * 1024
MAX_ASUNTO, MAX_MENSAJE = 200, 10_000


def _correos(texto: str) -> list[str]:
    lista = list(dict.fromkeys(c.strip() for c in texto.split(",") if c.strip()))
    malos = [c for c in lista if not entrega_chat.CORREO.match(c)]
    if malos:
        raise servicios.PeticionInvalida(f"Correo no válido: {', '.join(malos)}")
    if len(lista) > MAX_CORREOS:
        raise servicios.PeticionInvalida(f"Máximo {MAX_CORREOS} correos por campo.")
    return lista


def guardar_destinos(nombre: str, p: e.PedidoDestinosCorreo) -> e.ReporteDetalle:
    """Guarda en el .env a quién se envían los archivos del reporte y a quién va con copia."""
    servicios.reporte(nombre)
    cambios = {entrega_gmail.variable_para(nombre): ",".join(_correos(p.para)), entrega_gmail.variable_cc(nombre): ",".join(_correos(p.cc))}
    entorno.escribir(servicios.ENV, cambios)
    for variable, valor in cambios.items():
        if valor:
            os.environ[variable] = valor
        else:
            os.environ.pop(variable, None)
    return servicios.detalle(nombre)


def firma() -> e.FirmaGmail:
    try:
        return e.FirmaGmail(html=g.firma_gmail(g.token_de_acceso()))
    except g.GoogleError as exc:
        raise servicios.PeticionInvalida(str(exc)) from exc


def enviar(nombre: str, p: e.PedidoEnvioArchivos) -> e.PruebaNotificacion:
    servicios.reporte(nombre)
    asunto, mensaje = p.asunto.strip(), p.mensaje.strip()
    if not asunto or len(asunto) > MAX_ASUNTO or len(mensaje) > MAX_MENSAJE:
        raise servicios.PeticionInvalida(f"Escribe un asunto (máx. {MAX_ASUNTO} caracteres) y un mensaje de hasta {MAX_MENSAJE}.")
    if not p.archivos or len(p.archivos) > MAX_ADJUNTOS:
        raise servicios.PeticionInvalida(f"Elige de 1 a {MAX_ADJUNTOS} archivos.")
    if p.prueba:
        para, cc, asunto = [os.getenv("CORREO_PRUEBA", correo.CORREO_PRUEBA_DEFECTO).strip()], [], f"[PRUEBA] {asunto}"
    else:
        para, cc = _correos(",".join(p.para)), _correos(",".join(p.cc))
        if not para:
            raise servicios.PeticionInvalida("Indica al menos un destinatario.")
    generados = {a.nombre for a in servicios.archivos(nombre)}
    if desconocidos := [a for a in p.archivos if a not in generados]:
        raise servicios.PeticionInvalida(f"No es un archivo generado del reporte: {', '.join(desconocidos)}")
    rutas = [servicios.ruta_descarga(nombre, a) for a in dict.fromkeys(p.archivos)]
    if sum(r.stat().st_size for r in rutas) > MAX_BYTES:
        raise servicios.PeticionInvalida(f"Los adjuntos pesan más de {MAX_BYTES // 1024 // 1024} MB.")
    try:
        token = g.token_de_acceso()
        html_firma = g.firma_gmail(token) if p.con_firma else ""
        g.enviar_mensaje(token, g.armar_correo(para, cc, asunto, mensaje, html_firma, rutas))
    except g.GoogleError as exc:
        return e.PruebaNotificacion(ok=False, detalle=str(exc))
    return e.PruebaNotificacion(ok=True, detalle=f"Correo enviado a {', '.join(para)}" + (f" (copia: {', '.join(cc)})" if cc else ""))
