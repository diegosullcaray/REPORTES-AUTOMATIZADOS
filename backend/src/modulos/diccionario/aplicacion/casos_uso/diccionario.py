"""Consultas al diccionario de datos de los reportes MIS: resumen, reportes, tablas, calidad y lo que aporta a los reportes propios."""

from __future__ import annotations

import re

from core.excepciones import NoEncontrado
from core.servidores import servidor_de_base
from modulos.diccionario.aplicacion import dto
from modulos.diccionario.aplicacion.puertos import puertos
from modulos.diccionario.dominio.columnas import es_columna_fecha
from modulos.reportes.dominio.tablas import TABLAS, USO
from modulos.reportes.dominio.verificacion import causa_de

_EXTRAIDO = {"extraido", "validado"}


def _guardado() -> dict | None:
    """El diccionario ya generado desde la base, o None si todavía no hay."""
    try:
        return puertos().lector.leer()
    except NoEncontrado:
        return None


def _catalogo() -> tuple[list[dict], dto.OrigenCatalogo]:
    """Los reportes del MIS: los de `mod_rep.rep.RREGREP01` (en vivo) o, sin conexión, los del diccionario guardado."""
    en_json = (_guardado() or {}).get("reportes", [])
    try:
        filas = puertos().catalogo.leer()
    except Exception as exc:  # noqa: BLE001 - sin VPN, sin permisos o tabla cambiada: se sigue con el diccionario guardado y se dice por qué
        if not en_json:
            raise NoEncontrado(f"No hay diccionario guardado y no pude leer el catálogo: {causa_de(exc, servidor_de_base('mod_rep'))[0]}") from exc
        return en_json, dto.OrigenCatalogo(fuente="diccionario guardado", motivo=causa_de(exc, servidor_de_base("mod_rep"))[0], nuevos=[], retirados=[])
    guardados = {r["codigo"] for r in en_json}
    codigos = {f["codigo"] for f in filas}
    return filas, dto.OrigenCatalogo(fuente=puertos().catalogo.FUENTE, motivo=None, nuevos=sorted(codigos - guardados) if guardados else [], retirados=sorted(guardados - codigos))


def _datos() -> dict:
    """Catálogo en vivo + lo guardado; sin diccionario guardado quedan solo los reportes (sin tablas, columnas ni hallazgos)."""
    return {"procedimientos": [], "tablas": [], "hallazgos": [], **(_guardado() or {}), "reportes": _catalogo()[0]}


def _hallazgo(h: dict) -> dto.Hallazgo:
    return dto.Hallazgo(nivel=h["nivel"], regla=h["regla"], origen=h["origen"], objeto=h["objeto"], detalle=h.get("detalle") or "")


def resumen() -> dto.Resumen:
    d = _datos()
    sps, bases = d["procedimientos"], {}
    for p in sps:
        b = bases.setdefault(p["base"], {"sp": 0, "ext": 0, "val": 0, "tablas": set()})
        b["sp"] += 1
        b["ext"] += p["estado"] in _EXTRAIDO
        b["val"] += p["estado"] == "validado"
        b["tablas"].update(t["nombre"].lower() for t in p.get("tablas") or [])
    hallazgos_ = d["hallazgos"]
    return dto.Resumen(
        reportes=len(d["reportes"]), procedimientos=len(sps), extraidos=sum(b["ext"] for b in bases.values()), validados=sum(b["val"] for b in bases.values()),
        tablas=len(d["tablas"]), columnas=sum(len(t["columnas"]) for t in d["tablas"]),
        errores=sum(h["nivel"] == "error" for h in hallazgos_), avisos=sum(h["nivel"] == "aviso" for h in hallazgos_),
        catalogo=_catalogo()[1], datos=dto.DatosDiccionario(generado=puertos().lector.origen()),
        bases=[dto.BaseResumen(base=n, procedimientos=b["sp"], extraidos=b["ext"], validados=b["val"], tablas=len(b["tablas"])) for n, b in sorted(bases.items())],
    )


def hallazgos() -> list[dto.Hallazgo]:
    orden = {"error": 0, "aviso": 1}
    return sorted((_hallazgo(h) for h in _datos()["hallazgos"]), key=lambda h: (orden.get(h.nivel, 2), h.regla, h.objeto))


# ---------------------------------------------------------------- reportes

def _fila(r: dict, sp: dict | None) -> dto.ReporteFila:
    return dto.ReporteFila(
        codigo=r["codigo"], descripcion=r.get("descripcion") or "", procedimiento=r.get("procedimiento") or "", base=sp["base"] if sp else "",
        estado=sp["estado"] if sp else ("sin extraer" if r.get("procedimiento") else "sin procedimiento"), parametros=len(r.get("parametros") or []), tablas=len(sp.get("tablas") or []) if sp else 0)


def _procedimientos_por_base(d: dict) -> dict[str, list[dto.ProcedimientoFila]]:
    """Cada procedimiento en la base donde vive; los que el catálogo nombra y el diccionario aún no tiene van en la base de su nombre, como «sin extraer»."""
    sps = {p["nombre"]: p for p in d["procedimientos"]}
    por_reporte: dict[str, set[str]] = {}
    for r in d["reportes"]:
        if r.get("procedimiento"):
            por_reporte.setdefault(r["procedimiento"], set()).add(r["codigo"])
    por_base: dict[str, list[dto.ProcedimientoFila]] = {}
    for n in sorted(sps.keys() | por_reporte.keys()):
        sp = sps.get(n)
        fila = dto.ProcedimientoFila(
            nombre=n, estado=sp["estado"] if sp else "sin extraer", reportes=sorted(por_reporte.get(n, set()) | set((sp or {}).get("reportes") or [])),
            parametros=len((sp or {}).get("parametros") or []), tablas=len((sp or {}).get("tablas") or []))
        por_base.setdefault(sp["base"] if sp else n.split(".")[0], []).append(fila)
    return por_base


def _usadas(d: dict, base: str) -> dict[str, int]:
    """Tablas (nombre en minúsculas) que usan los procedimientos de la base y cuántos de ellos las usan."""
    uso: dict[str, int] = {}
    for p in d["procedimientos"]:
        if p["base"] == base:
            for t in {t["nombre"].lower() for t in p.get("tablas") or []}:
                uso[t] = uso.get(t, 0) + 1
    return uso


def bases() -> list[dto.BaseFila]:
    d = _datos()
    procs, propias = _procedimientos_por_base(d), {}
    for t in d["tablas"]:
        propias[t["base"]] = propias.get(t["base"], 0) + 1
    return sorted((
        dto.BaseFila(base=b, procedimientos=len(procs.get(b, [])), validados=sum(p.estado == "validado" for p in procs.get(b, [])),
                     reportes=len({r for p in procs.get(b, []) for r in p.reportes}), tablas_propias=propias.get(b, 0), tablas_usadas=len(_usadas(d, b)))
        for b in procs.keys() | propias.keys()), key=lambda x: (-(x.procedimientos + x.tablas_propias), x.base))


def base(nombre: str) -> dto.BaseDetalle:
    """Las dos secciones de una base: sus procedimientos y las tablas que ocupa (las que viven en ella y las que usan sus procedimientos)."""
    d = _datos()
    b = next((x for x in {*_procedimientos_por_base(d), *(t["base"] for t in d["tablas"])} if x.lower() == nombre.lower()), None)
    if b is None:
        raise NoEncontrado(f"No existe la base «{nombre}» en el diccionario.")
    usadas = _usadas(d, b)
    filas = [dto.TablaDeBase(nombre=t["nombre"], base=t["base"], tipo=t.get("tipo"), existe=t.get("existe"), columnas=len(t["columnas"]), propia=t["base"] == b,
                             usada_por=usadas.get(t["nombre"].lower(), 0), en_registro=t["nombre"].lower() in TABLAS)
             for t in d["tablas"] if t["base"] == b or t["nombre"].lower() in usadas]
    return dto.BaseDetalle(base=b, procedimientos=_procedimientos_por_base(d).get(b, []), tablas=sorted(filas, key=lambda t: (-t.usada_por, t.nombre)))


def _procedimiento(p: dict) -> dto.Procedimiento:
    return dto.Procedimiento(
        nombre=p["nombre"], base=p["base"], estado=p["estado"],
        parametros=[dto.ParametroSP(nombre=x["nombre"], tipo=x.get("tipo"), por_defecto=x.get("porDefecto"), salida=bool(x.get("salida"))) for x in p.get("parametros") or []],
        resultados=[[str(c) for c in rs] for rs in p.get("resultados") or []], invoca=p.get("invoca") or [],
        tablas=[dto.TablaUso(nombre=t["nombre"], usos=t.get("usos") or [],
                             columnas=[dto.ColumnaUso(nombre=c["nombre"], confianza=c.get("confianza"), es_fecha=es_columna_fecha(c["nombre"])) for c in t.get("columnas") or []])
                for t in p.get("tablas") or []])


def reporte(codigo: str) -> dto.ReporteDetalle:
    d = _datos()
    r = next((x for x in d["reportes"] if x["codigo"] == codigo), None)
    if r is None:
        raise NoEncontrado(f"No existe el reporte «{codigo}» en el diccionario.")
    sp = next((p for p in d["procedimientos"] if p["nombre"] == r.get("procedimiento")), None)
    objetos = {r.get("procedimiento")} | set((sp or {}).get("invoca") or [])
    return dto.ReporteDetalle(
        **_fila(r, sp).model_dump(), parametros_catalogo=r.get("parametros") or [], procedimiento_detalle=_procedimiento(sp) if sp else None,
        hallazgos=[_hallazgo(h) for h in d["hallazgos"] if h["objeto"] in objetos or re.search(rf"(?<![\w]){re.escape(codigo)}(?![\w])", h.get("detalle") or "")])


# ---------------------------------------------------------------- tablas

def _tabla_fila(t: dict) -> dto.TablaFila:
    procs = {p for c in t["columnas"] for p in c.get("procedimientos") or []}
    return dto.TablaFila(nombre=t["nombre"], base=t["base"], tipo=t.get("tipo"), existe=t.get("existe"), columnas=len(t["columnas"]),
                         procedimientos=len(procs), en_registro=t["nombre"].lower() in TABLAS)


def tabla(nombre: str) -> dto.TablaDetalle:
    d = _datos()
    t = next((x for x in d["tablas"] if x["nombre"].lower() == nombre.lower()), None)
    if t is None:
        raise NoEncontrado(f"No existe la tabla «{nombre}» en el diccionario.")
    por_sp = {p["nombre"]: p.get("reportes") or [] for p in d["procedimientos"]}
    usados = {p for c in t["columnas"] for p in c.get("procedimientos") or []}
    propia = TABLAS.get(t["nombre"].lower())
    return dto.TablaDetalle(
        **_tabla_fila(t).model_dump(), descripcion=t.get("descripcion"), ficha=t.get("ficha"),
        columnas_detalle=[dto.Columna(nombre=c["nombre"], tipo=c.get("tipo"), acepta_nulos=c.get("aceptaNulos"), confianza=c.get("confianza"),
                                      es_fecha=es_columna_fecha(c["nombre"]), procedimientos=c.get("procedimientos") or []) for c in t["columnas"]],
        reportes_mis=sorted({r for p in usados for r in por_sp.get(p, [])}),
        registro=dto.RegistroTabla(tipo=propia.tipo, col_fecha=propia.col_fecha, confianza=propia.confianza,
                                   reportes=sorted(r for r, ts in USO.items() if propia.nombre in ts)) if propia else None)


# ---------------------------------------------------------------- lo que aporta a los reportes propios

def potencial() -> dto.Potencial:
    """Cruza el registro de tablas de REPORTES-AUTOMATIZADOS con el diccionario: qué falta documentar y qué columna de fecha confirmar."""
    en_dic = {t["nombre"].lower(): t for t in _datos()["tablas"]}
    propias = {n: t for n, t in TABLAS.items() if "{" not in n}  # las de nombre con fecha ({yyyymmdd}) no tienen ficha
    fechas = []
    for n, t in propias.items():
        if n not in en_dic:
            continue
        columnas = [c["nombre"] for c in en_dic[n]["columnas"]]
        candidatas = [c for c in columnas if es_columna_fecha(c)]
        if t.col_fecha and t.col_fecha.lower() not in {c.lower() for c in columnas}:
            fechas.append(dto.SugerenciaFecha(tabla=n, actual=t.col_fecha, confianza=t.confianza, candidatas=candidatas,
                                              motivo="Ningún procedimiento del diccionario usa la columna registrada: confirma que exista."))
        elif candidatas and (t.confianza == "por_confirmar" or (t.col_fecha is None and t.tipo in {"historica", "stock"})):
            fechas.append(dto.SugerenciaFecha(tabla=n, actual=t.col_fecha, confianza=t.confianza, candidatas=candidatas,
                                              motivo="La columna de fecha está por confirmar: estas son las candidatas que usan los procedimientos."))
    por_sp = {p["nombre"]: p.get("reportes") or [] for p in _datos()["procedimientos"]}
    disponibles = sorted((
        dto.TablaDisponible(nombre=n, reportes_mis=len({r for c in t["columnas"] for p in c.get("procedimientos") or [] for r in por_sp.get(p, [])}),
                            columnas=len(t["columnas"]), fechas=[c["nombre"] for c in t["columnas"] if es_columna_fecha(c["nombre"])])
        for n, t in en_dic.items() if n not in TABLAS and t.get("existe") is not False), key=lambda x: (-x.reportes_mis, x.nombre))
    return dto.Potencial(tablas_registradas=len(propias), en_diccionario=sum(n in en_dic for n in propias),
                         faltan_en_diccionario=sorted(n for n in propias if n not in en_dic), fechas=fechas, disponibles=disponibles[:50])
