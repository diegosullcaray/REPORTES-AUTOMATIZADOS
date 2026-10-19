"""Analizador estático (heurístico) de procedimientos T-SQL.

Lee el texto de un CREATE PROCEDURE y responde: qué tablas usa y con qué operación, qué columnas de cada una, qué otros SP invoca, qué columnas devuelve y si
usa SQL dinámico. No es un parser completo: sirve para procedimientos de reportes y declara lo que no pudo resolver en vez de adivinar. La fuente
autoritativa sigue siendo el motor (`sys.dm_sql_referenced_entities`); esto lo complementa donde el motor no llega (SQL que no compila, columnas por alias).

Confianza de cada columna: `exacta` (calificada con alias o nombre de tabla, o lista de INSERT) · `inferida` (sin calificar, con una sola tabla de origen).
Una columna sin calificar con varias fuentes posibles va a `sin_resolver`. Función pura: solo texto adentro, un dict afuera.
"""

from __future__ import annotations

import re

_PALABRAS_CLAVE = set("""
add all alter and any as asc authorization backup begin between break browse bulk by cascade case catch check
checkpoint close clustered coalesce collate column commit compute constraint contains containstable continue
convert create cross current current_date current_time current_timestamp current_user cursor database dbcc
deallocate declare default delete deny desc disk distinct distributed double drop dump else end errlvl escape
except exec execute exists exit external fetch file fillfactor for foreign freetext freetexttable from full
function goto grant group having holdlock identity identity_insert identitycol if in index inner insert
intersect into is join key kill left like lineno load matched merge national nocheck nonclustered not null
nullif of off offsets on open opendatasource openquery openrowset openxml option or order outer output over
partition percent pivot plan precision primary print proc procedure public raiserror read readtext reconfigure
references replication restore restrict return revert revoke right rollback rowcount rowguidcol rule save schema
securityaudit select semantickeyphrasetable semanticsimilaritydetailstable semanticsimilaritytable
session_user set setuser shutdown some statistics system_user table tablesample textsize then to top tran
transaction trigger truncate try try_convert tsequal union unique unpivot update updatetext use user using values
varying view waitfor when where while with within writetext throw nocount ansi_nulls quoted_identifier dateformat
xact_abort ansi_warnings arithabort isolation level uncommitted committed repeatable serializable snapshot
nolock readuncommitted readcommitted rowlock tablock tablockx updlock xlock paglock nowait readpast
recompile apply rows range unbounded preceding following first next only offset fetch ties
grouping rollup cube sets
""".split())

_TIPOS = set("""
bigint int smallint tinyint bit decimal numeric money smallmoney float real date datetime datetime2
datetimeoffset smalldatetime time char varchar text nchar nvarchar ntext binary varbinary image
uniqueidentifier xml sql_variant hierarchyid geography geometry max sysname cursor rowversion timestamp
""".split())

# Palabras que inician una sentencia nueva (fuera de un CASE).
_INICIO = {"select", "insert", "update", "delete", "merge", "exec", "execute", "set", "declare", "if", "else", "while", "begin", "end", "return", "create", "alter",
           "drop", "truncate", "print", "raiserror", "throw", "open", "fetch", "close", "deallocate", "with", "use", "go", "commit", "rollback", "break", "continue",
           "waitfor", "union", "except", "intersect"}

# Tras una fuente, estas palabras no pueden ser su alias.
_NO_ALIAS = _INICIO | {"where", "on", "join", "inner", "left", "right", "full", "outer", "cross", "group", "order", "having", "option", "output", "pivot", "unpivot",
                       "for", "when", "then", "into", "from", "using", "values", "as", "apply", "tablesample", "offset"}

# Funciones de fecha cuyo primer argumento es una parte de fecha (day, mm, yyyy…), no una columna.
_FUNCIONES_DE_FECHA = {"dateadd", "datediff", "datediff_big", "datepart", "datename", "datetrunc", "date_bucket"}

_INICIO_ID = re.compile(r'[A-Za-z_@#\[À-ɏ"]')
_ID = re.compile(r"[A-Za-z0-9_@#$À-ɏ]")
_DOS = {">=", "<=", "<>", "!=", "+=", "-=", "*=", "/=", "::"}


# ─── 1. Léxico ────────────────────────────────────────────────────────────────

def tokenizar(texto: str) -> list[dict]:
    """Tokens: identificadores multiparte (`id`), cadenas (`cad`), números (`num`), operadores (`op`) y los símbolos `( ) , ;`."""
    tokens: list[dict] = []
    n, i = len(texto), 0

    def leer_parte() -> tuple[str, bool]:
        nonlocal i
        c = texto[i]
        if c in "[\"":
            fin = texto.find("]" if c == "[" else '"', i + 1)
            parte = texto[i + 1:n if fin < 0 else fin]
            i = n if fin < 0 else fin + 1
            return parte, True
        ini = i
        while i < n and _ID.match(texto[i]):
            i += 1
        return texto[ini:i], False

    def car(k: int) -> str:
        return texto[k] if k < n else ""

    while i < n:
        c = texto[i]
        if c.isspace():
            i += 1
            continue
        if c == "-" and car(i + 1) == "-":
            while i < n and texto[i] != "\n":
                i += 1
            continue
        if c == "/" and car(i + 1) == "*":
            prof, i = 1, i + 2
            while i < n and prof > 0:
                if texto[i] == "/" and car(i + 1) == "*":
                    prof, i = prof + 1, i + 2
                elif texto[i] == "*" and car(i + 1) == "/":
                    prof, i = prof - 1, i + 2
                else:
                    i += 1
            continue
        if c == "'" or (c in "Nn" and car(i + 1) == "'"):
            i += 1 if c == "'" else 2
            valor = []
            while i < n:
                if texto[i] == "'" and car(i + 1) == "'":
                    valor.append("'")
                    i += 2
                elif texto[i] == "'":
                    i += 1
                    break
                else:
                    valor.append(texto[i])
                    i += 1
            tokens.append({"t": "cad", "valor": "".join(valor)})
            continue
        if c.isdigit() or (c == "." and car(i + 1).isdigit()):
            ini = i
            while i < n and texto[i] in "0123456789.eE":
                i += 1
            tokens.append({"t": "num", "valor": texto[ini:i]})
            continue
        if _INICIO_ID.match(c):
            partes = [leer_parte()]
            # Identificador multiparte: a.b, a..b (base..tabla), a.*, con espacios opcionales.
            while True:
                j = i
                while j < n and texto[j].isspace():
                    j += 1
                if car(j) != ".":
                    break
                k, vacias = j + 1, 0
                while car(k) == ".":
                    vacias, k = vacias + 1, k + 1
                while k < n and texto[k].isspace():
                    k += 1
                if car(k) == "*":
                    partes += [("", False)] * vacias + [("*", False)]
                    i = k + 1
                    break
                if not (car(k) and _INICIO_ID.match(car(k))):
                    break
                partes += [("", False)] * vacias
                i = k
                partes.append(leer_parte())
            valores = [p[0] for p in partes]
            tokens.append({"t": "id", "partes": valores, "citado": any(p[1] for p in partes), "texto": ".".join(valores)})
            continue
        if texto[i:i + 2] in _DOS:
            tokens.append({"t": "op", "valor": texto[i:i + 2]})
            i += 2
            continue
        tokens.append({"t": c if c in "(),;" else "op", "valor": c})
        i += 1
    return tokens


def agrupar(tokens: list[dict]) -> list[dict]:
    """Agrupa los paréntesis en nodos `grupo`, recursivamente."""
    raiz: list[dict] = []
    pila = [raiz]
    for tk in tokens:
        if tk["t"] == "(":
            g = {"t": "grupo", "hijos": []}
            pila[-1].append(g)
            pila.append(g["hijos"])
        elif tk["t"] == ")":
            if len(pila) > 1:
                pila.pop()
        else:
            pila[-1].append(tk)
    return raiz


# ─── 2. Utilidades sobre tokens ───────────────────────────────────────────────

def _at(lista: list, k: int):
    return lista[k] if 0 <= k < len(lista) else None


def _pc(tk) -> str | None:
    return tk["partes"][0].lower() if tk and tk["t"] == "id" and not tk["citado"] and len(tk["partes"]) == 1 else None


def _es_palabra(tk, *palabras: str) -> bool:
    p = _pc(tk)
    return p is not None and p in palabras


def _es_clave(tk) -> bool:
    p = _pc(tk)
    return p is not None and (p in _PALABRAS_CLAVE or p in _TIPOS)


def _es_variable(tk) -> bool:
    return bool(tk) and tk["t"] == "id" and tk["partes"][0].startswith("@")


def _es_temporal(partes: list[str]) -> bool:
    return bool(partes) and partes[-1].startswith("#")


def _primero(lista: list):
    return next((x for x in lista if x["t"] != ";"), None)


def _es_subconsulta(g) -> bool:
    return bool(g) and g["t"] == "grupo" and _es_palabra(_primero(g["hijos"]), "select", "with")


def _texto_token(x) -> str:
    if not x:
        return ""
    if x["t"] == "id":
        return x["texto"]
    if x["t"] == "cad":
        return f"'{x['valor']}'"
    if x["t"] == "grupo":
        return "(" + " ".join(_texto_token(h) for h in x["hijos"]) + ")"
    return x["valor"]


def _partir_por_comas(lista: list) -> list[list]:
    salida: list[list] = [[]]
    for x in lista:
        if x["t"] == ",":
            salida.append([])
        else:
            salida[-1].append(x)
    return [s for s in salida if s]


class _Bloque:
    def __init__(self, tipo: str):
        self.tipo = tipo              # select | insert | update | delete | merge | exec | control | declare | set | ddl
        self.fuentes: list[dict] = []  # {partes, alias, clase: tabla|cte|temporal|derivada|funcion|variable}
        self.refs: list[dict] = []     # {partes, token, en_set}
        self.lista_select: list[dict] = []
        self.alias_select: set[str] = set()
        self.objetivo: dict | None = None
        self.into = False
        self.union = False
        self.asigna_variable = False
        self.uso_objetivo: str | None = None
        self.columnas_objetivo: list[str] | None = None
        self.cerrado_insert = False
        self.alimenta_insert = False
        self.alias_heredados: set[str] | None = None
        self.siguiente_es_union = False
        self.descartar_desde: int | None = None


class _Ctx:
    def __init__(self, base: str | None, esquema: str):
        self.base, self.esquema = base, esquema
        self.procedimiento: dict | None = None
        self.tablas: dict[str, dict] = {}
        self.sin_resolver: dict[str, dict] = {}
        self.ctes: set[str] = set()
        self.temporales: set[str] = set()
        self.invocaciones: list[dict] = []
        self.resultados: list[list[str]] = []
        self.sql_dinamico = False
        self.advertencias: dict[str, None] = {}   # conjunto que conserva el orden


# ─── 3. Análisis ──────────────────────────────────────────────────────────────

def analizar_procedimiento(texto: str, base: str | None = None, esquema: str = "dbo") -> dict:
    """`texto`: cuerpo del procedimiento (CREATE/ALTER PROCEDURE …). `base` y `esquema`: los del SP, para nombres de una o dos partes."""
    arbol = agrupar(tokenizar(texto))
    ctx = _Ctx(base, esquema or "dbo")
    cuerpo = _extraer_cabecera(arbol, ctx)
    _analizar_secuencia(cuerpo, ctx, [], 0)
    tablas = []
    for t in sorted(ctx.tablas.values(), key=lambda t: t["completo"].lower()):
        tablas.append({**{k: v for k, v in t.items() if k not in ("usos", "columnas")}, "usos": sorted(t["usos"]),
                       "columnas": sorted(t["columnas"].values(), key=lambda c: c["nombre"].lower())})
    return {"procedimiento": ctx.procedimiento, "tablas": tablas,
            "sin_resolver": [{**s, "candidatas": sorted(s["candidatas"])} for s in ctx.sin_resolver.values()],
            "invocaciones": ctx.invocaciones,
            "resultados": ctx.resultados, "sql_dinamico": ctx.sql_dinamico, "advertencias": list(ctx.advertencias)}


def _extraer_cabecera(arbol: list, ctx: _Ctx) -> list:
    """Lee `CREATE PROCEDURE esquema.nombre @p tipo = x, … AS` y devuelve el resto."""
    i = next((k for k, tk in enumerate(arbol) if _es_palabra(tk, "create", "alter") and _es_palabra(_at(arbol, k + 1), "proc", "procedure", "or")), -1)
    if i < 0:
        ctx.advertencias["No se encontró CREATE/ALTER PROCEDURE: se analizó el texto completo."] = None
        return arbol
    i += 1
    if _es_palabra(_at(arbol, i), "or"):
        i += 2   # OR ALTER
    i += 1       # PROC | PROCEDURE
    nombre_tk = _at(arbol, i)
    i += 1
    partes = nombre_tk["partes"] if nombre_tk and nombre_tk["t"] == "id" else []
    lista: list = []
    # Parámetros: en línea o entre paréntesis, hasta el AS que abre el cuerpo.
    while i < len(arbol) and not _es_palabra(arbol[i], "as"):
        if arbol[i]["t"] == "grupo" and not lista and arbol[i]["hijos"] and _es_variable(arbol[i]["hijos"][0]):
            lista.extend(arbol[i]["hijos"])
        elif _es_palabra(arbol[i], "with"):
            i += 1
            while i < len(arbol) and not _es_palabra(arbol[i], "as"):
                i += 1
            break
        else:
            lista.append(arbol[i])
        i += 1
    parametros = []
    for item in _partir_por_comas(lista):
        if not _es_variable(item[0]):
            continue
        igual = next((k for k, x in enumerate(item) if x["t"] == "op" and x["valor"] == "="), -1)
        tipo_tks = [x for x in (item[1:] if igual < 0 else item[1:igual]) if not _es_palabra(x, "output", "out", "readonly", "as")]
        tipo = "".join("(" + ",".join(_texto_token(h) for h in x["hijos"] if h["t"] != ",") + ")" if x["t"] == "grupo" else _texto_token(x) for x in tipo_tks).strip()
        defecto = None if igual < 0 else " ".join(_texto_token(x) for x in item[igual + 1:] if not _es_palabra(x, "output", "out", "readonly")) or None
        parametros.append({"nombre": item[0]["partes"][0], "tipo": tipo or None, "porDefecto": defecto, "salida": any(_es_palabra(x, "output", "out") for x in item)})
    ctx.procedimiento = {"esquema": partes[-2] if len(partes) > 1 else None, "nombre": partes[-1] if partes else None, "parametros": parametros}
    if len(partes) > 1:
        ctx.esquema = partes[-2]
    return arbol[i + 1:]


def _analizar_secuencia(items: list, ctx: _Ctx, padres: list, profundidad: int) -> None:
    """Recorre una secuencia de tokens del mismo nivel. `padres` es la cadena de bloques externos, para subconsultas correlacionadas."""
    bloque = _Bloque("control")
    modo = "expr"   # expr | fuente | lista-select | objetivo | into | set
    prof_case = 0

    def cerrar() -> None:
        _cerrar_bloque(bloque, ctx, padres, profundidad)

    i = -1
    while True:
        i += 1
        if i >= len(items):
            break
        tk = items[i]
        p = _pc(tk)

        if tk["t"] == ";":
            cerrar()
            bloque, modo = _Bloque("control"), "expr"
            continue
        if p == "case" or (p == "end" and prof_case > 0):
            prof_case += 1 if p == "case" else -1
            if modo == "lista-select":
                bloque.lista_select.append(tk)
            continue
        # Dentro de un CASE, WHEN/THEN/ELSE no cambian de cláusula.
        if prof_case > 0 and p in ("when", "then", "else"):
            if modo == "lista-select":
                bloque.lista_select.append(tk)
            continue

        # ── WITH: definición de CTE (o sugerencia de tabla, que se ignora)
        if p == "with" and prof_case == 0:
            sig = _at(items, i + 1)
            if sig and sig["t"] == "grupo":   # WITH (NOLOCK)
                i += 1
                continue
            cerrar()
            bloque, modo = _Bloque("control"), "expr"
            k = i + 1
            while _at(items, k) and items[k]["t"] == "id":
                ctx.ctes.add(items[k]["partes"][-1].lower())
                k += 1
                if _at(items, k) and items[k]["t"] == "grupo" and not _es_subconsulta(items[k]):
                    k += 1   # lista de columnas de la CTE
                if not _es_palabra(_at(items, k), "as") or not (_at(items, k + 1) and items[k + 1]["t"] == "grupo"):
                    break
                _analizar_secuencia(items[k + 1]["hijos"], ctx, padres, profundidad + 1)
                k += 2
                if _at(items, k) and items[k]["t"] == ",":
                    k += 1
                else:
                    break
            i = k - 1
            continue

        # ── Inicio de sentencia
        if p and p in _INICIO and prof_case == 0 and not tk["citado"]:
            if p == "set" and bloque.tipo in ("update", "merge"):
                modo = "set"
                continue
            if p == "select" and bloque.tipo == "insert" and not bloque.cerrado_insert:
                bloque.cerrado_insert = True
                cerrar()
                bloque = _Bloque("select")
                bloque.alimenta_insert = True
                modo = "lista-select"
                continue
            if p in ("update", "delete", "insert") and bloque.tipo == "merge":
                modo = "expr"
                continue
            if p in ("exec", "execute") and bloque.tipo == "insert":
                bloque.tipo = "insert-exec"
                _registrar_exec(items, i, ctx)
                i = _saltar_exec(items, i)
                continue
            union = p in ("union", "except", "intersect")
            cerrar()
            if union:
                previo = bloque
                bloque = _Bloque("control")
                # ORDER BY al final de un UNION usa los alias del primer SELECT.
                bloque.alias_heredados = previo.alias_select | (previo.alias_heredados or set())
                if _es_palabra(_at(items, i + 1), "all"):
                    i += 1
                bloque.siguiente_es_union = True
                modo = "expr"
                continue
            era_union, heredados = bloque.siguiente_es_union, bloque.alias_heredados
            if p == "select":
                bloque = _Bloque("select")
                bloque.union, bloque.alias_heredados = era_union, heredados
                modo = "lista-select"
            elif p == "insert":
                bloque, modo = _Bloque("insert"), "objetivo"
                bloque.uso_objetivo = "inserta"
                if _es_palabra(_at(items, i + 1), "into"):
                    i += 1
            elif p == "update":
                bloque, modo = _Bloque("update"), "objetivo"
                bloque.uso_objetivo = "actualiza"
            elif p == "delete":
                bloque, modo = _Bloque("delete"), "objetivo"
                bloque.uso_objetivo = "elimina"
                if _es_palabra(_at(items, i + 1), "from"):
                    i += 1
            elif p == "merge":
                bloque, modo = _Bloque("merge"), "objetivo"
                bloque.uso_objetivo = "fusiona"
                ctx.advertencias["MERGE analizado de forma aproximada: revisar columnas contra el motor."] = None
                if _es_palabra(_at(items, i + 1), "into"):
                    i += 1
            elif p == "truncate":
                bloque = _Bloque("ddl")
                if _es_palabra(_at(items, i + 1), "table") and _at(items, i + 2) and items[i + 2]["t"] == "id" and not _es_clave(items[i + 2]):
                    partes = items[i + 2]["partes"]
                    if _es_temporal(partes):
                        ctx.temporales.add(partes[-1])
                    else:
                        _registrar_tabla(ctx, partes, "trunca")
                    i += 2
            elif p in ("exec", "execute"):
                bloque = _Bloque("exec")
                _registrar_exec(items, i, ctx)
                i = _saltar_exec(items, i)
            elif p in ("create", "alter", "drop"):
                bloque = _Bloque("ddl")
                if _es_palabra(_at(items, i + 1), "table"):
                    k = i + 4 if _es_palabra(_at(items, i + 2), "if") and _es_palabra(_at(items, i + 3), "exists") else i + 2
                    if _at(items, k) and items[k]["t"] == "id" and not _es_clave(items[k]):
                        partes = items[k]["partes"]
                        if _es_temporal(partes):
                            ctx.temporales.add(partes[-1])
                        else:
                            _registrar_tabla(ctx, partes, "elimina-objeto" if p == "drop" else "crea")
                        i = k
            elif p == "declare":
                bloque, modo = _Bloque("declare"), "expr"
            elif p == "set":
                bloque, modo = _Bloque("set"), "expr"
            else:
                bloque, modo = _Bloque("control"), "expr"
            continue

        # ── Cláusulas que cambian el modo dentro del bloque
        if p in ("from", "join", "apply", "using"):
            modo = "fuente"
            continue
        if p == "into" and bloque.tipo == "select":
            modo = "into"
            continue
        if p == "into" and bloque.tipo == "merge":
            continue
        if p in ("where", "on", "group", "having", "order", "when", "then", "by", "output", "option"):
            if p == "output" and bloque.tipo != "select":
                bloque.descartar_desde = len(bloque.refs)
            modo = "expr"
            continue
        if p == "values":
            modo = "expr"
            continue

        # ── Según el modo
        if modo == "objetivo":
            if tk["t"] == "id" and not _es_clave(tk):
                if _es_palabra(tk, "top"):
                    continue
                bloque.objetivo = {"partes": tk["partes"], "uso": bloque.uso_objetivo, "alias": None, "fuente": None}
                k = i + 1
                if _es_palabra(_at(items, k), "with") and _at(items, k + 1) and items[k + 1]["t"] == "grupo":
                    k += 2
                if _es_palabra(_at(items, k), "as"):
                    k += 1
                sig = _at(items, k)
                if sig and sig["t"] == "id" and (_pc(sig) or "") not in _NO_ALIAS and not _es_clave(sig):
                    bloque.objetivo["alias"] = sig["partes"][0]
                    k += 1
                # INSERT INTO t (c1, c2): lista de columnas del objetivo.
                sig = _at(items, k)
                if bloque.tipo == "insert" and sig and sig["t"] == "grupo" and not _es_subconsulta(sig):
                    bloque.columnas_objetivo = [x["partes"][-1] for x in sig["hijos"] if x["t"] == "id"]
                    k += 1
                i = k - 1
                modo = "expr"
            continue   # TOP (n) y palabras clave antes del objetivo

        if modo == "into":
            if tk["t"] == "id":
                if _es_temporal(tk["partes"]):
                    ctx.temporales.add(tk["partes"][-1])
                else:
                    _registrar_tabla(ctx, tk["partes"], "crea")
                bloque.into = True
            modo = "expr"
            continue

        if modo == "fuente":
            if tk["t"] == ",":
                continue
            if _es_palabra(tk, "inner", "left", "right", "full", "outer", "cross", "lateral"):
                continue
            if tk["t"] == "grupo":   # Tabla derivada: (SELECT …) alias
                _analizar_secuencia(tk["hijos"], ctx, [bloque, *padres], profundidad + 1)
                alias, avance = _leer_alias(items, i + 1)
                bloque.fuentes.append({"partes": [alias or "(derivada)"], "alias": alias, "clase": "derivada"})
                i += avance
                continue
            if tk["t"] == "id" and not _es_clave(tk):
                clase, k = "tabla", i + 1
                if _es_variable(tk):
                    clase = "variable"
                elif _es_temporal(tk["partes"]):
                    clase = "temporal"
                    ctx.temporales.add(tk["partes"][-1])
                elif len(tk["partes"]) == 1 and tk["partes"][0].lower() in ctx.ctes:
                    clase = "cte"
                sig = _at(items, k)
                if sig and sig["t"] == "grupo":   # Función con valor de tabla: dbo.fn(@x) alias
                    clase = "funcion" if clase == "tabla" else clase
                    _analizar_secuencia(sig["hijos"], ctx, [bloque, *padres], profundidad + 1)
                    if clase == "funcion":
                        _registrar_funcion(ctx, tk["partes"])
                    k += 1
                if _es_palabra(_at(items, k), "with") and _at(items, k + 1) and items[k + 1]["t"] == "grupo":
                    k += 2
                alias, avance = _leer_alias(items, k)
                k += avance
                bloque.fuentes.append({"partes": tk["partes"], "alias": alias, "clase": clase})
                if clase == "tabla":
                    _registrar_tabla(ctx, tk["partes"], "fusiona" if bloque.tipo == "merge" and len(bloque.fuentes) == 1 and not bloque.objetivo else "lee")
                i = k - 1
                continue
            if _es_palabra(tk, "pivot", "unpivot"):
                ctx.advertencias["PIVOT/UNPIVOT presente: las columnas pivotadas no se resuelven."] = None
                modo = "expr"
                continue
            modo = "expr"   # cae al tratamiento de expresión

        if modo == "lista-select":
            if _es_palabra(tk, "distinct", "all"):
                continue
            if _es_palabra(tk, "top"):
                if _at(items, i + 1):
                    i += 1
                if _es_palabra(_at(items, i + 1), "percent"):
                    i += 1
                continue
            bloque.lista_select.append(tk)

        # ── Expresión: referencias a columna, subconsultas, funciones
        if tk["t"] == "grupo":
            if _es_subconsulta(tk):
                _analizar_secuencia(tk["hijos"], ctx, [bloque, *padres], profundidad + 1)
            else:
                _recorrer_expresion(tk["hijos"], bloque, ctx, padres, profundidad, modo == "set", _pc(_at(items, i - 1) if i > 0 else None))
            continue
        if tk["t"] == "id":
            if _es_clave(tk) or _es_variable(tk):
                continue
            sig = _at(items, i + 1)
            if sig and sig["t"] == "grupo":   # llamada a función: el nombre no es columna
                continue
            bloque.refs.append({"partes": tk["partes"], "token": tk, "en_set": modo == "set"})
    cerrar()


def _recorrer_expresion(hijos: list, bloque: _Bloque, ctx: _Ctx, padres: list, profundidad: int, en_set: bool, funcion: str | None = None) -> None:
    """Contenido de paréntesis que no es subconsulta: argumentos, IN (…), OVER (…)."""
    for i, tk in enumerate(hijos):
        if tk["t"] == "grupo":
            if _es_subconsulta(tk):
                _analizar_secuencia(tk["hijos"], ctx, [bloque, *padres], profundidad + 1)
            else:
                _recorrer_expresion(tk["hijos"], bloque, ctx, padres, profundidad, en_set, _pc(hijos[i - 1] if i > 0 else None))
            continue
        if i == 0 and funcion in _FUNCIONES_DE_FECHA:
            continue
        if tk["t"] != "id" or _es_clave(tk) or _es_variable(tk):
            continue
        sig = _at(hijos, i + 1)
        if sig and sig["t"] == "grupo":
            continue
        if i > 0 and _es_palabra(hijos[i - 1], "as"):   # CAST(x AS tipo): lo que sigue a AS es un tipo
            continue
        bloque.refs.append({"partes": tk["partes"], "token": tk, "en_set": en_set})


def _leer_alias(items: list, k: int) -> tuple[str | None, int]:
    avance = 0
    if _es_palabra(_at(items, k), "as"):
        avance, k = avance + 1, k + 1
    tk = _at(items, k)
    if tk and tk["t"] == "id" and len(tk["partes"]) == 1 and not _es_variable(tk) and (tk["citado"] or ((_pc(tk) or "") not in _NO_ALIAS and not _es_clave(tk))):
        return tk["partes"][0], avance + 1
    return None, avance


def _registrar_exec(items: list, i: int, ctx: _Ctx) -> None:
    k = i + 1
    if _es_variable(_at(items, k)) and _at(items, k + 1) and items[k + 1]["t"] == "op" and items[k + 1]["valor"] == "=":
        k += 2
    tk = _at(items, k)
    if tk is None or tk["t"] in ("grupo", "cad") or _es_variable(tk):
        ctx.sql_dinamico = True
        return
    if tk["t"] != "id":
        return
    nombre = tk["partes"]
    if re.fullmatch(r"sp_executesql", nombre[-1], re.I):
        ctx.sql_dinamico = True
        return
    # Un argumento por coma, con sus tokens juntos: `@p = @x OUTPUT` queda como un solo argumento.
    args: list[list[str]] = [[]]
    for a in items[k + 1:]:
        if a["t"] == ";" or (_pc(a) in _INICIO and not a["citado"]):
            break
        if a["t"] == ",":
            args.append([])
        else:
            args[-1].append(_texto_token(a))
    ctx.invocaciones.append({"nombre": ".".join(nombre), "partes": nombre, "argumentos": [a for a in (" ".join(x) for x in args) if a]})


def _saltar_exec(items: list, i: int) -> int:
    k = i + 1
    while k < len(items) and items[k]["t"] != ";" and not (_pc(items[k]) in _INICIO and not items[k]["citado"]):
        k += 1
    return k - 1


# ─── 4. Resolución de nombres ────────────────────────────────────────────────

def _resolver_nombre_tabla(partes: list[str], base: str | None, esquema_sp: str) -> dict:
    """Nombre completo de una tabla con la base y el esquema implícitos del SP."""
    p = list(partes)
    servidor, esquema, implicito = None, esquema_sp or "dbo", False
    if len(p) >= 4:
        servidor, base, esquema, nombre = p[-4:]
    elif len(p) == 3:
        base, esquema, nombre = p
    elif len(p) == 2:
        esquema, nombre = p
    else:
        nombre, implicito = p[0], True
    if not esquema:
        esquema, implicito = "dbo", True   # base..tabla
    completo = ".".join(x for x in (servidor, base, esquema, nombre) if x)
    return {"servidor": servidor, "base": base, "esquema": esquema, "nombre": nombre, "completo": completo, "clave": completo.lower(), "esquemaImplicito": implicito}


def _obtener_tabla(ctx: _Ctx, partes: list[str]) -> dict:
    n = _resolver_nombre_tabla(partes, ctx.base, ctx.esquema)
    return ctx.tablas.setdefault(n["clave"], {**n, "usos": set(), "columnas": {}})


def _registrar_tabla(ctx: _Ctx, partes: list[str], uso: str) -> None:
    _obtener_tabla(ctx, partes)["usos"].add(uso)


def _registrar_funcion(ctx: _Ctx, partes: list[str]) -> None:
    n = _resolver_nombre_tabla(partes, ctx.base, ctx.esquema)
    ctx.invocaciones.append({"nombre": n["completo"], "partes": partes, "argumentos": [], "funcion": True})


def _registrar_columna(ctx: _Ctx, partes_tabla: list[str], columna: str, confianza: str) -> None:
    t = _obtener_tabla(ctx, partes_tabla)
    previa = t["columnas"].get(columna.lower())
    if previa is None or (previa["confianza"] == "inferida" and confianza == "exacta"):
        t["columnas"][columna.lower()] = {"nombre": columna, "confianza": confianza}


def _agregar_sin_resolver(ctx: _Ctx, columna: str, candidatas: list[str]) -> None:
    previo = ctx.sin_resolver.setdefault(columna.lower(), {"columna": columna, "candidatas": set()})
    previo["candidatas"].update(candidatas)


def _cerrar_bloque(bloque: _Bloque, ctx: _Ctx, padres: list, profundidad: int) -> None:
    """Al cerrar un bloque se atribuye cada referencia a la fuente que corresponde."""
    if bloque.objetivo:   # objetivo de UPDATE/DELETE: puede ser un alias de una fuente del FROM
        o = bloque.objetivo
        por_alias = len(o["partes"]) == 1 and next((f for f in bloque.fuentes if f.get("alias") and f["alias"].lower() == o["partes"][0].lower()), None)
        if por_alias:
            if por_alias["clase"] == "tabla":
                _registrar_tabla(ctx, por_alias["partes"], o["uso"])
            o["fuente"] = por_alias
        elif _es_temporal(o["partes"]):
            ctx.temporales.add(o["partes"][-1])
            o["fuente"] = {"partes": o["partes"], "alias": o["alias"], "clase": "temporal"}
        elif o["partes"][0].startswith("@"):
            o["fuente"] = {"partes": o["partes"], "alias": o["alias"], "clase": "variable"}
        else:
            clase = "cte" if len(o["partes"]) == 1 and o["partes"][0].lower() in ctx.ctes else "tabla"
            o["fuente"] = {"partes": o["partes"], "alias": o["alias"], "clase": clase}
            if clase == "tabla":
                _registrar_tabla(ctx, o["partes"], o["uso"])
            if not any(".".join(f["partes"]).lower() == ".".join(o["partes"]).lower() for f in bloque.fuentes):
                bloque.fuentes.insert(0, o["fuente"])
        if bloque.columnas_objetivo and o["fuente"]["clase"] == "tabla":
            for c in bloque.columnas_objetivo:
                _registrar_columna(ctx, o["fuente"]["partes"], c, "exacta")
            _registrar_tabla(ctx, o["fuente"]["partes"], o["uso"])

    if bloque.tipo in ("exec", "declare", "set", "ddl", "control"):
        return

    # Alias del SELECT: `expr alias`, `expr AS alias`, `alias = expr`.
    salida: list[str] = []
    alias_tokens: list[dict] = []
    for item in _partir_por_comas(bloque.lista_select):
        ultimo, penultimo = item[-1], (item[-2] if len(item) > 1 else None)
        alias = None
        if len(item) >= 2 and item[1]["t"] == "op" and item[1]["valor"] == "=" and item[0]["t"] == "id":
            if _es_variable(item[0]):
                bloque.asigna_variable = True
            else:
                alias = item[0]["partes"][-1]
                alias_tokens.append(item[0])
        elif len(item) >= 2 and ultimo["t"] == "id" and len(ultimo["partes"]) == 1 and not _es_clave(ultimo) and not (penultimo and penultimo["t"] == "op"):
            alias = ultimo["partes"][0]
            alias_tokens.append(ultimo)
        if alias:
            bloque.alias_select.add(alias.lower())
            salida.append(alias)
        elif len(item) == 1 and item[0]["t"] == "id":
            salida.append(item[0]["partes"][-1])
        elif len(item) == 1 and item[0]["t"] == "op" and item[0]["valor"] == "*":
            salida.append("*")
        else:
            salida.append(f"(expresión {len(salida) + 1})")
    en_lista = {id(x) for x in bloque.lista_select}
    ids_alias = {id(x) for x in alias_tokens}

    for ref in bloque.refs[:len(bloque.refs) if bloque.descartar_desde is None else bloque.descartar_desde]:
        if id(ref["token"]) in ids_alias:
            continue
        # ORDER BY alias: fuera de la lista, un nombre igual a un alias del SELECT es el alias.
        n = ref["partes"][0].lower() if len(ref["partes"]) == 1 else None
        if n and id(ref["token"]) not in en_lista and (n in bloque.alias_select or n in (bloque.alias_heredados or ())):
            continue
        _resolver_ref(ref, bloque, padres, ctx)

    if bloque.tipo == "select" and profundidad == 0 and not bloque.into and not bloque.asigna_variable and not bloque.alimenta_insert and not bloque.union and salida:
        ctx.resultados.append(salida)


def _resolver_ref(ref: dict, bloque: _Bloque, padres: list, ctx: _Ctx) -> None:
    partes = ref["partes"]
    columna = partes[-1]
    if not columna or columna.startswith("@"):
        return
    if len(partes) == 1 and partes[0].lower() in ctx.ctes:
        return

    if len(partes) >= 2:
        calificador = partes[:-1]
        ultimo = calificador[-1].lower()
        for b in [bloque, *padres]:
            for f in b.fuentes:
                if (f.get("alias") and f["alias"].lower() == ultimo) or (
                        not f.get("alias") and f["partes"][-1].lower() == ultimo
                        and (len(calificador) == 1 or ".".join(f["partes"]).lower().endswith(".".join(calificador).lower()))):
                    if f["clase"] == "tabla":
                        _registrar_columna(ctx, f["partes"], columna, "exacta")
                    return
        # Calificador desconocido: si no es una CTE conocida, queda sin resolver.
        if ultimo not in ctx.ctes:
            _agregar_sin_resolver(ctx, ".".join(partes), [])
        return

    # Sin calificar.
    reales = [f for f in bloque.fuentes if f["clase"] != "variable"]
    if not reales:   # subconsulta sin FROM propio: puede ser columna del bloque externo
        externo = next((b for b in padres if b.fuentes), None)
        if externo and len(externo.fuentes) == 1 and externo.fuentes[0]["clase"] == "tabla":
            _registrar_columna(ctx, externo.fuentes[0]["partes"], columna, "inferida")
        return
    if len(reales) == 1:
        if reales[0]["clase"] == "tabla":
            _registrar_columna(ctx, reales[0]["partes"], columna, "inferida")
        return   # CTE, temporal o derivada: la columna no es de una tabla del diccionario
    candidatas = [_resolver_nombre_tabla(f["partes"], ctx.base, ctx.esquema)["completo"] for f in reales if f["clase"] == "tabla"]
    if candidatas:
        _agregar_sin_resolver(ctx, columna, candidatas)
