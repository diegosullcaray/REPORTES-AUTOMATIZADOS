"""Inicio y cierre de sesión, y cambio de usuario o contraseña (credenciales en el .env)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from aplicacion import dto as e
from aplicacion.casos_uso import configuracion, sesion

router = APIRouter(prefix="/api")


@router.post("/sesion", response_model=e.Sesion)
def iniciar_sesion(pedido: e.PedidoSesion, respuesta: Response):
    try:
        usuario = sesion.iniciar(pedido.usuario, pedido.clave)
    except PermissionError as exc:
        raise HTTPException(429, str(exc)) from None
    if not usuario:
        raise HTTPException(401, "Usuario o contraseña incorrectos, o sin permiso para entrar")
    respuesta.set_cookie(sesion.COOKIE, sesion.emitir(usuario), max_age=sesion.DURACION, httponly=True, samesite="strict")
    return e.Sesion(usuario=usuario)


@router.put("/cuenta", response_model=e.Sesion)
def actualizar_cuenta(pedido: e.PedidoCuenta, request: Request, respuesta: Response):
    actual = sesion.leer(request.cookies.get(sesion.COOKIE)) or ""
    usuario = configuracion.actualizar_cuenta(actual, pedido)
    respuesta.set_cookie(sesion.COOKIE, sesion.emitir(usuario), max_age=sesion.DURACION, httponly=True, samesite="strict")  # el nombre puede haber cambiado
    return e.Sesion(usuario=usuario)


@router.get("/sesion", response_model=e.Sesion)
def sesion_actual(request: Request):
    usuario = sesion.leer(request.cookies.get(sesion.COOKIE))
    if not usuario:
        raise HTTPException(401, "Sin sesión")
    return e.Sesion(usuario=usuario)


@router.delete("/sesion", status_code=204)
def cerrar_sesion(respuesta: Response):
    respuesta.delete_cookie(sesion.COOKIE)
