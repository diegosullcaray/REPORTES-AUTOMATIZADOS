"""Cliente de pruebas de la API (Django): mismo uso que el de `requests` (`json=`, `.text`, `cookies.set`) para no repetir andamiaje en cada prueba."""

from __future__ import annotations

import json as _json
from http.cookies import SimpleCookie

from django.test import Client


class _Galletas(SimpleCookie):
    def set(self, nombre: str, valor: str) -> None:
        self[nombre] = valor


class TestClient(Client):
    __test__ = False  # no es una clase de pruebas para pytest

    def __init__(self) -> None:
        super().__init__()
        self.cookies = _Galletas()

    def request(self, **request):
        respuesta = super().request(**request)
        if not respuesta.streaming:
            respuesta.text = respuesta.content.decode("utf-8")
        return respuesta

    def _json(self, metodo, ruta, json, extra):
        return metodo(ruta, data=_json.dumps(json) if json is not None else "", content_type="application/json", **extra)

    def post(self, path, data=None, *, json=None, **extra):
        return self._json(super().post, path, json if json is not None else data, extra)

    def put(self, path, data=None, *, json=None, **extra):
        return self._json(super().put, path, json if json is not None else data, extra)
