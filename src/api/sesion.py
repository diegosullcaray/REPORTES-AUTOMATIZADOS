"""Inicio de sesión con la cuenta de Windows y cookie firmada.

La clave se valida contra Windows (LogonUser, cuenta local o de dominio) y nunca se guarda ni se registra.
Quién puede entrar: `USUARIOS_WEB` en .env (separados por coma); si está vacío, solo el usuario que ejecuta la API.
La cookie se firma con `SESION_SECRETO` (.env); sin él se genera uno por proceso y las sesiones caen al reiniciar.
"""

from __future__ import annotations

import base64
import getpass
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
    """`DOMINIO\\ana` y `ana@dominio` se reducen a `ana`, en minúsculas."""
    return usuario.split("\\")[-1].split("@")[0].strip().lower()


def permitido(usuario: str) -> bool:
    lista = {_nombre(u) for u in os.environ.get("USUARIOS_WEB", "").split(",") if u.strip()}
    return _nombre(usuario) in (lista or {_nombre(getpass.getuser())})


def clave_valida_en_windows(usuario: str, clave: str) -> bool:
    try:
        import ctypes
        logon, cerrar = ctypes.windll.advapi32.LogonUserW, ctypes.windll.kernel32.CloseHandle
    except (AttributeError, OSError):
        return False  # fuera de Windows no hay con qué validar: se niega, no se acepta
    dominio, _, nombre = usuario.rpartition("\\")
    if "@" in nombre:
        dominio = None  # UPN: Windows resuelve el dominio solo
    token = ctypes.c_void_p()
    # 3 = inicio de sesión de red (no crea sesión interactiva); 0 = proveedor por defecto
    ok = logon(nombre, dominio or ("." if dominio is not None else None), clave, 3, 0, ctypes.byref(token))
    if ok:
        cerrar(token)
    return bool(ok)


def iniciar(usuario: str, clave: str) -> str | None:
    """Devuelve el nombre de la sesión o None. Limita a 5 fallos por usuario cada 5 minutos."""
    clave_u, ahora = _nombre(usuario), time.time()
    recientes = [t for t in _fallos.get(clave_u, []) if ahora - t < _VENTANA]
    if len(recientes) >= _INTENTOS_MAX:
        raise PermissionError("Demasiados intentos. Espera unos minutos.")
    if usuario and clave and permitido(usuario) and clave_valida_en_windows(usuario, clave):
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
