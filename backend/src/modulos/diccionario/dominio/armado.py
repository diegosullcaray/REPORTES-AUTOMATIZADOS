"""Arma el diccionario con lo que SQL Server sabe de sí mismo y con el análisis estático del código de cada procedimiento.

Entradas, todas ya leídas de la base:
- el catálogo de reportes (`mod_rep.rep.RREGREP01`): qué SP ejecuta cada reporte;
- las dependencias que el motor tiene registradas por SP (`sys.dm_sql_referenced_entities` y `sys.sql_expression_dependencies`);
- los parámetros de cada SP (`sys.parameters`);
- la estructura real de las tablas que esos SP usan (`INFORMATION_SCHEMA`);
- el análisis estático del texto de cada SP (`tsql.analizar_procedimiento`), que cubre donde el motor no llega: SQL que no compila contra el esquema actual,
  columnas sin calificar, columnas que devuelve, SQL dinámico y la firma exacta de los parámetros.

El motor manda; el análisis lo complementa. Una columna vista por los dos queda `confirmada`. Límites que se heredan: ninguno de los dos ve el SQL dinámico
(`EXEC(@sql)`) ni las tablas de un servidor vinculado. Función pura: no toca la base ni el disco.
"""

from __future__ import annotations

import re
from collections import defaultdict

from modulos.diccionario.dominio import tsql

_NIVEL_ORIGEN = {
    "sp-inexistente": ("error", "produccion"), "tabla-inexistente": ("error", "produccion"), "columna-inexistente": ("error", "produccion"),
    "parametros-de-mas": ("error", "produccion"), "parametros-faltantes": ("error", "produccion"),
    "motor-con-error": ("aviso", "produccion"), "esquema-distinto": ("aviso", "produccion"),
    "sql-dinamico": ("aviso", "analisis"), "columna-sin-resolver": ("aviso", "analisis"), "columna-inferida-inexistente": ("aviso", "analisis"),
    "discrepancia-motor": ("aviso", "analisis"), "tabla-de-trabajo": ("info", "analisis"), "parametro-nombre-distinto": ("info", "analisis"),
    "analisis-aproximado": ("info", "analisis"), "varios-resultados": ("info", "analisis"),
}
_ORDEN_NIVEL = {"error": 0, "aviso": 1, "info": 2}
_TIPO_TABLA = {"USER_TABLE": "tabla", "VIEW": "vista"}


def _verdadero(v: object) -> bool:
    return v is True or v == 1


def _clave(base: str, esquema: str, nombre: str) -> tuple[str, str, str]:
    return base.lower(), esquema.lower(), nombre.lower()


def _norm(p: object) -> str:
    return re.sub(r"^@", "", str(p or "")).lower()


def _referencia(f: dict, base: str) -> tuple[str, str, str, str, str] | None:
    """(nombre completo, base, esquema, entidad, tipo de objeto) de lo que una fila del motor referencia; None si no es utilizable (sin entidad o de un servidor vinculado)."""
    ent = f.get("ref_entidad")
    if not ent or f.get("ref_servidor"):
        return None
    rbase, resq = f.get("ref_base") or base, f.get("ref_esquema") or "dbo"
    return f"{rbase}.{resq}.{ent}", rbase, resq, ent, str(f.get("ref_objeto_tipo") or "")


def _partes(nombre: str) -> tuple[str, str, str] | None:
    p = nombre.split(".")
    return (p[0], p[1], p[2]) if len(p) == 3 and all(p) else None


def _canonico(reportes: list[dict], dependencias: list[dict], estructura: list[dict], analisis: dict[tuple, dict]):
    """Devuelve `nombre(base, esquema, objeto)` con la grafía canónica de cada parte.

    El código de un SP puede escribir `STORAGE.com_act.hdgp001` y el catálogo `storage`: SQL Server no distingue mayúsculas, pero el diccionario sí
    mostraría tres tablas. Manda la grafía real que devuelve la base (`DB_NAME()`, `INFORMATION_SCHEMA`); si no hay, la más repetida.
    """
    cuentas: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def contar(clave: tuple, grafia: str | None, peso: int = 1) -> None:
        if grafia:
            cuentas[clave][grafia] += peso

    for e in estructura:   # lo que dice la propia base pesa más que cualquier texto
        contar((e["base"].lower(),), e["base"], 1000)
        contar((e["base"].lower(), e["esquema"].lower()), e["esquema"], 1000)
        contar((e["base"].lower(), e["esquema"].lower(), e["tabla"].lower()), e["tabla"], 1000)
    for d in dependencias:
        contar((d["sp_base"].lower(),), d["sp_base"], 1000)   # DB_NAME() de la base donde vive el SP
        r = _referencia(d, d["sp_base"])
        if r:
            contar((r[1].lower(),), r[1])
            contar((r[1].lower(), r[2].lower()), r[2])
            contar((r[1].lower(), r[2].lower(), r[3].lower()), r[3])
    for r in reportes:
        partes = _partes(r.get("procedimiento") or "")
        if partes:
            contar((partes[0].lower(),), partes[0])
            contar((partes[0].lower(), partes[1].lower()), partes[1])
    for a in analisis.values():
        for t in a["tablas"]:
            if t["base"] and not t["servidor"]:
                contar((t["base"].lower(),), t["base"])
                if not t["esquemaImplicito"]:
                    contar((t["base"].lower(), t["esquema"].lower()), t["esquema"])
                    contar((t["base"].lower(), t["esquema"].lower(), t["nombre"].lower()), t["nombre"])

    def mejor(clave: tuple, por_defecto: str) -> str:
        c = cuentas.get(clave)
        return max(c, key=lambda g: (c[g], g)) if c else por_defecto

    def nombre(base: str, esquema: str, objeto: str) -> tuple[str, str, str]:
        b = mejor((base.lower(),), base)
        e = mejor((base.lower(), esquema.lower()), esquema)
        return b, e, mejor((base.lower(), esquema.lower(), objeto.lower()), objeto)

    return nombre


def analizar(cuerpos: dict[tuple[str, str, str], str]) -> dict[tuple, dict]:
    """Análisis estático de cada procedimiento: `{(base, esquema, sp): texto}` -> `{clave en minúsculas: análisis}`."""
    return {_clave(*k): tsql.analizar_procedimiento(texto, base=k[0], esquema=k[1]) for k, texto in cuerpos.items()}


def tablas_referidas(dependencias: list[dict], analisis: dict[tuple, dict] | None = None) -> dict[str, set[tuple[str, str]]]:
    """Las tablas (esquema, nombre) que los SP usan, por base: lo que hay que pedirle a cada base para conocer su estructura.

    Un nombre sin esquema (`FROM TABLA`) se pide también en `dbo`: SQL Server lo busca ahí si no está en el esquema del SP.
    """
    por_base: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for f in dependencias:
        r = _referencia(f, f["sp_base"])
        if r and r[4] != "SQL_STORED_PROCEDURE" and "FUNCTION" not in r[4]:
            por_base[r[1].lower()].add((r[2], r[3]))   # STORAGE y storage son la misma base
    for a in (analisis or {}).values():
        for t in a["tablas"]:
            if t["base"] and not t["servidor"]:
                por_base[t["base"].lower()].add((t["esquema"], t["nombre"]))
                if t["esquemaImplicito"]:
                    por_base[t["base"].lower()].add(("dbo", t["nombre"]))
    return dict(por_base)


def _confianza(fuentes: set[str]) -> str:
    if "motor" in fuentes and len(fuentes) > 1:
        return "confirmada"
    if "motor" in fuentes:
        return "motor"
    if "exacta" in fuentes:
        return "exacta"
    if "estructura" in fuentes:
        return "estructura"
    return "inferida"


def _revisar_a(a: dict, nombre: str, esquema: str, codigos: list[str], params_de: dict[str, list[str]], hallazgo) -> None:
    """Lo que el análisis del código dice del SP: esquema, firma contra lo que envía el catálogo, SQL dinámico y resultados."""
    decl = a["procedimiento"] or {}
    if decl.get("esquema") and decl["esquema"].lower() != esquema.lower():
        hallazgo("esquema-distinto", nombre, f"el CREATE declara el esquema {decl['esquema']}")
    firma = decl.get("parametros") or []
    for codigo in sorted(codigos) if a["procedimiento"] else []:   # sin CREATE no se conoce la firma
        enviados = params_de.get(codigo, [])
        if len(enviados) > len(firma):
            hallazgo("parametros-de-mas", codigo, f"el catálogo envía {len(enviados)} y {nombre} declara {len(firma)}")
            continue
        obligatorios = sum(1 for p in firma if p["porDefecto"] is None and not p["salida"])
        if len(enviados) < obligatorios:
            hallazgo("parametros-faltantes", codigo, f"el catálogo envía {len(enviados)} y {nombre} exige {obligatorios} sin valor por defecto")
        for i, p in enumerate(enviados):
            if i < len(firma) and _norm(firma[i]["nombre"]) != _norm(p):
                hallazgo("parametro-nombre-distinto", codigo, f"posición {i + 1}: `{p}` en el catálogo, `{firma[i]['nombre']}` en el SP")
    if a["sql_dinamico"]:
        hallazgo("sql-dinamico", nombre, "revisar a mano las tablas del texto dinámico")
    for adv in a["advertencias"]:
        hallazgo("analisis-aproximado", nombre, adv)
    if len(a["resultados"]) > 1:
        hallazgo("varios-resultados", nombre, f"devuelve {len(a['resultados'])} conjuntos de resultados")


def _tablas_finales(usos_tabla: dict, cols_reales: dict, tipo_objeto: dict, bases_con_estructura: set[str], hallazgo) -> list[dict]:
    """Cada tabla usada contra la estructura real de su base: existencia, tipos y columnas que no están."""
    # Tabla de trabajo: algún SP la crea o la borra en cada ejecución, así que no se exige que exista.
    trabajo = {(k[0], k[2]) for k, g in usos_tabla.items() if g["usos"] & {"crea", "elimina-objeto"}}

    tablas_out: list[dict] = []
    for k, g in sorted(usos_tabla.items()):
        reales = cols_reales.get(k, {})
        existe = True if reales else (False if k[0] in bases_con_estructura else None)
        if existe is False:
            if (k[0], k[2]) in trabajo:
                hallazgo("tabla-de-trabajo", g["nombre"], f"la crea y borra {', '.join(sorted(g['procs']))}")
            else:
                hallazgo("tabla-inexistente", g["nombre"], f"la usa {', '.join(sorted(g['procs']))} (o la cuenta de lectura no la ve)")
        columnas = []
        for kc, c in sorted(g["columnas"].items()):
            real = reales.get(kc)
            if reales and real is None and c["nombre"] != "*":
                calificada = bool(c["fuentes"] & {"exacta", "motor"})
                hallazgo("columna-inexistente" if calificada else "columna-inferida-inexistente", f"{g['nombre']}.{c['nombre']}", f"la usa {', '.join(sorted(c['procs']))}")
            columnas.append({"nombre": c["nombre"], "tipo": real.get("tipo") if real else None, "aceptaNulos": (str(real.get("acepta_nulos")).upper() == "YES") if real else None,
                             "existe": True if real else (False if reales else None), "confianza": _confianza(c["fuentes"]), "descripcion": None, "procedimientos": sorted(c["procs"])})
        nombre_real = g["nombre"].split(".")
        tablas_out.append({"nombre": g["nombre"], "base": nombre_real[0], "esquema": nombre_real[1], "tabla": nombre_real[2], "tipo": g["tipo"] or tipo_objeto.get(k),
                           "existe": existe, "columnasReales": len(reales) if reales else None, "descripcion": None, "ficha": None, "columnas": columnas})
    return tablas_out


def armar(reportes: list[dict], dependencias: list[dict], parametros: list[dict], estructura: list[dict], bases_con_sp: set[str], bases_con_estructura: set[str],
          analisis: dict[tuple, dict] | None = None) -> dict:
    """`bases_con_sp` y `bases_con_estructura` (en minúsculas) son las que se alcanzaron a consultar: sin ellas, la ausencia de un dato no prueba nada."""
    analisis = analisis or {}
    canon = _canonico(reportes, dependencias, estructura, analisis)
    deps: dict[tuple, list[dict]] = defaultdict(list)
    for d in dependencias:
        deps[_clave(d["sp_base"], d["sp_esquema"], d["sp_nombre"])].append(d)
    pars: dict[tuple, list[dict]] = defaultdict(list)
    for p in parametros:
        pars[_clave(p["base"], p["esquema"], p["sp"])].append(p)
    cols_reales: dict[tuple, dict[str, dict]] = defaultdict(dict)   # (base, esquema, tabla) -> columna en minúsculas -> fila
    tipo_objeto: dict[tuple, str] = {}
    for e in estructura:
        k = _clave(e["base"], e["esquema"], e["tabla"])
        cols_reales[k][str(e["columna"]).lower()] = e
        tipo_objeto[k] = "vista" if str(e.get("tipo_objeto", "")).upper() == "VIEW" else "tabla"

    por_sp: dict[str, list[str]] = defaultdict(list)
    params_de: dict[str, list[str]] = {}
    for r in reportes:
        if r.get("procedimiento"):
            por_sp[r["procedimiento"]].append(r["codigo"])
            params_de[r["codigo"]] = [str(x) for x in r.get("parametros") or []]

    hallazgos: list[dict] = []

    def hallazgo(regla: str, objeto: str, detalle: str) -> None:
        nivel, origen = _NIVEL_ORIGEN[regla]
        hallazgos.append({"nivel": nivel, "regla": regla, "origen": origen, "objeto": objeto, "detalle": detalle})

    procedimientos: list[dict] = []
    usos_tabla: dict[tuple, dict] = {}        # tabla -> {nombre, tipo, columnas: {minúsculas: {nombre, fuentes, procs}}, procs, usos}
    sin_resolver: list[tuple[str, dict]] = []  # (SP, columna sin calificar con varias tablas posibles): se resuelve al conocer la estructura

    for nombre, codigos in sorted(por_sp.items()):
        partes = _partes(nombre)
        if partes is None:
            procedimientos.append({"nombre": nombre, "base": nombre.split(".")[0], "esquema": "", "estado": "pendiente", "reportes": sorted(codigos),
                                   "parametros": None, "resultados": None, "invoca": [], "otrosObjetos": [], "tablas": []})
            continue
        base, esquema, sp = partes
        filas = deps.get(_clave(base, esquema, sp), [])
        a = analisis.get(_clave(base, esquema, sp))
        existe = not any(f.get("origen") == "catalogo" for f in filas) if filas or base.lower() in bases_con_sp else None
        motor = [f for f in filas if f.get("origen") == "dm_sql_referenced_entities"]
        error_motor = next((f["error"] for f in motor if f.get("error")), None)
        if existe is False:
            estado = "pendiente"
            hallazgo("sp-inexistente", nombre, f"lo ejecutan {', '.join(sorted(codigos))} (o la cuenta de lectura no lo ve)")
        elif existe is None:
            estado = "pendiente"          # su base no se alcanzó a consultar
        elif motor and not error_motor:
            estado = "validado"
        else:
            estado = "extraido"
        if error_motor and existe:
            hallazgo("motor-con-error", nombre, str(error_motor)[:200])

        invocados = {i["nombre"].lower().split(".")[-1] for i in (a or {}).get("invocaciones", [])}
        invoca: set[str] = set()
        otros: set[str] = set()
        tablas: dict[tuple, dict] = {}

        def tomar(clave: tuple, completo: str, tipo: str | None, implicito: bool) -> dict:
            return tablas.setdefault(clave, {"nombre": completo, "usos": set(), "columnas": {}, "fuentes": set(), "tipo": tipo, "implicito": implicito})  # noqa: B023

        # 1. Análisis estático. Un nombre sin esquema se resuelve al del SP, o a dbo si la estructura real la tiene ahí.
        estaticas = a["tablas"] if a else []
        for t in estaticas:
            if t["servidor"] or not t["base"]:
                continue
            esq = t["esquema"]
            if t["esquemaImplicito"]:
                gemela = next((x for x in estaticas if not x["esquemaImplicito"] and (x["base"] or "").lower() == t["base"].lower() and x["nombre"].lower() == t["nombre"].lower()), None)
                real = next((e for e in (t["esquema"], "dbo") if _clave(t["base"], e, t["nombre"]) in cols_reales), None)
                esq = gemela["esquema"] if gemela else (real or esq)
            d = tomar(_clave(t["base"], esq, t["nombre"]), ".".join(canon(t["base"], esq, t["nombre"])), None, t["esquemaImplicito"])
            d["fuentes"].add("estatico")
            d["usos"].update(t["usos"])
            for c in t["columnas"]:
                d["columnas"].setdefault(c["nombre"].lower(), {"nombre": c["nombre"], "fuentes": set()})["fuentes"].add(c["confianza"])

        # 2. Motor. Lo que no es tabla (SP, función, sinónimo) va a `otrosObjetos`. Si el motor no dice el tipo (otra base), es tabla si la estructura real la tiene.
        for f in filas:
            ref = _referencia(f, base)
            if ref is None:                                # fila de error o servidor vinculado: fuera de alcance
                continue
            _, rbase, resq, ent, tipo = ref
            completo = ".".join(canon(rbase, resq, ent))
            k = _clave(rbase, resq, ent)
            if tipo == "SQL_STORED_PROCEDURE" or (ent.lower() in invocados and k not in tablas):
                invoca.add(completo)
                continue
            if "FUNCTION" in tipo:
                otros.add(completo)
                continue
            gemela = k if k in tablas else next((c for c, x in tablas.items() if x["implicito"] and c[0] == k[0] and c[2] == k[2]), None)
            if gemela is None and not (tipo in _TIPO_TABLA or (not tipo and (rbase.lower() not in bases_con_estructura or k in cols_reales))):
                otros.add(completo)
                continue
            t = tablas[gemela] if gemela else tomar(k, completo, None, False)
            t["tipo"] = t["tipo"] or _TIPO_TABLA.get(tipo)
            t["fuentes"].add("motor")
            if f.get("origen") == "dm_sql_referenced_entities":
                if _verdadero(f.get("es_lectura")) or _verdadero(f.get("es_select_todo")):
                    t["usos"].add("lee")
                if _verdadero(f.get("es_escritura")):
                    t["usos"].add("escribe")
                if f.get("ref_columna"):
                    t["columnas"].setdefault(f["ref_columna"].lower(), {"nombre": f["ref_columna"], "fuentes": set()})["fuentes"].add("motor")
            elif not t["usos"]:
                t["usos"].add("lee")   # dependencia a nivel tabla (p. ej. de otra base): al menos dice que la nombra

        if a:
            sin_resolver.extend((nombre, s) for s in a["sin_resolver"])
        for t in tablas.values():
            t["usos"] = t["usos"] or {"lee"}
        if estado == "validado":
            for k, t in tablas.items():
                if t["fuentes"] == {"estatico"} and k[0] == base.lower() and not (t["usos"] & {"crea", "elimina-objeto"}):
                    hallazgo("discrepancia-motor", nombre, f"{t['nombre']} aparece en el análisis y no en el motor")

        if a:
            _revisar_a(a, nombre, esquema, codigos, params_de, hallazgo)

        uso_sp = []
        for k, t in sorted(tablas.items()):
            g = usos_tabla.setdefault(k, {"nombre": t["nombre"], "tipo": t["tipo"], "columnas": {}, "procs": set(), "usos": set()})
            g["tipo"] = g["tipo"] or t["tipo"]
            g["procs"].add(nombre)
            g["usos"] |= t["usos"]
            for kc, c in t["columnas"].items():
                gc = g["columnas"].setdefault(kc, {"nombre": c["nombre"], "fuentes": set(), "procs": set()})
                gc["fuentes"] |= c["fuentes"]
                gc["procs"].add(nombre)
            uso_sp.append({"nombre": t["nombre"], "usos": sorted(t["usos"]), "fuentes": sorted(t["fuentes"]),
                           "columnas": [{"nombre": c["nombre"], "confianza": _confianza(c["fuentes"])} for c in sorted(t["columnas"].values(), key=lambda c: c["nombre"].lower())]})
        declarados = ((a or {}).get("procedimiento") or {}).get("parametros") or []
        por_defecto = {_norm(p["nombre"]): p["porDefecto"] for p in declarados}
        del_motor = sorted(pars.get(_clave(base, esquema, sp), []), key=lambda p: p.get("orden", 0))
        if del_motor:   # el motor da el tipo exacto; el análisis, el valor por defecto
            lista_params = [{"nombre": p["nombre"], "tipo": p.get("tipo"),
                             "porDefecto": por_defecto[_norm(p["nombre"])] if por_defecto.get(_norm(p["nombre"])) is not None else ("" if _verdadero(p.get("tiene_defecto")) else None),
                             "salida": _verdadero(p.get("salida"))} for p in del_motor]
        else:
            lista_params = [{"nombre": p["nombre"], "tipo": p["tipo"], "porDefecto": p["porDefecto"], "salida": p["salida"]} for p in declarados]
        procedimientos.append({
            "nombre": nombre, "base": canon(base, esquema, sp)[0], "esquema": canon(base, esquema, sp)[1], "estado": estado, "reportes": sorted(codigos),
            "parametros": lista_params or None, "resultados": (a or {}).get("resultados") or None,
            "invoca": sorted(invoca), "otrosObjetos": sorted(otros), "tablas": uso_sp})

    # Columna sin calificar con varias tablas posibles: si una sola de las que tienen estructura la tiene, es de esa. Si ninguna la tiene es un alias, una columna
    # de CTE/derivada o de una tabla que no existe (ya reportada): no es un hallazgo aparte.
    for nombre, s in sin_resolver:
        claves = [_clave(*c.split(".")[-3:]) if len(c.split(".")) >= 3 else None for c in s["candidatas"]]
        con_estructura = [k for k in claves if k in cols_reales]
        tienen = [k for k in con_estructura if s["columna"].lower() in cols_reales[k]]
        if len(tienen) == 1 and tienen[0] in usos_tabla:
            gc = usos_tabla[tienen[0]]["columnas"].setdefault(s["columna"].lower(), {"nombre": s["columna"], "fuentes": set(), "procs": set()})
            gc["fuentes"].add("estructura")
            gc["procs"].add(nombre)
            continue
        inexistentes = [k for k in claves if k and k not in cols_reales and k[0] in bases_con_estructura]
        if not tienen and len(con_estructura) + len(inexistentes) == len(s["candidatas"]):
            continue
        hallazgo("columna-sin-resolver", nombre, f"`{s['columna']}`" + (f" podría ser de {' o '.join(s['candidatas'])}" if s["candidatas"] else ""))

    tablas_out = _tablas_finales(usos_tabla, cols_reales, tipo_objeto, bases_con_estructura, hallazgo)

    hallazgos.sort(key=lambda h: (_ORDEN_NIVEL[h["nivel"]], h["regla"], h["objeto"]))
    return {
        "nota": "Generado desde la base (mod_rep.rep.RREGREP01, los metadatos de SQL Server y el análisis del código de cada SP); no editar: se vuelve a generar.",
        "resumen": {"reportes": len(reportes), "procedimientos": len(procedimientos), "extraidos": sum(p["estado"] in ("extraido", "validado") for p in procedimientos),
                    "validados": sum(p["estado"] == "validado" for p in procedimientos), "tablas": len(tablas_out)},
        "reportes": [{"codigo": r["codigo"], "descripcion": r.get("descripcion") or "", "procedimiento": r.get("procedimiento") or "", "parametros": r.get("parametros") or []}
                     for r in reportes],
        "procedimientos": procedimientos, "tablas": tablas_out, "hallazgos": hallazgos,
    }
