"""Historial de la validación masiva de tablas (una ficha por verificación) y envío por Google Chat del mensaje para actualizarlas.

Las fichas las guarda el puerto del historial. A quién se envía el mensaje va en el .env:
`ENTREGA_CHAT_VALIDACION_<GRUPO>` (correos separados por coma), editable desde la pantalla del responsable.
"""

from __future__ import annotations

from datetime import date, datetime

from modulos.notificaciones.aplicacion import destinatarios
from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.notificaciones.dominio import entregas
from core.excepciones import ErrorIntegracion

from modulos.reportes.aplicacion.casos_uso.verificacion import GRUPOS_VALIDACION, verificar_grupo
from core import dto as dto_nucleo
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.integraciones.aplicacion import mensajeria as google
from modulos.reportes.aplicacion.puertos import puertos

MAX_FICHAS = 200          # por responsable; al pasar se borran las más antiguas
MAX_CHAT = 4000           # el mensaje de Chat admite 4096 caracteres
_PENDIENTE = {"DESACTUALIZADA", "NO EXISTE"}


def _grupo(grupo: str) -> str:
    if grupo not in GRUPOS_VALIDACION:
        raise NoEncontrado(f"Grupo desconocido: {grupo}")
    return grupo


def _variable(grupo: str) -> str:
    return entregas.variable_chat(f"validacion-{_grupo(grupo)}")


def registrar(v: dto_reportes.VerificacionGrupo) -> dto_reportes.EntradaValidacion:
    """Guarda el resultado de una verificación (sin el detalle por tabla) y poda las fichas más antiguas."""
    ahora = datetime.now()
    x = dto_reportes.EntradaValidacion(
        id=ahora.strftime("%Y%m%dT%H%M%S%f"), grupo=v.grupo, ejecutada=ahora.isoformat(timespec="seconds"), corte=v.corte, listo=v.listo,
        reportes=v.reportes, tablas_total=len(v.tablas), tablas_ok=sum(t.estado == "OK" for t in v.tablas),
        tablas_pendientes=sum(t.estado in _PENDIENTE for t in v.tablas), tablas_dudosas=sum(t.estado == "ERROR" for t in v.tablas), solicitud=v.solicitud,
    )
    almacen = puertos().historial_validacion
    almacen.guardar(x)
    almacen.podar(v.grupo, MAX_FICHAS)
    return x


def verificar(grupo: str, fecha: date | None) -> dto_reportes.VerificacionGrupo:
    """Verifica las tablas del grupo y deja el resultado en el historial."""
    resultado = verificar_grupo(grupo, fecha)
    try:
        registrar(resultado)
    except OSError:
        pass  # el historial es secundario: si no se puede escribir, el resultado de la verificación igual se devuelve
    return resultado


def historial(grupo: str, limite: int = 20) -> list[dto_reportes.EntradaValidacion]:
    """De la más reciente a la más antigua."""
    return puertos().historial_validacion.listar(_grupo(grupo), limite)


def destinos(grupo: str) -> dto_reportes.DestinosChat:
    return dto_reportes.DestinosChat(destinatarios=destinatarios.leer(_variable(grupo)))


def guardar_destinos(grupo: str, p: dto_reportes.PedidoChat) -> dto_reportes.DestinosChat:
    destinatarios.guardar(_variable(grupo), p.destinatarios)
    return destinos(grupo)


def enviar_chat(grupo: str) -> dto_nucleo.PruebaNotificacion:
    """Envía por Google Chat, a cada compañero guardado, el mensaje de la última verificación."""
    ultima = next(iter(historial(grupo, 1)), None)
    if not ultima or not ultima.solicitud:
        raise PeticionInvalida("No hay mensaje que enviar: verifica primero (si todo está al día no hace falta pedir nada).")
    if len(ultima.solicitud) > MAX_CHAT:
        raise PeticionInvalida(f"El mensaje pasa de {MAX_CHAT} caracteres (límite de Chat): cópialo y envíalo por otro medio.")
    para = destinos(grupo).destinatarios
    if not para:
        raise PeticionInvalida("Guarda primero a quién se envía el mensaje.")
    try:
        token = google.token_de_acceso()
    except ErrorIntegracion as exc:
        return dto_nucleo.PruebaNotificacion(ok=False, detalle=str(exc))
    enviados, fallos = [], []
    for correo in para:
        try:
            google.enviar_chat(token, correo, ultima.solicitud)
            enviados.append(correo)
        except ErrorIntegracion as exc:
            fallos.append(f"{correo}: {exc}")
    if enviados:
        ultima.chat_enviado, ultima.chat_a = datetime.now().isoformat(timespec="seconds"), enviados
        puertos().historial_validacion.guardar(ultima)
    detalle = (f"Enviado por Google Chat a {', '.join(enviados)}. " if enviados else "") + " · ".join(fallos)
    return dto_nucleo.PruebaNotificacion(ok=not fallos, detalle=detalle.strip())
