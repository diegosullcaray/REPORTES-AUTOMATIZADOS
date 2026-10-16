"""MCP de Google Workspace: cliente OAuth, autorización, servidores MCP oficiales y envío directo."""

from __future__ import annotations

from fastapi import APIRouter

from aplicacion import dto as e
from aplicacion.casos_uso import google

router = APIRouter(prefix="/api/mcp/google")


@router.get("", response_model=e.GoogleMcp)
def leer_google_mcp():
    return google.leer()


@router.put("", response_model=e.GoogleMcp)
def guardar_google_mcp(pedido: e.PedidoGoogleMcp):
    return google.guardar(pedido)


@router.post("/autorizar", response_model=e.Autorizacion)
def autorizar_google(pedido: e.PedidoAutorizacion):
    return google.autorizar(pedido)


@router.post("/codigo", response_model=e.GoogleMcp)
def codigo_google(pedido: e.PedidoCodigo):
    return google.canjear(pedido)


@router.delete("/autorizacion", response_model=e.GoogleMcp)
def desconectar_google():
    return google.desconectar()


@router.post("/{servicio}/herramientas", response_model=e.PruebaMcp)
def herramientas_google(servicio: str):
    return google.herramientas(servicio)


@router.post("/{servicio}/ejecutar", response_model=e.PruebaNotificacion)
def ejecutar_google(servicio: str, pedido: e.PedidoEjecutarMcp):
    return google.ejecutar(servicio, pedido)


@router.post("/{servicio}/enviar", response_model=e.PruebaNotificacion)
def enviar_google(servicio: str, pedido: e.PedidoPruebaGoogle):
    return google.enviar(servicio, pedido)
