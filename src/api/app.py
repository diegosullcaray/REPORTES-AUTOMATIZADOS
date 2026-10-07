"""API HTTP de la interfaz web de reportes.

Capas (de afuera hacia adentro):
  app.py         presentación: rutas HTTP y traducción de errores a códigos (404 / 422)
  esquemas.py    contratos de entrada y salida
  servicios.py   casos de uso: catálogo, verificación, solicitud, archivos, vista previa, envío
  ejecuciones.py cola de un solo trabajador que corre `main.py` como subproceso
  reportes/      dominio y acceso a datos ya existentes (no se modifican desde aquí)

Arranque, solo local (la web en Next.js la consume por proxy en /api):
  python -m uvicorn api.app:app --app-dir src --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse

from . import ejecuciones, servicios
from . import esquemas as e


@asynccontextmanager
async def _vida(_: FastAPI):
    ejecuciones.iniciar()
    yield


app = FastAPI(title="Reportes automatizados", lifespan=_vida)


@app.exception_handler(servicios.PeticionInvalida)
async def _invalida(_: Request, exc: servicios.PeticionInvalida):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(servicios.NoEncontrado)
async def _no_encontrado(_: Request, exc: servicios.NoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


# ---- catálogo
@app.get("/api/reportes", response_model=list[e.ReporteResumen])
def listar_reportes():
    return servicios.catalogo()


@app.get("/api/reportes/{nombre}", response_model=e.ReporteDetalle)
def detalle_reporte(nombre: str):
    return servicios.detalle(nombre)


# ---- validación de tablas y solicitud a Producción (solo SELECT)
@app.post("/api/reportes/{nombre}/verificacion", response_model=e.Verificacion)
def verificar(nombre: str, pedido: e.PedidoCorte):
    return servicios.verificar(nombre, pedido.fecha_corte)


@app.post("/api/reportes/{nombre}/solicitud", response_model=e.Solicitud)
def solicitud(nombre: str, pedido: e.PedidoCorte):
    return servicios.guardar_solicitud(nombre, pedido.fecha_corte)


# ---- archivos generados
@app.get("/api/reportes/{nombre}/archivos", response_model=list[e.Archivo])
def archivos(nombre: str):
    return servicios.archivos(nombre)


@app.get("/api/reportes/{nombre}/archivos/{archivo}/vista-previa", response_model=e.VistaPrevia)
def vista_previa(nombre: str, archivo: str):
    return servicios.vista_previa(nombre, archivo)


@app.get("/api/reportes/{nombre}/archivos/{archivo}")
def descargar(nombre: str, archivo: str, en_linea: bool = False):
    ruta = servicios.ruta_descarga(nombre, archivo)
    return FileResponse(ruta, filename=ruta.name, content_disposition_type="inline" if en_linea else "attachment")


# ---- correo (prueba -> conforme -> todos)
@app.get("/api/reportes/{nombre}/envio", response_model=e.EstadoEnvio)
def estado_envio(nombre: str, fecha_corte: date | None = None):
    return servicios.estado_envio(nombre, fecha_corte)


# ---- ejecuciones
@app.post("/api/ejecuciones", response_model=e.Ejecucion, status_code=202)
def ejecutar(pedido: e.PedidoEjecucion):
    return ejecuciones.encolar(pedido.reporte, servicios.argumentos(pedido))


@app.get("/api/ejecuciones", response_model=list[e.Ejecucion])
def historial(reporte: str | None = None, limite: int = Query(200, ge=1, le=2000)):
    return ejecuciones.historial(reporte, limite)


@app.get("/api/ejecuciones/{id_}", response_model=e.EjecucionDetalle)
def ejecucion(id_: str):
    try:
        return ejecuciones.obtener(id_)
    except KeyError:
        raise HTTPException(404, "No existe esa ejecución") from None


# ---- configuración: general, servidores (sin secretos) y prueba de conexión
@app.get("/api/perfil", response_model=e.Perfil)
def perfil():
    return servicios.perfil()


@app.get("/api/configuracion", response_model=e.ConfiguracionGeneral)
def configuracion():
    return servicios.configuracion()



@app.get("/api/servidores", response_model=list[e.Servidor])
def servidores():
    return servicios.servidores()


@app.post("/api/servidores/{nombre}/prueba", response_model=e.PruebaConexion)
def probar_servidor(nombre: str):
    return servicios.probar_servidor(nombre)
