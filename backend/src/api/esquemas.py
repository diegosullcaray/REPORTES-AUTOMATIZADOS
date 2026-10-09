"""Contratos HTTP (entrada y salida) de la API. Solo forma de los datos: sin lógica."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ReporteResumen(BaseModel):
    nombre: str
    grupo: str
    orden: str
    frecuencia: str
    servidores: list[str]
    descripcion: str
    carpeta: str
    es_lote: bool                 # usa el ejecutor común (verificación de tablas, --forzar…)
    escribe_en_bd: bool           # exige confirmar escritura
    vacio_valido: bool
    envia_correo: bool            # flujo prueba -> conforme -> todos
    avisos: list[str]


class Corte(BaseModel):
    fecha: date | None
    origen: str                   # de dónde salió (.env, día anterior…) o por qué falta


class TablaReporte(BaseModel):
    nombre: str
    servidor: str
    tipo: str
    columna_fecha: str | None
    confianza: str
    verificable: bool
    condicion: str | None


class ReporteDetalle(ReporteResumen):
    corte: Corte
    tablas: list[TablaReporte]


class PedidoCorte(BaseModel):
    fecha_corte: date | None = None


class ResultadoTabla(BaseModel):
    nombre: str
    servidor: str
    estado: Literal["OK", "DESACTUALIZADA", "NO EXISTE", "ERROR", "SIN CONTROL"]
    ultima_fecha: date | None
    detalle: str


class Verificacion(BaseModel):
    corte: date
    listo: bool                   # todas las verificables al día: se puede ejecutar sin --forzar
    resultados: list[ResultadoTabla]
    solicitud: str | None         # mensaje para Producción si falta alguna


class ResumenValidacion(BaseModel):
    nombre: str
    orden: str
    tablas: int
    pendientes: int               # desactualizadas o inexistentes
    dudosas: int                  # no se pudieron verificar
    listo: bool


class TablaValidada(ResultadoTabla):
    reportes: list[str]           # reportes del grupo que usan esta tabla


class VerificacionGrupo(BaseModel):
    """Validación masiva: todas las tablas de los reportes mensuales de un responsable, cada una verificada una sola vez."""

    grupo: str
    titulo: str
    corte: date
    listo: bool
    reportes: list[ResumenValidacion]
    tablas: list[TablaValidada]
    solicitud: str | None         # un solo mensaje para Producción si falta alguna


class Solicitud(BaseModel):
    archivo: str
    texto: str


class PedidoEjecucion(BaseModel):
    reporte: str
    fecha_corte: date | None = None
    forzar: bool = False
    confirmar_escritura: bool = False
    correo: Literal["no", "prueba", "todos"] = "prueba"   # solo reportes con envío de correo
    conforme: bool = False                                 # obligatorio con correo = todos


class Ejecucion(BaseModel):
    id: str
    reporte: str
    argumentos: list[str]
    estado: Literal["en_cola", "ejecutando", "ok", "error", "configuracion", "tablas_desactualizadas"]
    codigo: int | None
    inicio: str
    fin: str | None
    archivos: list[str] = Field(default_factory=list)  # nombres dentro de la carpeta del reporte


class EjecucionDetalle(Ejecucion):
    log: str


class Archivo(BaseModel):
    nombre: str
    tipo: Literal["excel", "imagen", "texto", "otro"]
    tamano: int
    modificado: str


class HojaPrevia(BaseModel):
    nombre: str
    columnas: list[str]
    filas: list[list[str | int | float | None]]
    total_filas: int              # filas reales de la hoja (la vista previa trae solo las primeras)


class VistaPrevia(BaseModel):
    archivo: str
    tipo: Literal["excel", "texto"]
    hojas: list[HojaPrevia] = Field(default_factory=list)
    texto: str | None = None


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


class Notificaciones(BaseModel):
    """Correo (SMTP) y Google Chat. La clave y el webhook nunca se devuelven: solo si están configurados."""

    smtp_host: str
    smtp_port: int
    smtp_user: str
    remitente_nombre: str
    correo_prueba: str
    clave_configurada: bool
    webhook_configurado: bool
    destinatarios: int | None


class PedidoNotificaciones(BaseModel):
    """Solo se cambian los campos enviados; texto vacío = quitar la variable del .env."""

    smtp_host: str | None = None
    smtp_port: str | None = None
    smtp_user: str | None = None
    smtp_clave: str | None = None
    remitente_nombre: str | None = None
    correo_prueba: str | None = None
    webhook: str | None = None


class PruebaNotificacion(BaseModel):
    ok: bool
    detalle: str


class PedidoConfiguracion(BaseModel):
    """Solo se cambian los campos enviados; texto vacío = quitar la variable del .env."""

    corte_mensual: str | None = None
    corte_diario: str | None = None
    dir_inputs: str | None = None
    dir_outputs: str | None = None
    driver_odbc: str | None = None


class EstadoEnvio(BaseModel):
    corte: date
    prueba: str | None            # fecha-hora de la prueba enviada
    todos: str | None             # fecha-hora del envío a la lista
    excel: str | None
