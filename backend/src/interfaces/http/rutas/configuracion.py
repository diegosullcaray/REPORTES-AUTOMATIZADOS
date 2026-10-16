"""Configuración editable desde la web: perfil, ajustes generales, bases de datos y notificaciones (correo y Google Chat)."""

from __future__ import annotations

from fastapi import APIRouter

from aplicacion import dto as e
from aplicacion.casos_uso import configuracion, notificaciones

router = APIRouter(prefix="/api")


@router.get("/perfil", response_model=e.Perfil)
def perfil():
    return configuracion.perfil()


@router.get("/configuracion", response_model=e.ConfiguracionGeneral)
def leer_configuracion():
    return configuracion.configuracion()


@router.put("/configuracion", response_model=e.ConfiguracionGeneral)
def guardar_configuracion(pedido: e.PedidoConfiguracion):
    return configuracion.guardar_configuracion(pedido)


@router.get("/servidores", response_model=list[e.Servidor])
def servidores():
    return configuracion.servidores()


@router.post("/servidores/{nombre}/prueba", response_model=e.PruebaConexion)
def probar_servidor(nombre: str):
    return configuracion.probar_servidor(nombre)


@router.get("/notificaciones", response_model=e.Notificaciones)
def leer_notificaciones():
    return notificaciones.leer()


@router.put("/notificaciones", response_model=e.Notificaciones)
def guardar_notificaciones(pedido: e.PedidoNotificaciones):
    return notificaciones.guardar(pedido)


@router.post("/notificaciones/{canal}/prueba", response_model=e.PruebaNotificacion)
def probar_notificacion(canal: str):
    return notificaciones.probar(canal)
