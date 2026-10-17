"""Contratos del módulo de sistema (sesión, cuenta, ajustes y servidores). Solo forma de los datos: sin lógica."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from modulos.reportes.aplicacion.dto import Corte


class Servidor(BaseModel):
    """Una de las 3 conexiones, sin secretos: solo si hay credenciales configuradas."""

    nombre: str
    servidor: str
    autenticacion: Literal["Windows", "SQL"]
    credenciales_en_env: bool
    descripcion: str
    bases: list[str]


class PruebaConexion(BaseModel):
    nombre: str
    ok: bool
    detalle: str
    milisegundos: int


class PedidoSesion(BaseModel):
    usuario: str = Field(min_length=1, max_length=256)
    clave: str = Field(min_length=1, max_length=256)


class PedidoCuenta(BaseModel):
    """Cambio de usuario y/o contraseña de la web. Siempre exige la contraseña actual."""

    clave_actual: str = Field(min_length=1, max_length=256)
    usuario: str | None = Field(default=None, max_length=64)
    clave_nueva: str | None = Field(default=None, max_length=256)


class Sesion(BaseModel):
    usuario: str


class Perfil(BaseModel):
    """Quién ejecuta la API y cómo está configurado el envío de correo (sin contraseñas ni webhook)."""

    usuario: str
    equipo: str
    correo_prueba: str
    cuenta_envio: str | None
    clave_envio_configurada: bool
    webhook_configurado: bool
    destinatarios: int | None     # None si no se pudo leer la lista


class ConfiguracionGeneral(BaseModel):
    """Lo que la API leyó del .env al arrancar (sin secretos)."""

    corte_mensual: Corte
    corte_diario: Corte
    dir_inputs: str
    dir_outputs: str
    driver_odbc: str
    pendientes_reinicio: list[str] = []   # ajustes guardados en el .env que la API aplica al reiniciar


class PedidoConfiguracion(BaseModel):
    """Solo se cambian los campos enviados; texto vacío = quitar la variable del .env."""

    corte_mensual: str | None = None
    corte_diario: str | None = None
    dir_inputs: str | None = None
    dir_outputs: str | None = None
    driver_odbc: str | None = None
