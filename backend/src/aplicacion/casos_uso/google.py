"""MCP de Google Workspace desde la web: cliente OAuth, autorización con código, servidores MCP oficiales y pruebas.

Todo se guarda en el .env. El Client secret y el refresh token son de solo escritura: nunca vuelven al navegador.
Autorizar: la web pide la URL de Google, la persona da su consentimiento y Google redirige con `?code=…`; la web
canjea ese código (o la persona lo pega a mano, solo o con la URL completa).
"""

from __future__ import annotations

import base64
import hashlib
import re
import secrets
import sys
from urllib.parse import parse_qs, urlparse

from aplicacion import dto as e
from aplicacion.errores import NoEncontrado, PeticionInvalida
from aplicacion.puertos import puertos
from dominio.errores import ErrorIntegracion

from . import herramientas_envio

SECRETO = "<GOOGLE_OAUTH_CLIENT_SECRET del .env>"   # el JSON que ve el navegador nunca lleva el secreto
VARIABLES = {"client_id": "GOOGLE_OAUTH_CLIENT_ID", "client_secret": "GOOGLE_OAUTH_CLIENT_SECRET",
             "redirect_uri": "GOOGLE_OAUTH_REDIRECT_URI", "cuenta": "USER_GOOGLE_EMAIL"}
_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_pendientes: dict[str, tuple[str, str]] = {}   # state -> (code_verifier, redirect_uri), solo en memoria
_ultimo: list[str] = []                         # último state, para cuando se pega solo el código


def _g():
    return puertos().google


def _env(variable: str) -> str:
    return puertos().entorno.leer(variable).strip()


def _poner(cambios: dict[str, str]) -> None:
    puertos().entorno.guardar(cambios)


def leer() -> e.GoogleMcp:
    activos = _g().servicios_activos()
    autorizado = bool(_env("GOOGLE_OAUTH_REFRESH_TOKEN"))
    oauth = {"clientId": _env("GOOGLE_OAUTH_CLIENT_ID") or "<client-id>", "clientSecret": SECRETO}
    servidores: dict = {f"gws-{s}": {"serverUrl": _g().SERVICIOS[s].url, "oauth": oauth} for s in activos}
    if herramientas_envio.herramientas():
        servidores["google-envio"] = {"command": "python", "args": [str(puertos().entorno.raiz() / "src" / "interfaces" / "mcp" / "servidor.py")]}
    return e.GoogleMcp(
        client_id=_env("GOOGLE_OAUTH_CLIENT_ID"), secreto_configurado=bool(_env("GOOGLE_OAUTH_CLIENT_SECRET")),
        redirect_uri=_env("GOOGLE_OAUTH_REDIRECT_URI"), cuenta=_env("USER_GOOGLE_EMAIL"), autorizado=autorizado,
        correo_prueba=_env("CORREO_PRUEBA"),
        servicios=[e.ServicioGoogle(id=s.id, nombre=s.nombre, url=s.url, activo=s.id in activos, envia=s.envia, scopes=list(s.scopes),
                                    falta_consentimiento=autorizado and s.id in activos and _g().falta_consentimiento(s.id))
                   for s in _g().SERVICIOS.values()],
        herramientas_envio=[e.HerramientaMcp(nombre=h["name"], descripcion=h["description"]) for h in herramientas_envio.herramientas()],
        python=sys.executable, configuracion={"mcpServers": servidores},
    )


def _validar(campo: str, valor: str) -> str:
    if not valor:
        return ""
    if any(c in valor for c in "\r\n#\"' "):
        raise PeticionInvalida(f"{VARIABLES[campo]}: no admite espacios, saltos de línea, # ni comillas.")
    if campo == "client_id" and not valor.endswith(".apps.googleusercontent.com"):
        raise PeticionInvalida("El Client ID termina en .apps.googleusercontent.com (cópialo de Google Cloud › Credenciales).")
    if campo == "redirect_uri" and urlparse(valor).scheme not in {"http", "https"}:
        raise PeticionInvalida("La URI de redirección debe empezar con http:// o https://.")
    if campo == "cuenta" and not _CORREO.match(valor):
        raise PeticionInvalida("USER_GOOGLE_EMAIL: escribe un correo válido.")
    return valor


def guardar(p: e.PedidoGoogleMcp) -> e.GoogleMcp:
    """Solo se cambian los campos enviados; texto vacío quita la variable."""
    cambios = {VARIABLES[c]: _validar(c, (getattr(p, c) or "").strip()) for c in p.model_fields_set if c in VARIABLES}
    if "servicios" in p.model_fields_set:
        desconocidos = [s for s in p.servicios or [] if s not in _g().SERVICIOS]
        if desconocidos or not p.servicios:
            raise PeticionInvalida(f"Servicios no válidos: {', '.join(desconocidos)}" if desconocidos else "Activa al menos un servicio.")
        cambios["GOOGLE_MCP_SERVICIOS"] = ",".join(s for s in _g().SERVICIOS if s in p.servicios)
    if not cambios:
        raise PeticionInvalida("No hay ningún ajuste que guardar.")
    _poner(cambios)
    return leer()


def autorizar(p: e.PedidoAutorizacion) -> e.Autorizacion:
    redirect = _env("GOOGLE_OAUTH_REDIRECT_URI") or p.redirect_uri.strip()
    if urlparse(redirect).scheme not in {"http", "https"}:
        raise PeticionInvalida("Falta una URI de redirección válida.")
    if not _env("GOOGLE_OAUTH_CLIENT_SECRET"):
        raise PeticionInvalida("Guarda primero el Client secret de OAuth.")
    verificador = secrets.token_urlsafe(64)
    desafio = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    try:
        url = _g().url_autorizacion(redirect, state, desafio, _g().servicios_activos())
    except ErrorIntegracion as exc:
        raise PeticionInvalida(str(exc)) from exc
    _pendientes[state] = (verificador, redirect)
    _ultimo[:] = [state]
    return e.Autorizacion(url=url, redirect_uri=redirect)


def _separar(texto: str, state: str | None) -> tuple[str, str | None]:
    """Acepta el código solo o la URL completa a la que llevó Google (…?code=…&state=…)."""
    if "code=" in texto:
        q = parse_qs(urlparse(texto).query or texto.split("?", 1)[-1])
        if q.get("error"):
            raise PeticionInvalida(f"Google devolvió un error: {q['error'][0]}")
        return q.get("code", [""])[0], (q.get("state") or [state])[0]
    return texto, state


def canjear(p: e.PedidoCodigo) -> e.GoogleMcp:
    codigo, state = _separar(p.codigo.strip(), p.state)
    if not codigo:
        raise PeticionInvalida("Pega el código de autorización (o la URL completa a la que te llevó Google).")
    state = state or (_ultimo[0] if _ultimo else None)
    if not state or state not in _pendientes:
        raise PeticionInvalida("La autorización venció o la API se reinició: pulsa «Autorizar» otra vez.")
    verificador, redirect = _pendientes.pop(state)
    try:
        r = _g().canjear_codigo(codigo, redirect, verificador)
        cuenta = _g().correo_de(r["access_token"])
    except ErrorIntegracion as exc:
        raise PeticionInvalida(str(exc)) from exc
    cambios = {"GOOGLE_OAUTH_REFRESH_TOKEN": r["refresh_token"], "GOOGLE_OAUTH_SCOPES": r.get("scope", "")}
    if cuenta:
        cambios["USER_GOOGLE_EMAIL"] = cuenta
    _poner(cambios)
    return leer()


def desconectar() -> e.GoogleMcp:
    token = _env("GOOGLE_OAUTH_REFRESH_TOKEN")
    if token:
        try:
            _g().revocar(token)
        except ErrorIntegracion:
            pass   # se quita igual del .env; el acceso también se puede quitar en myaccount.google.com/permissions
    _poner({"GOOGLE_OAUTH_REFRESH_TOKEN": "", "GOOGLE_OAUTH_SCOPES": ""})
    return leer()


def _servicio(servicio: str) -> None:
    if servicio not in _g().SERVICIOS:
        raise NoEncontrado(f"Servidor MCP de Google desconocido: {servicio}")


def herramientas(servicio: str) -> e.PruebaMcp:
    """Prueba del MCP oficial: conecta, inicia sesión MCP y lista sus herramientas."""
    _servicio(servicio)
    try:
        lista = _g().mcp_herramientas(servicio)
    except ErrorIntegracion as exc:
        return e.PruebaMcp(ok=False, detalle=str(exc))
    return e.PruebaMcp(ok=True, detalle=f"{len(lista)} herramienta(s) en {_g().SERVICIOS[servicio].url}",
                       herramientas=[e.HerramientaRemota(nombre=h.get("name", ""), descripcion=h.get("description", ""),
                                                         esquema=h.get("inputSchema") or {}) for h in lista])


def ejecutar(servicio: str, p: e.PedidoEjecutarMcp) -> e.PruebaNotificacion:
    _servicio(servicio)
    if not p.herramienta.strip():
        raise PeticionInvalida("Elige una herramienta.")
    try:
        ok, texto = _g().mcp_ejecutar(servicio, p.herramienta.strip(), p.argumentos)
    except ErrorIntegracion as exc:
        return e.PruebaNotificacion(ok=False, detalle=str(exc))
    return e.PruebaNotificacion(ok=ok, detalle=texto[:20000])


def enviar(servicio: str, p: e.PedidoPruebaGoogle) -> e.PruebaNotificacion:
    """Envío directo (servidor propio): Gmail a un correo, Chat a un contacto o espacio."""
    _servicio(servicio)
    if not _g().SERVICIOS[servicio].envia:
        raise PeticionInvalida(f"{_g().SERVICIOS[servicio].nombre} no envía mensajes.")
    destinatario = p.destinatario.strip()
    if not (_CORREO.match(destinatario) or (servicio == "chat" and destinatario.startswith("spaces/"))):
        raise PeticionInvalida("Escribe un correo válido" + (" o un espacio spaces/…" if servicio == "chat" else "") + ".")
    try:
        return e.PruebaNotificacion(ok=True, detalle=_g().enviar(servicio, destinatario, p.texto.strip()[:herramientas_envio.MAX_TEXTO]))
    except ErrorIntegracion as exc:
        return e.PruebaNotificacion(ok=False, detalle=str(exc))
