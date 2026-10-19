"""Contratos del módulo diccionario: lo que la web ve del diccionario de datos de los reportes MIS. Solo forma de los datos."""

from __future__ import annotations

from pydantic import BaseModel


class Hallazgo(BaseModel):
    nivel: str
    regla: str
    origen: str
    objeto: str
    detalle: str
    en_linea_base: bool


class BaseResumen(BaseModel):
    base: str
    procedimientos: int
    extraidos: int
    validados: int
    tablas: int


class OrigenCatalogo(BaseModel):
    """De dónde sale el catálogo de reportes: la base (en vivo) o, sin conexión, el diccionario.json."""

    fuente: str                   # mod_rep.rep.RREGREP01 | diccionario.json
    motivo: str | None            # por qué no se pudo leer la base
    nuevos: list[str]             # en la base y aún no en el diccionario
    retirados: list[str]          # en el diccionario y ya no en la base


class Resumen(BaseModel):
    reportes: int
    procedimientos: int
    extraidos: int
    validados: int
    tablas: int
    columnas: int
    errores: int
    avisos: int
    errores_nuevos: int
    catalogo: OrigenCatalogo
    bases: list[BaseResumen]


class ReporteFila(BaseModel):
    codigo: str
    descripcion: str
    procedimiento: str
    base: str
    estado: str                   # del procedimiento: validado | extraido | pendiente | sin procedimiento
    parametros: int
    tablas: int
    front: list[str]


class BaseFila(BaseModel):
    """Una base de datos del diccionario: la de los procedimientos del MIS o la que guarda las tablas."""

    base: str
    procedimientos: int
    validados: int
    reportes: int
    tablas_propias: int           # tablas que viven en esta base
    tablas_usadas: int            # tablas (de cualquier base) que usan sus procedimientos


class ProcedimientoFila(BaseModel):
    nombre: str
    estado: str                   # validado | extraido | pendiente | sin procedimiento
    reportes: list[str]
    parametros: int
    tablas: int


class TablaDeBase(BaseModel):
    nombre: str
    base: str                     # donde vive la tabla
    tipo: str | None
    existe: bool | None
    columnas: int
    propia: bool                  # vive en la base que se mira (si no, la usan sus procedimientos desde otra base)
    usada_por: int                # procedimientos de la base que se mira que la usan
    en_registro: bool


class BaseDetalle(BaseModel):
    base: str
    procedimientos: list[ProcedimientoFila]
    tablas: list[TablaDeBase]


class ParametroSP(BaseModel):
    nombre: str
    tipo: str | None
    por_defecto: str | None
    salida: bool


class ColumnaUso(BaseModel):
    nombre: str
    confianza: str | None
    es_fecha: bool


class TablaUso(BaseModel):
    nombre: str
    usos: list[str]
    columnas: list[ColumnaUso]


class Procedimiento(BaseModel):
    nombre: str
    base: str
    estado: str
    parametros: list[ParametroSP]
    resultados: list[list[str]]
    invoca: list[str]
    tablas: list[TablaUso]


class ReporteDetalle(ReporteFila):
    parametros_catalogo: list[str]
    procedimiento_detalle: Procedimiento | None
    hallazgos: list[Hallazgo]


class RegistroTabla(BaseModel):
    """Lo que REPORTES-AUTOMATIZADOS sabe de la misma tabla (dominio/tablas.py)."""

    tipo: str
    col_fecha: str | None
    confianza: str
    reportes: list[str]


class TablaFila(BaseModel):
    nombre: str
    base: str
    tipo: str | None
    existe: bool | None
    columnas: int
    procedimientos: int
    en_registro: bool


class Columna(BaseModel):
    nombre: str
    tipo: str | None
    acepta_nulos: bool | None
    confianza: str | None
    es_fecha: bool
    procedimientos: list[str]


class TablaDetalle(TablaFila):
    descripcion: str | None
    ficha: str | None
    columnas_detalle: list[Columna]
    reportes_mis: list[str]
    registro: RegistroTabla | None


class SugerenciaFecha(BaseModel):
    tabla: str
    actual: str | None
    confianza: str
    motivo: str
    candidatas: list[str]


class TablaDisponible(BaseModel):
    """Una tabla que los reportes del MIS ya usan y que aún no está en el registro de REPORTES-AUTOMATIZADOS."""

    nombre: str
    reportes_mis: int
    columnas: int
    fechas: list[str]


class Potencial(BaseModel):
    """Lo que el diccionario le aporta a los reportes propios."""

    tablas_registradas: int
    en_diccionario: int
    faltan_en_diccionario: list[str]
    fechas: list[SugerenciaFecha]
    disponibles: list[TablaDisponible]


class ProcesoDef(BaseModel):
    id: str
    nombre: str
    descripcion: str
    comando: str
    escribe: str
    genera: bool                  # deja archivos que se pueden ver


class ScriptArchivo(BaseModel):
    ruta: str
    codigo: str


class ArchivoProceso(BaseModel):
    """Un archivo que el proceso deja en el repo DICCIONARIO."""

    ruta: str                     # relativa a la carpeta del repo, con «/»
    tamano: int
    modificado: str
    tipo: str                     # texto (se puede ver) | otro


class VistaArchivo(BaseModel):
    ruta: str
    texto: str
    recortado: bool


class ProcesoDetalle(ProcesoDef):
    scripts: list[ScriptArchivo]
    archivos: list[ArchivoProceso]


class Ejecucion(BaseModel):
    id: str
    proceso: str
    estado: str                   # ejecutando | ok | error
    inicio: str
    fin: str | None
    codigo: int | None


class EjecucionDetalle(Ejecucion):
    log: str
