"""API HTTP de la interfaz web de reportes (capa de interfaces: solo traduce HTTP a casos de uso).

Capas (de afuera hacia adentro; la dependencia solo apunta hacia adentro):
  interfaces/http   rutas por tema (`rutas/`), sesión y traducción de errores a códigos (404 / 422)
  aplicacion        casos de uso, puertos y contratos (`dto.py`)
  dominio           reglas puras del negocio
  infraestructura   base de datos, Excel, correo, Google, .env, cola de ejecuciones (conectados en `composicion.py`)

Arranque, solo local (la web en Next.js la consume por proxy en /api):
  python -m uvicorn interfaces.http.app:app --app-dir src --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import composicion  # noqa: F401 - conecta los adaptadores reales a los puertos
from aplicacion.casos_uso import sesion
from aplicacion.errores import NoEncontrado, PeticionInvalida
from aplicacion.puertos import puertos

from .rutas import configuracion, ejecuciones, google, reportes, validacion
from .rutas import sesion as rutas_sesion


@asynccontextmanager
async def _vida(_: FastAPI):
    puertos().cola.iniciar()
    yield


app = FastAPI(title="Reportes automatizados", lifespan=_vida)


@app.middleware("http")
async def _exigir_sesion(request: Request, siguiente):
    """Todo /api exige cookie de sesión válida salvo iniciar sesión y consultar si la hay."""
    libre = request.url.path == "/api/sesion"
    if request.url.path.startswith("/api") and not libre and not sesion.leer(request.cookies.get(sesion.COOKIE)):
        return JSONResponse(status_code=401, content={"detail": "Inicia sesión para continuar"})
    return await siguiente(request)


@app.exception_handler(PeticionInvalida)
async def _invalida(_: Request, exc: PeticionInvalida):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(NoEncontrado)
async def _no_encontrado(_: Request, exc: NoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


for modulo in (rutas_sesion, reportes, validacion, ejecuciones, configuracion, google):
    app.include_router(modulo.router)
