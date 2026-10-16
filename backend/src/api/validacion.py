"""Historial de la validación masiva de tablas (una ficha por verificación) y envío por Google Chat del mensaje para actualizarlas.

Las fichas son JSON en data/outputs/validaciones/<grupo>/ (no versionadas). A quién se envía el mensaje va en el .env:
`ENTREGA_CHAT_VALIDACION_<GRUPO>` (correos separados por coma), editable desde la pantalla del responsable.
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from mcp_google import cliente as g
from reportes.comun import entrega_chat
from reportes.config import DIR_OUTPUTS

from . import entorno
from . import esquemas as e
from . import servicios

DIR = DIR_OUTPUTS / "validaciones"
MAX_FICHAS = 200          # por responsable; al pasar se borran las más antiguas
MAX_CHAT = 4000           # el mensaje de Chat admite 4096 caracteres
_PENDIENTE = {"DESACTUALIZADA", "NO EXISTE"}


def _grupo(grupo: str) -> str:
    if grupo not in servicios.GRUPOS_VALIDACION:
        raise servicios.NoEncontrado(f"Grupo desconocido: {grupo}")
    return grupo


def _carpeta(grupo: str) -> Path:
    return DIR / _grupo(grupo)


def _variable(grupo: str) -> str:
    return entrega_chat.variable(f"validacion-{_grupo(grupo)}")


def _guardar(x: e.EntradaValidacion) -> None:
    carpeta = _carpeta(x.grupo)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / f"{x.id}.json").write_text(x.model_dump_json(indent=2), encoding="utf-8")


def registrar(v: e.VerificacionGrupo) -> e.EntradaValidacion:
    """Guarda el resultado de una verificación (sin el detalle por tabla) y poda las fichas más antiguas."""
    ahora = datetime.now()
    x = e.EntradaValidacion(
        id=ahora.strftime("%Y%m%dT%H%M%S%f"), grupo=v.grupo, ejecutada=ahora.isoformat(timespec="seconds"), corte=v.corte, listo=v.listo,
        reportes=v.reportes, tablas_total=len(v.tablas), tablas_ok=sum(t.estado == "OK" for t in v.tablas),
        tablas_pendientes=sum(t.estado in _PENDIENTE for t in v.tablas), tablas_dudosas=sum(t.estado == "ERROR" for t in v.tablas), solicitud=v.solicitud,
    )
    _guardar(x)
    for vieja in sorted(_carpeta(v.grupo).glob("*.json"))[:-MAX_FICHAS]:
        vieja.unlink(missing_ok=True)
    return x


def historial(grupo: str, limite: int = 20) -> list[e.EntradaValidacion]:
    """De la más reciente a la más antigua."""
    carpeta = _carpeta(grupo)
    if not carpeta.is_dir():
        return []
    return [e.EntradaValidacion.model_validate_json(p.read_text(encoding="utf-8")) for p in sorted(carpeta.glob("*.json"), reverse=True)[:limite]]


def destinos(grupo: str) -> e.DestinosChat:
    return e.DestinosChat(destinatarios=entrega_chat.destinatarios(f"validacion-{_grupo(grupo)}"))


def guardar_destinos(grupo: str, p: e.PedidoChat) -> e.DestinosChat:
    correos = list(dict.fromkeys(c.strip() for c in p.destinatarios.split(",") if c.strip()))
    if malos := [c for c in correos if not entrega_chat.CORREO.match(c)]:
        raise servicios.PeticionInvalida(f"Correo no válido: {', '.join(malos)}")
    variable, valor = _variable(grupo), ",".join(correos)
    entorno.escribir(servicios.ENV, {variable: valor})
    if valor:
        os.environ[variable] = valor
    else:
        os.environ.pop(variable, None)
    return destinos(grupo)


def enviar_chat(grupo: str) -> e.PruebaNotificacion:
    """Envía por Google Chat, a cada compañero guardado, el mensaje de la última verificación."""
    ultima = next(iter(historial(grupo, 1)), None)
    if not ultima or not ultima.solicitud:
        raise servicios.PeticionInvalida("No hay mensaje que enviar: verifica primero (si todo está al día no hace falta pedir nada).")
    if len(ultima.solicitud) > MAX_CHAT:
        raise servicios.PeticionInvalida(f"El mensaje pasa de {MAX_CHAT} caracteres (límite de Chat): cópialo y envíalo por otro medio.")
    para = destinos(grupo).destinatarios
    if not para:
        raise servicios.PeticionInvalida("Guarda primero a quién se envía el mensaje.")
    try:
        token = g.token_de_acceso()
    except g.GoogleError as exc:
        return e.PruebaNotificacion(ok=False, detalle=str(exc))
    enviados, fallos = [], []
    for correo in para:
        try:
            g.enviar_chat(token, correo, ultima.solicitud)
            enviados.append(correo)
        except g.GoogleError as exc:
            fallos.append(f"{correo}: {exc}")
    if enviados:
        ultima.chat_enviado, ultima.chat_a = datetime.now().isoformat(timespec="seconds"), enviados
        _guardar(ultima)
    detalle = (f"Enviado por Google Chat a {', '.join(enviados)}. " if enviados else "") + " · ".join(fallos)
    return e.PruebaNotificacion(ok=not fallos, detalle=detalle.strip())
