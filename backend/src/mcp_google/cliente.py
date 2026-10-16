"""Google Workspace con OAuth de usuario: servidores MCP oficiales de Google (Drive, Gmail, Docs, Sheets, Slides, Chat)
y envío directo por Gmail y Google Chat (el MCP oficial de Gmail solo crea borradores). Solo biblioteca estándar.

Configuración (solo en el .env; el secreto y el refresh token nunca salen hacia el navegador):
  GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET   cliente OAuth del proyecto de Google Cloud (el mismo para todos)
  GOOGLE_OAUTH_REDIRECT_URI                             opcional; por defecto la página /configuracion/mcp de la web
  USER_GOOGLE_EMAIL                                     cuenta autorizada
  GOOGLE_MCP_SERVICIOS                                  servidores activos, separados por coma (drive,gmail,…)
  GOOGLE_OAUTH_REFRESH_TOKEN / GOOGLE_OAUTH_SCOPES      los escribe la web al canjear el código de autorización
"""

from __future__ import annotations

import base64
import html
import json
import mimetypes
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

URL_AUTORIZACION = "https://accounts.google.com/o/oauth2/v2/auth"
URL_TOKEN = "https://oauth2.googleapis.com/token"
URL_REVOCAR = "https://oauth2.googleapis.com/revoke"
URL_USUARIO = "https://openidconnect.googleapis.com/v1/userinfo"
G = "https://www.googleapis.com/auth/"
BASICOS = ["openid", "email"]
DRIVE = (G + "drive.readonly", G + "drive.file")
PROTOCOLO_MCP = "2025-06-18"


@dataclass(frozen=True)
class Servicio:
    id: str
    nombre: str
    scopes: tuple[str, ...]
    envia: bool = False          # además del MCP, la web envía directo por la API (correo o mensaje)

    @property
    def url(self) -> str:
        return f"https://{self.id}mcp.googleapis.com/mcp/v1"


SERVICIOS: dict[str, Servicio] = {s.id: s for s in [
    Servicio("drive", "Drive", DRIVE),
    Servicio("gmail", "Gmail", (G + "gmail.readonly", G + "gmail.compose", G + "gmail.send"), envia=True),
    Servicio("docs", "Docs", (*DRIVE, G + "documents.readonly", G + "documents")),
    Servicio("sheets", "Sheets", (*DRIVE, G + "spreadsheets.readonly", G + "spreadsheets")),
    Servicio("slides", "Slides", (*DRIVE, G + "presentations.readonly", G + "presentations")),
    Servicio("chat", "Chat", (G + "chat.spaces.readonly", G + "chat.spaces.create", G + "chat.memberships.readonly",
                              G + "chat.messages.readonly", G + "chat.messages.create", G + "chat.users.readstate.readonly"), envia=True),
]}


class GoogleError(RuntimeError):
    """Fallo de configuración o respuesta de error de Google (mensaje apto para mostrar, sin secretos)."""


def _env(variable: str) -> str:
    return os.getenv(variable, "").strip()


def servicios_activos() -> list[str]:
    activos = [s.strip() for s in _env("GOOGLE_MCP_SERVICIOS").split(",") if s.strip() in SERVICIOS]
    return activos or list(SERVICIOS)


def scopes_de(servicios: list[str]) -> list[str]:
    vistos = dict.fromkeys(BASICOS + [sc for s in servicios for sc in SERVICIOS[s].scopes])
    return list(vistos)


def scopes_concedidos() -> set[str]:
    return set(_env("GOOGLE_OAUTH_SCOPES").split())


def falta_consentimiento(servicio: str) -> bool:
    """El token no tiene todos los permisos del servicio (hay que volver a autorizar)."""
    return not set(SERVICIOS[servicio].scopes) <= scopes_concedidos()


# ---------------------------------------------------------------- HTTP

def _http(metodo: str, url: str, *, datos: dict | None = None, form: dict | None = None, crudo: tuple[bytes, str] | None = None, token: str | None = None) -> dict:
    cuerpo, cabeceras = None, {}
    if crudo is not None:
        cuerpo, cabeceras["Content-Type"] = crudo
    elif form is not None:
        cuerpo, cabeceras["Content-Type"] = urllib.parse.urlencode(form).encode(), "application/x-www-form-urlencoded"
    elif datos is not None:
        cuerpo, cabeceras["Content-Type"] = json.dumps(datos).encode(), "application/json; charset=UTF-8"
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=cuerpo, headers=cabeceras, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - solo URLs https fijas de Google
            texto = resp.read().decode("utf-8")
            return json.loads(texto) if texto.strip() else {}
    except urllib.error.HTTPError as exc:
        raise GoogleError(_mensaje_error(exc)) from exc
    except (urllib.error.URLError, OSError) as exc:
        raise GoogleError(f"No se pudo conectar con Google ({type(exc).__name__})") from exc


def _mensaje_error(exc: urllib.error.HTTPError) -> str:
    try:
        cuerpo = json.loads(exc.read().decode("utf-8"))
    except (ValueError, OSError):
        return f"Google respondió {exc.code}"
    err = cuerpo.get("error")
    if isinstance(err, dict):
        return f"Google respondió {exc.code}: {err.get('message') or err.get('status')}"
    return f"Google respondió {exc.code}: {cuerpo.get('error_description') or err}"


# ---------------------------------------------------------------- OAuth

def url_autorizacion(redirect_uri: str, state: str, desafio: str, servicios: list[str]) -> str:
    cliente = _env("GOOGLE_OAUTH_CLIENT_ID")
    if not cliente:
        raise GoogleError("Falta el Client ID de OAuth (GOOGLE_OAUTH_CLIENT_ID).")
    p = {"client_id": cliente, "redirect_uri": redirect_uri, "response_type": "code", "scope": " ".join(scopes_de(servicios)),
         "access_type": "offline", "prompt": "consent", "include_granted_scopes": "true", "state": state,
         "code_challenge": desafio, "code_challenge_method": "S256"}
    if _env("USER_GOOGLE_EMAIL"):
        p["login_hint"] = _env("USER_GOOGLE_EMAIL")
    return f"{URL_AUTORIZACION}?{urllib.parse.urlencode(p)}"


def canjear_codigo(codigo: str, redirect_uri: str, verificador: str) -> dict:
    """Devuelve {refresh_token, scope, access_token}. Google solo entrega refresh_token con prompt=consent."""
    cliente, secreto = _env("GOOGLE_OAUTH_CLIENT_ID"), _env("GOOGLE_OAUTH_CLIENT_SECRET")
    if not cliente or not secreto:
        raise GoogleError("Falta el Client ID o el Client secret de OAuth.")
    r = _http("POST", URL_TOKEN, form={"code": codigo, "client_id": cliente, "client_secret": secreto, "redirect_uri": redirect_uri,
                                       "grant_type": "authorization_code", "code_verifier": verificador})
    if not r.get("refresh_token"):
        raise GoogleError("Google no devolvió refresh token. Quita el acceso en myaccount.google.com/permissions y vuelve a autorizar.")
    return r


def token_de_acceso() -> str:
    cliente, secreto, refresco = _env("GOOGLE_OAUTH_CLIENT_ID"), _env("GOOGLE_OAUTH_CLIENT_SECRET"), _env("GOOGLE_OAUTH_REFRESH_TOKEN")
    if not refresco:
        raise GoogleError("La cuenta de Google no está autorizada: en MCP › Google Workspace pulsa «Autorizar» y pega el código.")
    if not cliente or not secreto:
        raise GoogleError("Falta el Client ID o el Client secret de OAuth.")
    r = _http("POST", URL_TOKEN, form={"client_id": cliente, "client_secret": secreto, "refresh_token": refresco, "grant_type": "refresh_token"})
    return r["access_token"]


def correo_de(token: str) -> str:
    return _http("GET", URL_USUARIO, token=token).get("email", "")


def revocar(token: str) -> None:
    _http("POST", URL_REVOCAR, form={"token": token})


# ---------------------------------------------------------------- Gmail

def enviar_correo(token: str, para: str, asunto: str, cuerpo: str) -> str:
    msg = EmailMessage()
    msg["To"], msg["Subject"] = para, asunto
    if _env("USER_GOOGLE_EMAIL"):
        msg["From"] = formataddr((_env("MAIL_FROM_NAME") or "Reportes automatizados", _env("USER_GOOGLE_EMAIL")))
    msg.set_content(cuerpo)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return _http("POST", "https://gmail.googleapis.com/gmail/v1/users/me/messages/send", datos={"raw": raw}, token=token).get("id", "")


def armar_correo(para: list[str], cc: list[str], asunto: str, texto: str, firma_html: str = "", adjuntos: list[Path] | None = None) -> EmailMessage:
    """Correo con el texto en HTML (+ la firma de Gmail, ya HTML) y los archivos adjuntos."""
    msg = EmailMessage()
    msg["To"], msg["Subject"] = ", ".join(para), asunto
    if cc:
        msg["Cc"] = ", ".join(cc)
    if _env("USER_GOOGLE_EMAIL"):
        msg["From"] = formataddr((_env("MAIL_FROM_NAME") or "Reportes automatizados", _env("USER_GOOGLE_EMAIL")))
    msg.set_content(texto)
    cuerpo = html.escape(texto).replace("\n", "<br>")
    msg.add_alternative(f"<div>{cuerpo}</div>" + (f"<br><div>{firma_html}</div>" if firma_html else ""), subtype="html")
    for ruta in adjuntos or []:
        tipo, _ = mimetypes.guess_type(ruta.name)
        principal, _, sub = (tipo or "application/octet-stream").partition("/")
        msg.add_attachment(ruta.read_bytes(), maintype=principal, subtype=sub, filename=ruta.name)
    return msg


def enviar_mensaje(token: str, msg: EmailMessage) -> str:
    """Envío por la carga `message/rfc822` de Gmail (hasta 35 MB; el JSON con `raw` admite mucho menos)."""
    url = "https://gmail.googleapis.com/upload/gmail/v1/users/me/messages/send?uploadType=media"
    return _http("POST", url, crudo=(msg.as_bytes(), "message/rfc822"), token=token).get("id", "")


def firma_gmail(token: str) -> str:
    """Firma HTML de la dirección de envío predeterminada de la cuenta (Configuración › Firma de Gmail)."""
    direcciones = _http("GET", "https://gmail.googleapis.com/gmail/v1/users/me/settings/sendAs", token=token).get("sendAs", [])
    elegida = next((d for d in direcciones if d.get("isDefault")), direcciones[0] if direcciones else {})
    return elegida.get("signature", "")


# ---------------------------------------------------------------- Chat

CHAT = "https://chat.googleapis.com/v1"


def espacio_directo(token: str, correo: str) -> str:
    """Espacio del mensaje directo con un contacto (por correo); lo crea si aún no hay conversación."""
    try:
        return _http("GET", f"{CHAT}/spaces:findDirectMessage?{urllib.parse.urlencode({'name': f'users/{correo}'})}", token=token)["name"]
    except GoogleError as exc:
        if "404" not in str(exc):
            raise
    datos = {"space": {"spaceType": "DIRECT_MESSAGE"}, "memberships": [{"member": {"name": f"users/{correo}", "type": "HUMAN"}}]}
    return _http("POST", f"{CHAT}/spaces:setup", datos=datos, token=token)["name"]


MAX_ADJUNTO = 200 * 1024 * 1024   # límite de Google Chat por archivo


def subir_adjunto(token: str, espacio: str, ruta: Path) -> dict:
    """Sube un archivo al espacio (media.upload, subida multipart) y devuelve su `attachmentDataRef`."""
    if ruta.stat().st_size > MAX_ADJUNTO:
        raise GoogleError(f"{ruta.name} supera los 200 MB que admite Google Chat.")
    limite = f"limite_{secrets.token_hex(8)}"
    tipo = mimetypes.guess_type(ruta.name)[0] or "application/octet-stream"
    cuerpo = (f"--{limite}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps({'filename': ruta.name})}\r\n"
              f"--{limite}\r\nContent-Type: {tipo}\r\n\r\n").encode() + ruta.read_bytes() + f"\r\n--{limite}--\r\n".encode()
    url = f"https://chat.googleapis.com/upload/v1/{espacio}/attachments:upload?uploadType=multipart"
    req = urllib.request.Request(url, data=cuerpo, method="POST", headers={
        "Authorization": f"Bearer {token}", "Content-Type": f"multipart/related; boundary={limite}"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310 - URL https fija de Google
            return json.loads(resp.read().decode("utf-8"))["attachmentDataRef"]
    except urllib.error.HTTPError as exc:
        raise GoogleError(_mensaje_error(exc)) from exc
    except (urllib.error.URLError, OSError, KeyError, ValueError) as exc:
        raise GoogleError(f"No se pudo subir {ruta.name} a Google Chat ({type(exc).__name__})") from exc


def enviar_chat(token: str, para: str, texto: str, adjuntos: list[Path] | None = None) -> str:
    """`para` es el correo de un contacto (mensaje directo) o un espacio `spaces/…`; `adjuntos` van en el mismo mensaje."""
    espacio = para if para.startswith("spaces/") else espacio_directo(token, para)
    mensaje: dict = {"text": texto}
    if adjuntos:
        mensaje["attachment"] = [{"attachmentDataRef": subir_adjunto(token, espacio, r)} for r in adjuntos]
    return _http("POST", f"{CHAT}/{espacio}/messages", datos=mensaje, token=token).get("name", "")


def espacios_chat(token: str, cantidad: int = 20) -> list[dict]:
    r = _http("GET", f"{CHAT}/spaces?pageSize={cantidad}", token=token)
    return [{"espacio": s["name"], "nombre": s.get("displayName") or ("Mensaje directo" if s.get("spaceType") == "DIRECT_MESSAGE" else s["name"]),
             "tipo": s.get("spaceType", "")} for s in r.get("spaces", [])]


# ---------------------------------------------------------------- cliente MCP (HTTP «streamable») para probar los servidores de Google

def _mcp(url: str, token: str, mensaje: dict, sesion: str | None = None) -> tuple[dict | None, str | None]:
    """Envía un mensaje JSON-RPC; devuelve (resultado, id de sesión). Acepta respuesta JSON o text/event-stream."""
    cabeceras = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                 "Authorization": f"Bearer {token}", "MCP-Protocol-Version": PROTOCOLO_MCP}
    if sesion:
        cabeceras["Mcp-Session-Id"] = sesion
    req = urllib.request.Request(url, data=json.dumps(mensaje).encode(), headers=cabeceras, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - solo URLs https fijas de Google
            sesion = resp.headers.get("Mcp-Session-Id") or sesion
            texto = resp.read().decode("utf-8")
            tipo = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        raise GoogleError(_mensaje_error(exc)) from exc
    except (urllib.error.URLError, OSError) as exc:
        raise GoogleError(f"No se pudo conectar con el MCP de Google ({type(exc).__name__})") from exc
    if "id" not in mensaje or not texto.strip():
        return None, sesion
    if "text/event-stream" in tipo:
        datos = [json.loads(l[5:]) for l in texto.splitlines() if l.startswith("data:") and l[5:].strip()]
        respuesta = next((d for d in datos if d.get("id") == mensaje["id"]), {})
    else:
        respuesta = json.loads(texto)
    if respuesta.get("error"):
        raise GoogleError(f"MCP: {respuesta['error'].get('message')}")
    return respuesta.get("result", {}), sesion


def _sesion_mcp(url: str, token: str) -> str | None:
    _, sesion = _mcp(url, token, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": PROTOCOLO_MCP, "capabilities": {}, "clientInfo": {"name": "reportes-automatizados", "version": "1.0"}}})
    _mcp(url, token, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sesion)
    return sesion


def mcp_herramientas(servicio: str) -> list[dict]:
    """Conecta con el MCP oficial del servicio y lista sus herramientas (nombre, descripción, esquema de argumentos)."""
    url, token = SERVICIOS[servicio].url, token_de_acceso()
    sesion, cursor, salida = _sesion_mcp(url, token), None, []
    for n in range(2, 12):
        res, _ = _mcp(url, token, {"jsonrpc": "2.0", "id": n, "method": "tools/list", "params": {"cursor": cursor} if cursor else {}}, sesion)
        salida += (res or {}).get("tools", [])
        cursor = (res or {}).get("nextCursor")
        if not cursor:
            break
    return salida


def mcp_ejecutar(servicio: str, herramienta: str, argumentos: dict) -> tuple[bool, str]:
    """Ejecuta una herramienta del MCP oficial; devuelve (ok, texto del resultado)."""
    url, token = SERVICIOS[servicio].url, token_de_acceso()
    sesion = _sesion_mcp(url, token)
    res, _ = _mcp(url, token, {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": herramienta, "arguments": argumentos}}, sesion)
    res = res or {}
    partes = [c.get("text", "") if c.get("type") == "text" else f"[{c.get('type')}]" for c in res.get("content", [])]
    if not partes and "structuredContent" in res:
        partes = [json.dumps(res["structuredContent"], ensure_ascii=False, indent=2)]
    return not res.get("isError"), "\n".join(partes) or "(sin contenido)"


# ---------------------------------------------------------------- envío directo (lo que el MCP oficial no hace)

def enviar(servicio: str, destinatario: str, texto: str) -> str:
    """Gmail: correo a `destinatario`. Chat: mensaje directo al contacto (correo) o a un espacio `spaces/…`."""
    if not destinatario:
        raise GoogleError("Indica el destinatario.")
    token = token_de_acceso()
    texto = texto or "Prueba desde la web de reportes automatizados."
    if servicio == "gmail":
        enviar_correo(token, destinatario, "Prueba · Reportes automatizados", texto)
        return f"Correo enviado por Gmail a {destinatario}"
    if servicio == "chat":
        enviar_chat(token, destinatario, texto)
        return f"Mensaje de Google Chat enviado a {destinatario}"
    raise GoogleError(f"{servicio} no envía mensajes.")
