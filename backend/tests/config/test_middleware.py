"""Middleware de la API (config/middleware.py): sesión obligatoria y traducción de errores a códigos HTTP."""

from django.http import HttpResponse
from django.test import RequestFactory

from modulos.sistema.aplicacion.casos_uso import sesion
from core.excepciones import NoEncontrado, PeticionInvalida
from core import http as h
from config.middleware import TraducirErrores, sesion_obligatoria

RF = RequestFactory()


def _con_sesion(ruta):
    r = RF.get(ruta)
    r.COOKIES[sesion.COOKIE] = sesion.emitir("ana")
    return r


def test_la_api_exige_sesion_salvo_iniciar_y_consultarla():
    pasa = sesion_obligatoria(lambda request: HttpResponse("ok"))
    assert pasa(RF.get("/api/reportes")).status_code == 401
    assert pasa(RF.get("/api/sesion")).status_code == 200            # iniciar sesión y consultar si la hay
    assert pasa(_con_sesion("/api/reportes")).status_code == 200
    assert pasa(RF.get("/fuera-de-la-api")).status_code == 200


def test_cada_error_de_negocio_tiene_su_codigo():
    t = TraducirErrores(lambda request: HttpResponse())
    r = RF.get("/x")
    assert t.process_exception(r, PeticionInvalida("fecha mala")).status_code == 422
    assert t.process_exception(r, NoEncontrado("no existe")).status_code == 404
    assert t.process_exception(r, h.ErrorHttp(429, "mucho")).status_code == 429
    assert t.process_exception(r, RuntimeError("falla real")) is None   # sigue como error 500
