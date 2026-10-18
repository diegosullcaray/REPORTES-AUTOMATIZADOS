"""Contratos del módulo de integraciones (Google Workspace y MCP). Solo forma de los datos: sin lógica."""

from __future__ import annotations

from pydantic import BaseModel


class HerramientaMcp(BaseModel):
    nombre: str
    descripcion: str


class ServicioGoogle(BaseModel):
    id: str
    nombre: str
    url: str                        # servidor MCP oficial de Google
    activo: bool
    envia: bool                     # además, envío directo por la API (Gmail, Chat)
    scopes: list[str]
    falta_consentimiento: bool      # activo, pero el token no tiene sus permisos: volver a autorizar


class GoogleMcp(BaseModel):
    """MCP de Google Workspace. Sin secretos: el Client secret y el token solo se informan como configurados o no."""

    client_id: str
    secreto_configurado: bool
    redirect_uri: str               # vacío = la web usa su propia página /configuracion/mcp
    cuenta: str
    autorizado: bool
    correo_prueba: str
    servicios: list[ServicioGoogle]
    herramientas_envio: list[HerramientaMcp]   # las del servidor propio (envío)
    python: str
    configuracion: dict             # bloque mcpServers para el cliente MCP (sin el Client secret)


class PedidoGoogleMcp(BaseModel):
    """Solo se cambian los campos enviados; texto vacío = quitar la variable del .env."""

    client_id: str | None = None
    client_secret: str | None = None
    redirect_uri: str | None = None
    cuenta: str | None = None
    servicios: list[str] | None = None


class HerramientaRemota(BaseModel):
    nombre: str
    descripcion: str
    esquema: dict                   # inputSchema de la herramienta


class PruebaMcp(BaseModel):
    ok: bool
    detalle: str
    herramientas: list[HerramientaRemota] = []


class PedidoEjecutarMcp(BaseModel):
    herramienta: str
    argumentos: dict = {}


class PedidoAutorizacion(BaseModel):
    redirect_uri: str = ""


class Autorizacion(BaseModel):
    url: str
    redirect_uri: str


class PedidoCodigo(BaseModel):
    codigo: str
    state: str | None = None


class PedidoPruebaGoogle(BaseModel):
    destinatario: str = ""
    texto: str = ""


class ConfigIA(BaseModel):
    """Una conexión con un proveedor de IA. Sin la API key: solo se informa si está configurada."""

    id: str
    nombre: str
    api_url: str
    modelo: str
    activo: bool
    proveedor: str                  # openai | anthropic | gemini | mistral | ollama | custom…
    clave_configurada: bool


class PedidoIA(BaseModel):
    nombre: str
    api_url: str
    api_key: str = ""               # Ollama local no la exige
    modelo: str
    activo: bool = True


class PedidoIAActualizar(BaseModel):
    """Solo se cambian los campos enviados; `api_key` vacía o ausente conserva la guardada."""

    nombre: str | None = None
    api_url: str | None = None
    api_key: str | None = None
    modelo: str | None = None
    activo: bool | None = None


class PedidoModelos(BaseModel):
    api_url: str
    api_key: str = ""               # vacía + `id`: usa la guardada (solo si la URL no cambió)
    id: str | None = None


class ModelosIA(BaseModel):
    proveedor: str
    modelos: list[str]
