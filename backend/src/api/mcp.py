"""MCP de Google Workspace desde la web: configuración del cliente OAuth, autorización con código, servicios y pruebas.

Todo se guarda en el .env. El Client secret y el refresh token son de solo escritura: nunca vuelven al navegador.
Autorizar: la web pide la URL de Google, la persona da su consentimiento y Google redirige con `?code=…`; la web
canjea ese código (o la persona lo pega a mano, solo o con la URL completa).
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
import sys
from urllib.parse import parse_qs, urlparse

from mcp_google import cliente as g
from mcp_google import servidor
from reportes.config import RAIZ

from . import entorno
from . import esquemas as e
from . import servicios

SERVIDOR = RAIZ / "src" / "mcp_google" / "servidor.py"
NIVELES = {"core", "extended", "complete"}
VARIABLES = {"client_id": "GOOGLE_OAUTH_CLIENT_ID", "client_secret": "GOOGLE_OAUTH_CLIENT_SECRET",
             "redirect_uri": "GOOGLE_OAUTH_REDIRECT_URI", "cuenta": "USER_GOOGLE_EMAIL"}
_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_pendientes: dict[str, tuple[str, str]] = {}   # state -> (code_verifier, redirect_uri), solo en memoria
_ultimo: list[str] = []                         # último state, para cuando se pega solo el código


def _env(variable: str) -> str:
    return os.getenv(variable, "").strip()


def _poner(cambios: dict[str, str]) -> None:
    entorno.escribir(servicios.ENV, cambios)
    for variable, valor in cambios.items():
        if valor:
            os.environ[variable] = valor
        else:
            os.environ.pop(variable, None)


def leer() -> e.GoogleMcp:
    activos = g.servicios_activos()
    autorizado = bool(_env("GOOGLE_OAUTH_REFRESH_TOKEN"))
    comando, args = "python", [str(SERVIDOR)]
    workspace_args = ["workspace-mcp", "--tools", *(s for s in activos), "--tool-tier", _env("GOOGLE_MCP_NIVEL") or "core"]
    if g.solo_lectura():
        workspace_args.append("--read-only")
    return e.GoogleMcp(
        client_id=_env("GOOGLE_OAUTH_CLIENT_ID"), secreto_configurado=bool(_env("GOOGLE_OAUTH_CLIENT_SECRET")),
        redirect_uri=_env("GOOGLE_OAUTH_REDIRECT_URI"), cuenta=_env("USER_GOOGLE_EMAIL"), autorizado=autorizado,
        solo_lectura=g.solo_lectura(), nivel=_env("GOOGLE_MCP_NIVEL") or "core", correo_prueba=_env("CORREO_PRUEBA"),
        servicios=[e.ServicioGoogle(id=s.id, nombre=s.nombre, descripcion=s.descripcion, activo=s.id in activos, envia=s.envia,
                                    scopes=list(s.scopes), falta_consentimiento=autorizado and s.id in activos and g.falta_consentimiento(s.id))
                   for s in g.SERVICIOS.values()],
        herramientas=[e.HerramientaMcp(nombre=h["name"], descripcion=h["description"]) for h in servidor.herramientas()],
        comando=comando, args=args, python=sys.executable,
        configuracion={"mcpServers": {"google-workspace": {"command": comando, "args": args}}},
        configuracion_workspace_mcp={"mcpServers": {"google_workspace": {"command": "uvx", "args": workspace_args, "env": {
            "GOOGLE_OAUTH_CLIENT_ID": _env("GOOGLE_OAUTH_CLIENT_ID") or "<client-id>",
            "GOOGLE_OAUTH_CLIENT_SECRET": "<client-secret del .env>",
            **({"USER_GOOGLE_EMAIL": _env("USER_GOOGLE_EMAIL")} if _env("USER_GOOGLE_EMAIL") else {}),
        }}}},
    )


def _validar(campo: str, valor: str) -> str:
    if not valor:
        return ""
    if any(c in valor for c in "\r\n#\"' "):
        raise servicios.PeticionInvalida(f"{VARIABLES[campo]}: no admite espacios, saltos de línea, # ni comillas.")
    if campo == "client_id" and not valor.endswith(".apps.googleusercontent.com"):
        raise servicios.PeticionInvalida("El Client ID termina en .apps.googleusercontent.com (cópialo de Google Cloud › Credenciales).")
    if campo == "redirect_uri" and urlparse(valor).scheme not in {"http", "https"}:
        raise servicios.PeticionInvalida("La URI de redirección debe empezar con http:// o https://.")
    if campo == "cuenta" and not _CORREO.match(valor):
        raise servicios.PeticionInvalida("USER_GOOGLE_EMAIL: escribe un correo válido.")
    return valor


def guardar(p: e.PedidoGoogleMcp) -> e.GoogleMcp:
    """Solo se cambian los campos enviados; texto vacío quita la variable."""
    cambios = {VARIABLES[c]: _validar(c, (getattr(p, c) or "").strip()) for c in p.model_fields_set if c in VARIABLES}
    if "servicios" in p.model_fields_set:
        desconocidos = [s for s in p.servicios or [] if s not in g.SERVICIOS]
        if desconocidos or not p.servicios:
            raise servicios.PeticionInvalida(f"Servicios no válidos: {', '.join(desconocidos)}" if desconocidos else "Activa al menos un servicio.")
        cambios["GOOGLE_MCP_SERVICIOS"] = ",".join(s for s in g.SERVICIOS if s in p.servicios)
    if "solo_lectura" in p.model_fields_set:
        cambios["GOOGLE_MCP_SOLO_LECTURA"] = "true" if p.solo_lectura else ""
    if "nivel" in p.model_fields_set:
        if p.nivel not in NIVELES:
            raise servicios.PeticionInvalida("El nivel de herramientas es core, extended o complete.")
        cambios["GOOGLE_MCP_NIVEL"] = "" if p.nivel == "core" else p.nivel
    if not cambios:
        raise servicios.PeticionInvalida("No hay ningún ajuste que guardar.")
    _poner(cambios)
    return leer()


def autorizar(p: e.PedidoAutorizacion) -> e.Autorizacion:
    redirect = _env("GOOGLE_OAUTH_REDIRECT_URI") or p.redirect_uri.strip()
    if urlparse(redirect).scheme not in {"http", "https"}:
        raise servicios.PeticionInvalida("Falta una URI de redirección válida.")
    if not _env("GOOGLE_OAUTH_CLIENT_SECRET"):
        raise servicios.PeticionInvalida("Guarda primero el Client secret de OAuth.")
    verificador = secrets.token_urlsafe(64)
    desafio = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    try:
        url = g.url_autorizacion(redirect, state, desafio, g.servicios_activos())
    except g.GoogleError as exc:
        raise servicios.PeticionInvalida(str(exc)) from exc
    _pendientes[state] = (verificador, redirect)
    _ultimo[:] = [state]
    return e.Autorizacion(url=url, redirect_uri=redirect)


def _separar(texto: str, state: str | None) -> tuple[str, str | None]:
    """Acepta el código solo o la URL completa a la que llevó Google (…?code=…&state=…)."""
    if "code=" in texto:
        q = parse_qs(urlparse(texto).query or texto.split("?", 1)[-1])
        if q.get("error"):
            raise servicios.PeticionInvalida(f"Google devolvió un error: {q['error'][0]}")
        return q.get("code", [""])[0], (q.get("state") or [state])[0]
    return texto, state


def canjear(p: e.PedidoCodigo) -> e.GoogleMcp:
    codigo, state = _separar(p.codigo.strip(), p.state)
    if not codigo:
        raise servicios.PeticionInvalida("Pega el código de autorización (o la URL completa a la que te llevó Google).")
    state = state or (_ultimo[0] if _ultimo else None)
    if not state or state not in _pendientes:
        raise servicios.PeticionInvalida("La autorización venció o la API se reinició: pulsa «Autorizar» otra vez.")
    verificador, redirect = _pendientes.pop(state)
    try:
        r = g.canjear_codigo(codigo, redirect, verificador)
        cuenta = g.correo_de(r["access_token"])
    except g.GoogleError as exc:
        raise servicios.PeticionInvalida(str(exc)) from exc
    cambios = {"GOOGLE_OAUTH_REFRESH_TOKEN": r["refresh_token"], "GOOGLE_OAUTH_SCOPES": r.get("scope", "")}
    if cuenta:
        cambios["USER_GOOGLE_EMAIL"] = cuenta
    _poner(cambios)
    return leer()


def desconectar() -> e.GoogleMcp:
    token = _env("GOOGLE_OAUTH_REFRESH_TOKEN")
    if token:
        try:
            g.revocar(token)
        except g.GoogleError:
            pass   # se quita igual del .env; el acceso también se puede quitar en myaccount.google.com/permissions
    _poner({"GOOGLE_OAUTH_REFRESH_TOKEN": "", "GOOGLE_OAUTH_SCOPES": ""})
    return leer()


def probar(servicio: str, p: e.PedidoPruebaGoogle) -> e.PruebaNotificacion:
    if servicio not in g.SERVICIOS:
        raise servicios.NoEncontrado(f"Servicio de Google desconocido: {servicio}")
    destinatario = p.destinatario.strip()
    if g.SERVICIOS[servicio].envia and destinatario and not (_CORREO.match(destinatario) or destinatario.startswith("spaces/")):
        raise servicios.PeticionInvalida("Escribe un correo válido (o un espacio spaces/… en Google Chat).")
    try:
        return e.PruebaNotificacion(ok=True, detalle=g.probar(servicio, destinatario, p.texto.strip()[:servidor.MAX_TEXTO]))
    except g.GoogleError as exc:
        return e.PruebaNotificacion(ok=False, detalle=str(exc))
