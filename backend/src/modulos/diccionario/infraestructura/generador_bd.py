"""Lo que SQL Server sabe de los procedimientos del MIS: dependencias, parámetros y estructura de tablas. Solo lectura de metadatos (nada de EXEC de un SP de reporte).

Consultas estándar de catálogo de SQL Server (dependencias, parámetros e INFORMATION_SCHEMA); todas de solo lectura.
Los nombres de SP y tablas viajan como parámetros (`?`), nunca pegados al texto de la consulta.
"""

from __future__ import annotations

from core import bd
from modulos.diccionario.aplicacion import dto
from core.servidores import servidor_de_base

ESPERA = 180      # segundos por consulta: las dependencias de ~260 SP tardan
TRAMO = 400       # pares por INSERT (≤1000 filas por VALUES). shortcut: el tope de 2100 parámetros es de TODA la consulta (~1050 SP por base); partir la llamada si una base los supera

_DEPENDENCIAS = """
SET NOCOUNT ON;
DECLARE @catalogo TABLE (esquema sysname, nombre sysname);
{inserts}
DECLARE @resultado TABLE (
    sp_base sysname, sp_esquema sysname, sp_nombre sysname,
    ref_servidor sysname NULL, ref_base sysname NULL, ref_esquema sysname NULL,
    ref_entidad sysname NULL, ref_columna sysname NULL, ref_tipo nvarchar(60) NULL, ref_objeto_tipo nvarchar(60) NULL,
    es_lectura bit NULL, es_escritura bit NULL, es_select_todo bit NULL,
    origen varchar(30), error nvarchar(2000) NULL);

DECLARE @esquema sysname, @nombre sysname, @objeto nvarchar(520);
DECLARE c CURSOR LOCAL FAST_FORWARD FOR SELECT esquema, nombre FROM @catalogo;
OPEN c;
FETCH NEXT FROM c INTO @esquema, @nombre;
WHILE @@FETCH_STATUS = 0
BEGIN
    SET @objeto = QUOTENAME(@esquema) + N'.' + QUOTENAME(@nombre);
    IF OBJECT_ID(@objeto) IS NULL
        INSERT INTO @resultado (sp_base, sp_esquema, sp_nombre, origen, error)
        VALUES (DB_NAME(), @esquema, @nombre, 'catalogo', N'El SP no existe en esta base');
    ELSE
    BEGIN
        BEGIN TRY
            INSERT INTO @resultado
            SELECT DB_NAME(), @esquema, @nombre,
                   r.referenced_server_name, ISNULL(r.referenced_database_name, DB_NAME()),
                   r.referenced_schema_name, r.referenced_entity_name, r.referenced_minor_name,
                   r.referenced_class_desc, o.type_desc, r.is_selected, r.is_updated, r.is_select_all,
                   'dm_sql_referenced_entities', NULL
            FROM sys.dm_sql_referenced_entities(@objeto, N'OBJECT') r
            LEFT JOIN sys.objects o ON o.object_id = r.referenced_id;
        END TRY
        BEGIN CATCH
            INSERT INTO @resultado (sp_base, sp_esquema, sp_nombre, origen, error)
            VALUES (DB_NAME(), @esquema, @nombre, 'dm_sql_referenced_entities', ERROR_MESSAGE());
        END CATCH;

        INSERT INTO @resultado (sp_base, sp_esquema, sp_nombre, ref_servidor, ref_base, ref_esquema,
                                ref_entidad, ref_tipo, ref_objeto_tipo, origen)
        SELECT DB_NAME(), @esquema, @nombre, d.referenced_server_name,
               ISNULL(d.referenced_database_name, DB_NAME()), d.referenced_schema_name,
               d.referenced_entity_name, d.referenced_class_desc, o.type_desc, 'sql_expression_dependencies'
        FROM sys.sql_expression_dependencies d
        LEFT JOIN sys.objects o ON o.object_id = d.referenced_id
        WHERE d.referencing_id = OBJECT_ID(@objeto);
    END;
    FETCH NEXT FROM c INTO @esquema, @nombre;
END;
CLOSE c;
DEALLOCATE c;

SELECT sp_base, sp_esquema, sp_nombre, ref_servidor, ref_base, ref_esquema, ref_entidad,
       ref_columna, ref_tipo, ref_objeto_tipo, es_lectura, es_escritura, es_select_todo, origen, error
FROM @resultado
"""

PARAMETROS = """
SELECT DB_NAME() AS base, SCHEMA_NAME(o.schema_id) AS esquema, o.name AS sp, p.name AS nombre,
       TYPE_NAME(p.user_type_id) AS tipo, p.has_default_value AS tiene_defecto, p.is_output AS salida, p.parameter_id AS orden
FROM sys.parameters p
JOIN sys.objects o ON o.object_id = p.object_id
WHERE o.type = 'P' AND p.parameter_id > 0
"""

ESTRUCTURA = """
SELECT DB_NAME() AS base, t.TABLE_SCHEMA AS esquema, t.TABLE_NAME AS tabla, t.TABLE_TYPE AS tipo_objeto,
       c.ORDINAL_POSITION AS orden, c.COLUMN_NAME AS columna, c.DATA_TYPE AS tipo,
       c.CHARACTER_MAXIMUM_LENGTH AS largo, c.NUMERIC_PRECISION AS precision, c.NUMERIC_SCALE AS escala,
       c.IS_NULLABLE AS acepta_nulos
FROM INFORMATION_SCHEMA.TABLES t
JOIN INFORMATION_SCHEMA.COLUMNS c ON c.TABLE_SCHEMA = t.TABLE_SCHEMA AND c.TABLE_NAME = t.TABLE_NAME
WHERE {filtro}
"""

CUERPOS = """
SELECT SCHEMA_NAME(o.schema_id) AS esquema, o.name AS nombre, m.definition AS definicion
FROM sys.sql_modules m
JOIN sys.objects o ON o.object_id = m.object_id
WHERE o.type = 'P' AND ({filtro})
"""


def scripts() -> list[dto.ScriptArchivo]:
    return [dto.ScriptArchivo(ruta="SQL · dependencias de los procedimientos (por base)", codigo=_DEPENDENCIAS.replace("{inserts}", "INSERT INTO @catalogo (esquema, nombre) VALUES (?, ?), …;").strip()),
            dto.ScriptArchivo(ruta="SQL · parámetros de los procedimientos (por base)", codigo=PARAMETROS.strip()),
            dto.ScriptArchivo(ruta="SQL · código de los procedimientos (por base)", codigo=CUERPOS.replace("{filtro}", "(SCHEMA_NAME(o.schema_id) = ? AND o.name = ?) OR …").strip()),
            dto.ScriptArchivo(ruta="SQL · estructura de las tablas que usan (por base)", codigo=ESTRUCTURA.replace("{filtro}", "(t.TABLE_SCHEMA = ? AND t.TABLE_NAME = ?) OR …").strip())]


def _filas(cursor) -> list[dict]:
    """Las filas del último conjunto de resultados con columnas (el lote termina con el SELECT)."""
    filas: list[dict] = []
    while True:
        if cursor.description:
            columnas = [c[0] for c in cursor.description]
            filas = [dict(zip(columnas, f)) for f in cursor.fetchall()]
        if not cursor.nextset():
            return filas


def _ejecutar(base: str, sql: str, params: tuple = ()) -> list[dict]:
    with bd.conexion_pyodbc(servidor_de_base(base), base) as conn:
        conn.timeout = ESPERA
        cursor = conn.cursor()
        try:
            cursor.execute(sql, *params)
            return _filas(cursor)
        finally:
            cursor.close()


def dependencias(base: str, sps: list[tuple[str, str]]) -> list[dict]:
    """Una fila por (SP, tabla, columna) que el motor tiene registrada, más el error de los SP que no compilan o no existen."""
    pares = sorted(set(sps))
    inserts = "\n".join("INSERT INTO @catalogo (esquema, nombre) VALUES " + ", ".join(["(?, ?)"] * len(pares[i:i + TRAMO])) + ";" for i in range(0, len(pares), TRAMO))
    return _ejecutar(base, _DEPENDENCIAS.format(inserts=inserts), tuple(x for par in pares for x in par))


def parametros(base: str) -> list[dict]:
    return _ejecutar(base, PARAMETROS)


def cuerpos(base: str, sps: list[tuple[str, str]]) -> list[dict]:
    """El texto (`definicion`) de los procedimientos pedidos; una cuenta sin VIEW DEFINITION recibe NULL y esos no se analizan."""
    filas: list[dict] = []
    pares = sorted(set(sps))
    for i in range(0, len(pares), 500):
        parte = pares[i:i + 500]
        filtro = " OR ".join("(SCHEMA_NAME(o.schema_id) = ? AND o.name = ?)" for _ in parte)
        filas += [f for f in _ejecutar(base, CUERPOS.format(filtro=filtro), tuple(x for par in parte for x in par)) if f.get("definicion")]
    return filas


def estructura(base: str, tablas: list[tuple[str, str]]) -> list[dict]:
    """Columnas reales (tipo, nulos) de las tablas pedidas; las que no existen no devuelven filas."""
    filas: list[dict] = []
    pares = sorted(set(tablas))
    for i in range(0, len(pares), 500):
        parte = pares[i:i + 500]
        filtro = " OR ".join("(t.TABLE_SCHEMA = ? AND t.TABLE_NAME = ?)" for _ in parte)
        filas += _ejecutar(base, ESTRUCTURA.format(filtro=filtro), tuple(x for par in parte for x in par))
    return filas
