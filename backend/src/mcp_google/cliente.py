"""Cliente de Google Workspace con OAuth de usuario: Gmail, Chat (mensajes directos a contactos), Calendar, Drive, Docs,
Sheets, Slides, Forms, Tasks y Contactos. Solo biblioteca estándar.

Configuración (solo en el .env; el secreto y el refresh token nunca salen hacia el navegador):
  GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET   cliente OAuth del proyecto de Google Cloud
  GOOGLE_OAUTH_REDIRECT_URI                             opcional; por defecto la página /configuracion/mcp de la web
  USER_GOOGLE_EMAIL                                     cuenta autorizada
  GOOGLE_MCP_SERVICIOS                                  servicios activos, separados por coma (gmail,chat,…)
  GOOGLE_MCP_SOLO_LECTURA                               true = el MCP no envía ni modifica nada
  GOOGLE_MCP_NIVEL                                      core | extended | complete (para workspace-mcp)
  GOOGLE_OAUTH_REFRESH_TOKEN / GOOGLE_OAUTH_SCOPES      los escribe la web al canjear el código de autorización
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr

URL_AUTORIZACION = "https://accounts.google.com/o/oauth2/v2/auth"
URL_TOKEN = "https://oauth2.googleapis.com/token"
URL_REVOCAR = "https://oauth2.googleapis.com/revoke"
URL_USUARIO = "https://openidconnect.googleapis.com/v1/userinfo"
G = "https://www.googleapis.com/auth/"
BASICOS = ["openid", "email"]


@dataclass(frozen=True)
class Servicio:
    id: str
    nombre: str
    descripcion: str
    scopes: tuple[str, ...]
    envia: bool = False          # su prueba publica o envía algo (la web pide confirmación y destinatario)


SERVICIOS: dict[str, Servicio] = {s.id: s for s in [
    Servicio("gmail", "Gmail", "Enviar correos desde tu cuenta y buscar en la bandeja.", (G + "gmail.send", G + "gmail.readonly"), envia=True),
    Servicio("chat", "Google Chat", "Mensajes directos a tus contactos (no al webhook) y a espacios donde estás.",
             (G + "chat.messages.create", G + "chat.spaces.create", G + "chat.spaces.readonly"), envia=True),
    Servicio("contacts", "Contactos", "Buscar contactos por nombre para saber su correo.", (G + "contacts.readonly", G + "directory.readonly")),
    Servicio("calendar", "Calendar", "Leer y crear eventos.", (G + "calendar.readonly", G + "calendar.events")),
    Servicio("drive", "Drive", "Buscar y leer archivos.", (G + "drive.readonly",)),
    Servicio("docs", "Docs", "Leer y editar documentos.", (G + "documents", G + "drive.metadata.readonly")),
    Servicio("sheets", "Sheets", "Leer y editar hojas de cálculo.", (G + "spreadsheets", G + "drive.metadata.readonly")),
    Servicio("slides", "Slides", "Leer y editar presentaciones.", (G + "presentations", G + "drive.metadata.readonly")),
    Servicio("forms", "Forms", "Leer formularios y respuestas.", (G + "forms.body.readonly", G + "forms.responses.readonly", G + "drive.metadata.readonly")),
    Servicio("tasks", "Tasks", "Leer y crear tareas.", (G + "tasks",)),
]}
MIME_DRIVE = {"docs": "application/vnd.google-apps.document", "sheets": "application/vnd.google-apps.spreadsheet",
              "slides": "application/vnd.google-apps.presentation", "forms": "application/vnd.google-apps.form"}


class GoogleError(RuntimeError):
    """Fallo de configuración o respuesta de error de Google (mensaje apto para mostrar, sin secretos)."""


def _env(variable: str) -> str:
    return os.getenv(variable, "").strip()


def servicios_activos() -> list[str]:
    activos = [s.strip() for s in _env("GOOGLE_MCP_SERVICIOS").split(",") if s.strip() in SERVICIOS]
    return activos or ["gmail", "chat", "contacts"]


def solo_lectura() -> bool:
    return _env("GOOGLE_MCP_SOLO_LECTURA").lower() in {"1", "true", "si", "sí"}


def scopes_de(servicios: list[str]) -> list[str]:
    vistos = dict.fromkeys(BASICOS + [sc for s in servicios for sc in SERVICIOS[s].scopes])
    return list(vistos)


def scopes_concedidos() -> set[str]:
    return set(_env("GOOGLE_OAUTH_SCOPES").split())


def falta_consentimiento(servicio: str) -> bool:
    """El token no tiene todos los permisos del servicio (hay que volver a autorizar)."""
    return not set(SERVICIOS[servicio].scopes) <= scopes_concedidos()


# ---------------------------------------------------------------- HTTP

def _http(metodo: str, url: str, *, datos: dict | None = None, form: dict | None = None, token: str | None = None) -> dict:
    cuerpo, cabeceras = None, {}
    if form is not None:
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


def enviar_chat(token: str, para: str, texto: str) -> str:
    """`para` es el correo de un contacto (mensaje directo) o un espacio `spaces/…`."""
    espacio = para if para.startswith("spaces/") else espacio_directo(token, para)
    return _http("POST", f"{CHAT}/{espacio}/messages", datos={"text": texto}, token=token).get("name", "")


def espacios_chat(token: str, cantidad: int = 20) -> list[dict]:
    r = _http("GET", f"{CHAT}/spaces?pageSize={cantidad}", token=token)
    return [{"espacio": s["name"], "nombre": s.get("displayName") or ("Mensaje directo" if s.get("spaceType") == "DIRECT_MESSAGE" else s["name"]),
             "tipo": s.get("spaceType", "")} for s in r.get("spaces", [])]


# ---------------------------------------------------------------- Contactos, Calendar, Drive, Tasks

def buscar_contactos(token: str, consulta: str, cantidad: int = 10) -> list[dict]:
    """Busca en tus contactos y, si no hay, en el directorio de la organización."""
    campos = "names,emailAddresses"
    q = urllib.parse.urlencode({"query": consulta, "readMask": campos, "pageSize": cantidad})
    personas = [x.get("person", {}) for x in _http("GET", f"https://people.googleapis.com/v1/people:searchContacts?{q}", token=token).get("results", [])]
    if not personas:
        q = urllib.parse.urlencode({"query": consulta, "readMask": campos, "pageSize": cantidad, "sources": "DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE"})
        try:
            personas = _http("GET", f"https://people.googleapis.com/v1/people:searchDirectoryPeople?{q}", token=token).get("people", [])
        except GoogleError:
            personas = []   # cuentas personales no tienen directorio
    return [{"nombre": (p.get("names") or [{}])[0].get("displayName", ""), "correo": (p.get("emailAddresses") or [{}])[0].get("value", "")} for p in personas]


def proximos_eventos(token: str, cantidad: int = 5) -> list[dict]:
    q = urllib.parse.urlencode({"maxResults": cantidad, "singleEvents": "true", "orderBy": "startTime",
                                "timeMin": datetime.now(timezone.utc).isoformat()})
    r = _http("GET", f"https://www.googleapis.com/calendar/v3/calendars/primary/events?{q}", token=token)
    return [{"titulo": e.get("summary", "(sin título)"), "inicio": (e.get("start") or {}).get("dateTime") or (e.get("start") or {}).get("date")}
            for e in r.get("items", [])]


def buscar_archivos(token: str, consulta: str = "", tipo: str | None = None, cantidad: int = 10) -> list[dict]:
    filtros = ["trashed = false"]
    if consulta:
        filtros.append("name contains '" + consulta.replace("\\", "\\\\").replace("'", "\\'") + "'")
    if tipo in MIME_DRIVE:
        filtros.append(f"mimeType = '{MIME_DRIVE[tipo]}'")
    q = urllib.parse.urlencode({"q": " and ".join(filtros), "pageSize": cantidad, "fields": "files(id,name,mimeType,webViewLink)", "orderBy": "modifiedTime desc"})
    return [{"nombre": f["name"], "enlace": f.get("webViewLink", ""), "tipo": f.get("mimeType", "")}
            for f in _http("GET", f"https://www.googleapis.com/drive/v3/files?{q}", token=token).get("files", [])]


def listas_tareas(token: str) -> list[dict]:
    return [{"id": x["id"], "titulo": x.get("title", "")} for x in _http("GET", "https://tasks.googleapis.com/tasks/v1/users/@me/lists", token=token).get("items", [])]


# ---------------------------------------------------------------- pruebas (una por servicio)

def probar(servicio: str, destinatario: str = "", texto: str = "") -> str:
    """Ejecuta la prueba del servicio y devuelve un resumen. Gmail y Chat envían de verdad a `destinatario`."""
    if servicio not in SERVICIOS:
        raise GoogleError(f"Servicio desconocido: {servicio}")
    token = token_de_acceso()
    texto = texto or "Prueba del MCP de Google Workspace desde la web de reportes automatizados."
    if servicio == "gmail":
        if not destinatario:
            raise GoogleError("Indica el correo que recibirá la prueba.")
        enviar_correo(token, destinatario, "Prueba del MCP de Google · Reportes automatizados", texto)
        return f"Correo enviado por Gmail a {destinatario}"
    if servicio == "chat":
        if not destinatario:
            raise GoogleError("Indica el correo del contacto (o el espacio spaces/…) que recibirá el mensaje.")
        enviar_chat(token, destinatario, texto)
        return f"Mensaje de Google Chat enviado a {destinatario}"
    if servicio == "contacts":
        encontrados = buscar_contactos(token, destinatario or "a", 5)
        return f"{len(encontrados)} contacto(s) encontrados" + (f": {', '.join(c['nombre'] or c['correo'] for c in encontrados)}" if encontrados else "")
    if servicio == "calendar":
        eventos = proximos_eventos(token)
        return f"{len(eventos)} evento(s) próximos" + (f"; el siguiente: {eventos[0]['titulo']}" if eventos else "")
    if servicio == "tasks":
        listas = listas_tareas(token)
        return f"{len(listas)} lista(s) de tareas" + (f": {', '.join(x['titulo'] for x in listas)}" if listas else "")
    archivos = buscar_archivos(token, tipo=None if servicio == "drive" else servicio, cantidad=5)
    return f"{len(archivos)} archivo(s) visibles" + (f": {', '.join(a['nombre'] for a in archivos)}" if archivos else "")
