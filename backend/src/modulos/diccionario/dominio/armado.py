"""Arma el diccionario (la misma forma del `diccionario.json` del repo DICCIONARIO) con lo que SQL Server sabe de sí mismo.

Entradas, todas ya leídas de la base:
- el catálogo de reportes (`mod_rep.rep.RREGREP01`): qué SP ejecuta cada reporte;
- las dependencias que el motor tiene registradas por SP (`sys.dm_sql_referenced_entities` y `sys.sql_expression_dependencies`);
- los parámetros de cada SP (`sys.parameters`);
- la estructura real de las tablas que esos SP usan (`INFORMATION_SCHEMA`).

Límites del motor, que se heredan: no ve el SQL dinámico (`EXEC(@sql)`), ni las tablas temporales, ni las columnas de tablas de otra base
desde la dependencia en sí (esas se completan con la estructura). Esto es lo que el motor confirma; no inventa nada más.
Función pura: no toca la base ni el disco.
"""

from __future__ import annotations

from collections import defaultdict

_TIPO_TABLA = {"USER_TABLE": "tabla", "VIEW": "vista"}


def _verdadero(v: object) -> bool:
    return v is True or v == 1


def _clave(base: str, esquema: str, nombre: str) -> tuple[str, str, str]:
    return base.lower(), esquema.lower(), nombre.lower()


def _referencia(f: dict, base: str) -> tuple[str, str, str, str, str] | None:
    """(nombre completo, base, esquema, entidad, tipo de objeto) de lo que una fila del motor referencia; None si no es utilizable (sin entidad o de un servidor vinculado)."""
    ent = f.get("ref_entidad")
    if not ent or f.get("ref_servidor"):
        return None
    rbase, resq = f.get("ref_base") or base, f.get("ref_esquema") or "dbo"
    return f"{rbase}.{resq}.{ent}", rbase, resq, ent, str(f.get("ref_objeto_tipo") or "")


def tablas_referidas(dependencias: list[dict]) -> dict[str, set[tuple[str, str]]]:
    """Las tablas (esquema, nombre) que los SP usan, por base: lo que hay que pedirle a cada base para conocer su estructura."""
    por_base: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for f in dependencias:
        r = _referencia(f, f["sp_base"])
        if r and r[4] != "SQL_STORED_PROCEDURE" and "FUNCTION" not in r[4]:
            por_base[r[1].lower()].add((r[2], r[3]))   # STORAGE y storage son la misma base
    return dict(por_base)


def _partes(nombre: str) -> tuple[str, str, str] | None:
    p = nombre.split(".")
    return (p[0], p[1], p[2]) if len(p) == 3 and all(p) else None


def armar(reportes: list[dict], dependencias: list[dict], parametros: list[dict], estructura: list[dict], bases_con_sp: set[str], bases_con_estructura: set[str]) -> dict:
    """`bases_con_sp` y `bases_con_estructura` (en minúsculas) son las que se alcanzaron a consultar: sin ellas, la ausencia de un dato no prueba nada."""
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
    for r in reportes:
        if r.get("procedimiento"):
            por_sp[r["procedimiento"]].append(r["codigo"])

    hallazgos: list[dict] = []
    procedimientos: list[dict] = []
    usos_tabla: dict[tuple, dict] = {}   # tabla -> {"nombre", "tipo", "columnas": {columna: {procedimientos}}, "procs": set}

    for nombre, codigos in sorted(por_sp.items()):
        partes = _partes(nombre)
        if partes is None:
            procedimientos.append({"nombre": nombre, "base": nombre.split(".")[0], "esquema": "", "estado": "pendiente", "reportes": sorted(codigos),
                                   "parametros": None, "resultados": None, "invoca": [], "otrosObjetos": [], "tablas": []})
            continue
        base, esquema, sp = partes
        filas = deps.get(_clave(base, esquema, sp), [])
        existe = not any(f.get("origen") == "catalogo" for f in filas) if filas or base.lower() in bases_con_sp else None
        motor = [f for f in filas if f.get("origen") == "dm_sql_referenced_entities"]
        error_motor = next((f["error"] for f in motor if f.get("error")), None)
        if existe is False:
            estado = "pendiente"
            hallazgos.append({"nivel": "error", "regla": "sp-inexistente", "origen": "produccion", "objeto": nombre,
                              "detalle": f"lo ejecutan {', '.join(sorted(codigos))} (o la cuenta de lectura no lo ve)", "enLineaBase": False})
        elif existe is None:
            estado = "pendiente"          # su base no se alcanzó a consultar
        elif motor and not error_motor:
            estado = "validado"
        else:
            estado = "extraido"
            if error_motor:
                hallazgos.append({"nivel": "aviso", "regla": "motor-sin-columnas", "origen": "analisis", "objeto": nombre, "detalle": str(error_motor)[:200], "enLineaBase": False})

        invoca: list[str] = []
        otros: list[str] = []
        tablas: dict[tuple, dict] = {}
        for f in filas:
            ref = _referencia(f, base)
            if ref is None:                                # fila de error o servidor vinculado: fuera de alcance
                continue
            completo, rbase, resq, ent, tipo = ref
            if tipo == "SQL_STORED_PROCEDURE":
                invoca.append(completo)
                continue
            if "FUNCTION" in tipo:
                otros.append(completo)
                continue
            t = tablas.setdefault(_clave(rbase, resq, ent), {"nombre": completo, "usos": set(), "columnas": {}, "fuentes": set(), "tipo": _TIPO_TABLA.get(tipo)})
            t["fuentes"].add("motor")
            if f.get("origen") == "dm_sql_referenced_entities":
                if _verdadero(f.get("es_lectura")) or _verdadero(f.get("es_select_todo")):
                    t["usos"].add("lee")
                if _verdadero(f.get("es_escritura")):
                    t["usos"].add("escribe")
                if f.get("ref_columna"):
                    t["columnas"][f["ref_columna"]] = "motor"
            elif not t["usos"]:
                t["usos"].add("lee")   # dependencia a nivel tabla (p. ej. de otra base): al menos dice que la nombra

        uso_sp = []
        for k, t in sorted(tablas.items()):
            g = usos_tabla.setdefault(k, {"nombre": t["nombre"], "tipo": t["tipo"], "columnas": {}})
            g["tipo"] = g["tipo"] or t["tipo"]
            for c in t["columnas"]:
                g["columnas"].setdefault(c, set()).add(nombre)
            g.setdefault("procs", set()).add(nombre)
            uso_sp.append({"nombre": t["nombre"], "usos": sorted(t["usos"]) or ["lee"], "fuentes": sorted(t["fuentes"]),
                           "columnas": [{"nombre": c, "confianza": "motor"} for c in sorted(t["columnas"], key=str.lower)]})
        procedimientos.append({
            "nombre": nombre, "base": base, "esquema": esquema, "estado": estado, "reportes": sorted(codigos),
            "parametros": [{"nombre": p["nombre"], "tipo": p.get("tipo"), "porDefecto": "" if _verdadero(p.get("tiene_defecto")) else None, "salida": _verdadero(p.get("salida"))}
                           for p in sorted(pars.get(_clave(base, esquema, sp), []), key=lambda p: p.get("orden", 0))] or None,
            "resultados": None, "invoca": sorted(set(invoca)), "otrosObjetos": sorted(set(otros)), "tablas": uso_sp})

    tablas_out: list[dict] = []
    for k, g in sorted(usos_tabla.items()):
        base = k[0]
        reales = cols_reales.get(k, {})
        consultada = base in bases_con_estructura
        existe = True if reales else (False if consultada else None)
        if existe is False and g["tipo"] is None:
            # Sin tipo: el motor no resolvió el objeto (otra base, sinónimo, procedimiento remoto o tabla que no existe). No se afirma que falte.
            existe = None
            hallazgos.append({"nivel": "aviso", "regla": "objeto-no-resuelto", "origen": "analisis", "objeto": g["nombre"],
                              "detalle": f"lo usa {', '.join(sorted(g['procs']))}; no es una tabla visible: puede no existir, ser un procedimiento o sinónimo de otra base, o la cuenta no lo ve", "enLineaBase": False})
        elif existe is False:
            hallazgos.append({"nivel": "error", "regla": "tabla-inexistente", "origen": "produccion", "objeto": g["nombre"],
                              "detalle": f"la usa {', '.join(sorted(g['procs']))} (o la cuenta de lectura no la ve)", "enLineaBase": False})
        columnas = []
        for c, procs in sorted(g["columnas"].items(), key=lambda x: x[0].lower()):
            real = reales.get(c.lower())
            if reales and real is None:
                hallazgos.append({"nivel": "error", "regla": "columna-inexistente", "origen": "produccion", "objeto": f"{g['nombre']}.{c}",
                                  "detalle": f"la usa {', '.join(sorted(procs))}", "enLineaBase": False})
            columnas.append({"nombre": c, "tipo": real.get("tipo") if real else None, "aceptaNulos": (str(real.get("acepta_nulos")).upper() == "YES") if real else None,
                             "existe": True if real else (False if reales else None), "confianza": "exacta" if real else "motor", "descripcion": None, "procedimientos": sorted(procs)})
        nombre_real = g["nombre"].split(".")
        tablas_out.append({"nombre": g["nombre"], "base": nombre_real[0], "esquema": nombre_real[1], "tabla": nombre_real[2], "tipo": g["tipo"] or tipo_objeto.get(k),
                           "existe": existe, "columnasReales": len(reales) if reales else None, "descripcion": None, "ficha": None, "columnas": columnas})

    return {
        "nota": "Generado desde la base (mod_rep.rep.RREGREP01 y los metadatos de SQL Server); no editar: se vuelve a generar.",
        "resumen": {"reportes": len(reportes), "procedimientos": len(procedimientos), "extraidos": sum(p["estado"] in ("extraido", "validado") for p in procedimientos),
                    "validados": sum(p["estado"] == "validado" for p in procedimientos), "tablas": len(tablas_out)},
        "reportes": [{"codigo": r["codigo"], "descripcion": r.get("descripcion") or "", "procedimiento": r.get("procedimiento") or "", "parametros": r.get("parametros") or [], "front": []}
                     for r in reportes],
        "procedimientos": procedimientos, "tablas": tablas_out, "hallazgos": hallazgos,
    }
