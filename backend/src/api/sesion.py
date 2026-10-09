"""Inicio de sesión con usuario y clave del .env, y cookie firmada.

Credenciales: `WEB_USUARIO` y `WEB_CLAVE` (solo en .env, nunca en código). Si faltan, nadie puede entrar.
La cookie se firma con `SESION_SECRETO` (.env); sin él se genera uno por proceso y las sesiones caen al reiniciar.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time

COOKIE = "reportes_sesion"
DURACION = 8 * 3600
_INTENTOS_MAX, _VENTANA = 5, 300

_secreto_proceso = secrets.token_bytes(32)
_fallos: dict[str, list[float]] = {}


def _secreto() -> bytes:
    return os.environ.get("SESION_SECRETO", "").encode() or _secreto_proceso


def _nombre(usuario: str) -> str:
    return usuario.strip().lower()


def credenciales_validas(usuario: str, clave: str) -> bool:
    esperado_u, esperada_c = os.environ.get("WEB_USUARIO", "").strip(), os.environ.get("WEB_CLAVE", "")
    if not esperado_u or not esperada_c:
        return False  # sin configurar no entra nadie
    ok_u = hmac.compare_digest(_nombre(usuario).encode(), _nombre(esperado_u).encode())
    ok_c = hmac.compare_digest(clave.encode(), esperada_c.encode())
    return ok_u and ok_c


def iniciar(usuario: str, clave: str) -> str | None:
    """Devuelve el nombre de la sesión o None. Limita a 5 fallos por usuario cada 5 minutos."""
    clave_u, ahora = _nombre(usuario), time.time()
    recientes = [t for t in _fallos.get(clave_u, []) if ahora - t < _VENTANA]
    if len(recientes) >= _INTENTOS_MAX:
        raise PermissionError("Demasiados intentos. Espera unos minutos.")
    if usuario and clave and credenciales_validas(usuario, clave):
        _fallos.pop(clave_u, None)
        return clave_u
    _fallos[clave_u] = [*recientes, ahora]
    return None


def _firma(carga: str) -> str:
    return hmac.new(_secreto(), carga.encode(), hashlib.sha256).hexdigest()


def emitir(usuario: str) -> str:
    carga = base64.urlsafe_b64encode(f"{usuario}|{int(time.time()) + DURACION}".encode()).decode()
    return f"{carga}.{_firma(carga)}"


def leer(token: str | None) -> str | None:
    """Usuario de una cookie válida y vigente, o None."""
    try:
        carga, firma = (token or "").split(".")
        if not hmac.compare_digest(firma, _firma(carga)):
            return None
        usuario, vence = base64.urlsafe_b64decode(carga).decode().rsplit("|", 1)
        return usuario if int(vence) > time.time() else None
    except ValueError:
        return None
