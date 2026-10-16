"""Validación masiva de las tablas de los reportes mensuales de un responsable (Piero / Erick): verificar, historial y mensaje por Chat."""

from __future__ import annotations

from fastapi import APIRouter, Query

from aplicacion import dto as e
from aplicacion.casos_uso import validacion, verificacion

router = APIRouter(prefix="/api/validacion")


@router.post("/{grupo}", response_model=e.VerificacionGrupo)
def verificar_grupo(grupo: str, pedido: e.PedidoCorte):
    return validacion.verificar(grupo, pedido.fecha_corte)


@router.get("/{grupo}/historial", response_model=list[e.EntradaValidacion])
def historial_validacion(grupo: str, limite: int = Query(20, ge=1, le=200)):
    return validacion.historial(grupo, limite)


@router.get("/{grupo}/chat", response_model=e.DestinosChat)
def destinos_chat_validacion(grupo: str):
    return validacion.destinos(grupo)


@router.put("/{grupo}/chat", response_model=e.DestinosChat)
def guardar_destinos_chat_validacion(grupo: str, pedido: e.PedidoChat):
    return validacion.guardar_destinos(grupo, pedido)


@router.post("/{grupo}/chat/enviar", response_model=e.PruebaNotificacion)
def enviar_chat_validacion(grupo: str):
    return validacion.enviar_chat(grupo)


@router.post("/{grupo}/solicitud", response_model=e.Solicitud)
def solicitud_grupo(grupo: str, pedido: e.PedidoCorte):
    return verificacion.guardar_solicitud_grupo(grupo, pedido.fecha_corte)
