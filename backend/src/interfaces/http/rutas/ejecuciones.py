"""Ejecuciones: encolar un reporte, ver el historial y eliminar ejecuciones."""

from __future__ import annotations

from fastapi import APIRouter, Query

from aplicacion import dto as e
from aplicacion.casos_uso import ejecuciones

router = APIRouter(prefix="/api/ejecuciones")


@router.post("", response_model=e.Ejecucion, status_code=202)
def ejecutar(pedido: e.PedidoEjecucion):
    return ejecuciones.encolar(pedido)


@router.get("", response_model=list[e.Ejecucion])
def historial(reporte: str | None = None, limite: int = Query(200, ge=1, le=2000)):
    return ejecuciones.historial(reporte, limite)


@router.post("/eliminar", response_model=e.EjecucionesEliminadas)
def eliminar_ejecuciones(pedido: e.PedidoEliminarEjecuciones):
    return e.EjecucionesEliminadas(eliminadas=ejecuciones.eliminar(pedido.ids))


@router.get("/{id_}", response_model=e.EjecucionDetalle)
def ejecucion(id_: str):
    return ejecuciones.obtener(id_)
