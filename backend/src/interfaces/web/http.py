"""Utilidades HTTP de la interfaz web: respuestas JSON, lectura validada del cuerpo y de la consulta, y errores con su código.

Los contratos son los DTO de `aplicacion/dto.py` (Pydantic): la API responde el mismo JSON que antes y los errores de validación
mantienen el formato `{"detail": [{"loc", "msg", "type"}]}` que ya interpreta el frontend.
"""

from __future__ import annotations

from datetime import date
from typing import TypeVar

from django.http import HttpRequest, JsonResponse
from pydantic import BaseModel, ValidationError

M = TypeVar("M", bound=BaseModel)
_VERDADEROS = {"true", "1", "yes", "on", "si", "sí"}


class ErrorHttp(Exception):
    """Respuesta de error con su código y el `detail` que verá el frontend (texto o lista de errores de validación)."""

    def __init__(self, status: int, detalle: object):
        super().__init__(str(detalle))
        self.status, self.detalle = status, detalle


def json(valor: object, status: int = 200) -> JsonResponse:
    """Modelo, lista de modelos o dato simple → JSON (sin escapar tildes)."""
    return JsonResponse(_a_json(valor), status=status, safe=False, json_dumps_params={"ensure_ascii": False})


def _a_json(valor: object) -> object:
    if isinstance(valor, BaseModel):
        return valor.model_dump(mode="json")
    if isinstance(valor, list):
        return [_a_json(v) for v in valor]
    return valor


def error(status: int, detalle: object) -> JsonResponse:
    return json({"detail": detalle}, status)


def _errores(donde: str, exc: ValidationError) -> list[dict]:
    return [{"loc": [donde, *map(str, e["loc"])], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]


def cuerpo(request: HttpRequest, modelo: type[M]) -> M:
    """El cuerpo JSON validado con el DTO; un cuerpo inválido es 422 con la lista de errores."""
    try:
        return modelo.model_validate_json(request.body or b"{}")
    except ValidationError as exc:
        raise ErrorHttp(422, _errores("body", exc)) from exc


def _fallo_consulta(nombre: str, msg: str, tipo: str) -> ErrorHttp:
    return ErrorHttp(422, [{"loc": ["query", nombre], "msg": msg, "type": tipo}])


def entero(request: HttpRequest, nombre: str, defecto: int, minimo: int, maximo: int) -> int:
    """Parámetro de consulta entero dentro de un rango."""
    crudo = request.GET.get(nombre)
    if crudo is None:
        return defecto
    try:
        valor = int(crudo)
    except ValueError:
        raise _fallo_consulta(nombre, "Input should be a valid integer", "int_parsing") from None
    if valor < minimo:
        raise _fallo_consulta(nombre, f"Input should be greater than or equal to {minimo}", "greater_than_equal")
    if valor > maximo:
        raise _fallo_consulta(nombre, f"Input should be less than or equal to {maximo}", "less_than_equal")
    return valor


def fecha(request: HttpRequest, nombre: str) -> date | None:
    """Parámetro de consulta AAAA-MM-DD, o None si no viene."""
    crudo = request.GET.get(nombre)
    if not crudo:
        return None
    try:
        return date.fromisoformat(crudo)
    except ValueError:
        raise _fallo_consulta(nombre, "Input should be a valid date or datetime", "date_from_datetime_parsing") from None


def booleano(request: HttpRequest, nombre: str) -> bool:
    return request.GET.get(nombre, "").lower() in _VERDADEROS
