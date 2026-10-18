"""Contratos del módulo de reportes (entrada y salida). Solo forma de los datos: sin lógica."""

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
    envia_chat: bool = False      # puede enviar el archivo generado por Google Chat (--chat)
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
    chat_destinatarios: list[str] = []   # a quién se envía por Google Chat (ENTREGA_CHAT_<REPORTE> del .env)
    correo_para: list[str] = []          # destinatarios del correo con los archivos (ENTREGA_CORREO_PARA_<REPORTE>)
    correo_cc: list[str] = []            # con copia (ENTREGA_CORREO_CC_<REPORTE>)


class Grupo(BaseModel):
    id: str
    nombre: str
    frecuencia: Literal["diaria", "mensual"]
    propio: bool                  # creado desde la web (los del legado no se tocan)
    reportes: int
    etiquetas: list[Etiqueta] = []


class PedidoGrupo(BaseModel):
    nombre: str
    etiquetas: list[str] = []


class PedidoReporteNuevo(BaseModel):
    nombre: str                   # comando: minúsculas y guiones
    grupo: str                    # id de un grupo existente (diarias, piero, erick o uno creado desde la web)
    orden: str                    # número del legado: "07" o "07.1"
    base: str | None = None       # None = la del `use <base>` del T-SQL; de ella sale el servidor
    descripcion: str
    frecuencia: Literal["diaria", "mensual"] | None = None   # None = la del grupo; los grupos del legado no admiten otra
    sql: str = ""                 # T-SQL con tokens de fecha; vacío = plantilla, se completa en la pestaña Script


class ReporteCreado(BaseModel):
    nombre: str
    ruta: str                     # relativa al repo
    tablas_nuevas: list[str]      # tablas que no estaban registradas: completar su columna de fecha en dominio/tablas.py


class PedidoScript(BaseModel):
    codigo: str


class PedidoChat(BaseModel):
    destinatarios: str            # correos separados por coma; vacío = no enviar a nadie


class PedidoDestinosCorreo(BaseModel):
    para: str = ""                # correos separados por coma; vacío = sin destinatarios guardados
    cc: str = ""


class PedidoEnvioArchivos(BaseModel):
    para: list[str]
    cc: list[str] = []
    asunto: str
    mensaje: str = ""
    archivos: list[str]
    con_firma: bool = True
    prueba: bool = False          # solo a CORREO_PRUEBA, sin copia


class FirmaGmail(BaseModel):
    html: str                     # vacío si la cuenta no tiene firma


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


class ProblemaValidacion(BaseModel):
    """Una causa de error compartida por varias tablas (p. ej. sin red a un servidor), para no repetirla en cada fila."""

    causa: str
    tablas: int
    solucion: str


class VerificacionGrupo(BaseModel):
    """Validación masiva: todas las tablas de los reportes mensuales de un responsable, cada una verificada una sola vez."""

    grupo: str
    titulo: str
    corte: date
    listo: bool
    reportes: list[ResumenValidacion]
    tablas: list[TablaValidada]
    problemas: list[ProblemaValidacion]   # errores que no son de la tabla sino de la conexión, agrupados por causa
    solicitud: str | None         # un solo mensaje para Producción si falta alguna


class EntradaValidacion(BaseModel):
    """Una verificación del grupo guardada en el historial (resumen por reporte; el detalle por tabla no se conserva)."""

    id: str
    grupo: str
    ejecutada: str                # cuándo se verificó (ISO)
    corte: date
    listo: bool
    reportes: list[ResumenValidacion]
    tablas_total: int
    tablas_ok: int
    tablas_pendientes: int
    tablas_dudosas: int
    solicitud: str | None = None  # mensaje para Producción de esa verificación
    chat_enviado: str | None = None
    chat_a: list[str] = Field(default_factory=list)


class DestinosChat(BaseModel):
    destinatarios: list[str]


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
    chat: bool = False                                     # enviar el archivo generado por Google Chat (reportes con envia_chat)
    fase: Literal["operaciones", "provisiones", "generar"] | None = None  # solo cmg-mora: una etapa del flujo por fases


class Ejecucion(BaseModel):
    id: str
    reporte: str
    argumentos: list[str]
    estado: Literal["en_cola", "ejecutando", "ok", "error", "configuracion", "tablas_desactualizadas"]
    codigo: int | None
    inicio: str
    fin: str | None
    archivos: list[str] = Field(default_factory=list)  # nombres dentro de la carpeta del reporte


class PedidoEliminarEjecuciones(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=500)


class EjecucionesEliminadas(BaseModel):
    eliminadas: int


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


class EstadoEnvio(BaseModel):
    corte: date
    prueba: str | None            # fecha-hora de la prueba enviada
    todos: str | None             # fecha-hora del envío a la lista
    excel: str | None


class PedidoEtiqueta(BaseModel):
    nombre: str
    color: str = "#6b7280"        # #rrggbb, el que elige la persona


class Etiqueta(PedidoEtiqueta):
    id: str


class CatalogoEtiquetas(BaseModel):
    """Lo que se guarda en disco: las etiquetas y cuáles lleva cada grupo."""

    etiquetas: list[Etiqueta] = []
    grupos: dict[str, list[str]] = {}


class PedidoEtiquetasGrupo(BaseModel):
    etiquetas: list[str]


class Script(BaseModel):
    ruta: str     # relativa al repo, para abrirla en el editor
    codigo: str
