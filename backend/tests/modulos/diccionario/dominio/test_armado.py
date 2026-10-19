"""Arma el diccionario con lo que responde SQL Server: estados de los SP, tablas y columnas con su estructura real, y lo que está roto."""

from modulos.diccionario.dominio.armado import armar, tablas_referidas

REPORTES = [
    {"codigo": "R1", "descripcion": "Uno", "procedimiento": "mod_rep.com.SP1", "parametros": ["fec"]},
    {"codigo": "R1B", "descripcion": "Uno bis", "procedimiento": "mod_rep.com.SP1", "parametros": ["fec"]},
    {"codigo": "R2", "descripcion": "Dos", "procedimiento": "mod_rep.com.SP_MUERTO", "parametros": []},
    {"codigo": "R3", "descripcion": "Tres", "procedimiento": "strategos.dbo.SP3", "parametros": []},
    {"codigo": "R4", "descripcion": "Cuatro", "procedimiento": "mod_rep.com.SP_DINAMICO", "parametros": []},
    {"codigo": "R5", "descripcion": "Cinco", "procedimiento": "", "parametros": []},
]


def _dep(sp, base="mod_rep", esquema="com", **resto):
    return {"sp_base": base, "sp_esquema": esquema, "sp_nombre": sp, "ref_servidor": None, "ref_base": None, "ref_esquema": None, "ref_entidad": None, "ref_columna": None,
            "ref_tipo": None, "ref_objeto_tipo": None, "es_lectura": None, "es_escritura": None, "es_select_todo": None, "origen": "dm_sql_referenced_entities", "error": None, **resto}


DEPENDENCIAS = [
    # SP1: lee storage.com_act.HDGP001 (HFECPRO y HOLA, que no existe), escribe en mod_rep.dbo.Falta (que no existe), llama a SP2 y a una función
    _dep("SP1", ref_base="storage", ref_esquema="com_act", ref_entidad="HDGP001", ref_columna="HFECPRO", es_lectura=True),
    _dep("SP1", ref_base="storage", ref_esquema="com_act", ref_entidad="HDGP001", ref_columna="HOLA", es_lectura=True),
    _dep("SP1", ref_base="storage", ref_esquema="com_act", ref_entidad="HDGP001", origen="sql_expression_dependencies"),
    _dep("SP1", ref_base="mod_rep", ref_esquema="dbo", ref_entidad="Falta", ref_columna="x", es_escritura=True, ref_objeto_tipo="USER_TABLE"),
    _dep("SP1", ref_base="mod_rep", ref_esquema="com", ref_entidad="SP2", ref_objeto_tipo="SQL_STORED_PROCEDURE"),
    _dep("SP1", ref_base="mod_rep", ref_esquema="dbo", ref_entidad="fn_algo", ref_objeto_tipo="SQL_SCALAR_FUNCTION"),
    _dep("SP1", ref_servidor="LINKED", ref_base="otra", ref_esquema="dbo", ref_entidad="remota", origen="sql_expression_dependencies"),   # servidor vinculado: fuera
    _dep("SP_MUERTO", origen="catalogo", error="El SP no existe en esta base"),
    _dep("SP_DINAMICO", origen="dm_sql_referenced_entities", error="no compila contra el esquema actual"),
    _dep("SP_DINAMICO", ref_base="storage", ref_esquema="com_act", ref_entidad="HDGP001", origen="sql_expression_dependencies"),
]
PARAMETROS = [
    {"base": "mod_rep", "esquema": "com", "sp": "SP1", "nombre": "@fec", "tipo": "date", "tiene_defecto": False, "salida": False, "orden": 1},
    {"base": "mod_rep", "esquema": "com", "sp": "SP1", "nombre": "@pagina", "tipo": "int", "tiene_defecto": True, "salida": False, "orden": 2},
]
ESTRUCTURA = [
    {"base": "storage", "esquema": "com_act", "tabla": "HDGP001", "tipo_objeto": "BASE TABLE", "orden": 1, "columna": "HFECPRO", "tipo": "date", "acepta_nulos": "NO"},
    {"base": "storage", "esquema": "com_act", "tabla": "HDGP001", "tipo_objeto": "BASE TABLE", "orden": 2, "columna": "HCODA", "tipo": "varchar", "acepta_nulos": "YES"},
]


def _armar():
    return armar(REPORTES, DEPENDENCIAS, PARAMETROS, ESTRUCTURA, {"mod_rep"}, {"storage", "mod_rep"})


def test_estados_de_los_procedimientos():
    d = _armar()
    estado = {p["nombre"]: p["estado"] for p in d["procedimientos"]}
    assert estado == {"mod_rep.com.SP1": "validado", "mod_rep.com.SP_MUERTO": "pendiente", "mod_rep.com.SP_DINAMICO": "extraido", "strategos.dbo.SP3": "pendiente"}
    assert "" not in estado                                    # el reporte sin procedimiento no inventa uno
    sp1 = next(p for p in d["procedimientos"] if p["nombre"] == "mod_rep.com.SP1")
    assert sp1["reportes"] == ["R1", "R1B"] and sp1["invoca"] == ["mod_rep.com.SP2"] and sp1["otrosObjetos"] == ["mod_rep.dbo.fn_algo"]
    assert [(p["nombre"], p["tipo"], p["porDefecto"]) for p in sp1["parametros"]] == [("@fec", "date", None), ("@pagina", "int", "")]


def test_tablas_y_columnas_con_su_estructura_real():
    d = _armar()
    t = {x["nombre"]: x for x in d["tablas"]}
    assert set(t) == {"storage.com_act.HDGP001", "mod_rep.dbo.Falta"}                 # ni el servidor vinculado ni el SP2 ni la función son tablas
    hdgp = t["storage.com_act.HDGP001"]
    assert (hdgp["existe"], hdgp["columnasReales"]) == (True, 2)
    c = {x["nombre"]: x for x in hdgp["columnas"]}
    assert (c["HFECPRO"]["tipo"], c["HFECPRO"]["aceptaNulos"], c["HFECPRO"]["confianza"], c["HFECPRO"]["existe"]) == ("date", False, "exacta", True)
    assert (c["HOLA"]["existe"], c["HOLA"]["confianza"]) == (False, "motor")
    assert hdgp["columnas"][0]["procedimientos"] == ["mod_rep.com.SP1"]
    assert t["mod_rep.dbo.Falta"]["existe"] is False


def test_hallazgos_de_lo_que_esta_roto():
    h = {(x["regla"], x["objeto"]): x for x in _armar()["hallazgos"]}
    assert ("sp-inexistente", "mod_rep.com.SP_MUERTO") in h and h[("sp-inexistente", "mod_rep.com.SP_MUERTO")]["nivel"] == "error"
    assert ("tabla-inexistente", "mod_rep.dbo.Falta") in h and ("columna-inexistente", "storage.com_act.HDGP001.HOLA") in h
    assert h[("motor-sin-columnas", "mod_rep.com.SP_DINAMICO")]["nivel"] == "aviso"
    assert not any(k[1] == "strategos.dbo.SP3" for k in h)                         # su base no se consultó: no se afirma que esté roto


def test_una_base_no_consultada_deja_su_tabla_sin_veredicto():
    d = armar(REPORTES, DEPENDENCIAS, PARAMETROS, [], {"mod_rep"}, set())
    t = {x["nombre"]: x for x in d["tablas"]}
    assert t["storage.com_act.HDGP001"]["existe"] is None and t["mod_rep.dbo.Falta"]["existe"] is None
    assert not any(h["regla"].startswith(("tabla-", "columna-")) for h in d["hallazgos"])


def test_el_resumen_y_los_reportes_salen_del_catalogo():
    d = _armar()
    assert d["resumen"] == {"reportes": 6, "procedimientos": 4, "extraidos": 2, "validados": 1, "tablas": 2}
    assert {r["codigo"] for r in d["reportes"]} == {"R1", "R1B", "R2", "R3", "R4", "R5"} and all(r["front"] == [] for r in d["reportes"])


def test_tablas_referidas_por_base_para_pedir_su_estructura():
    assert tablas_referidas(DEPENDENCIAS) == {"storage": {("com_act", "HDGP001")}, "mod_rep": {("dbo", "Falta")}}


def test_un_objeto_sin_tipo_no_se_acusa_de_faltar():
    dep = [_dep("SP1", ref_base="strategos", ref_esquema="dbo", ref_entidad="SP_OTRA_BASE")]          # sin ref_objeto_tipo: el motor no lo resolvió
    d = armar([REPORTES[0]], dep, [], [], {"mod_rep"}, {"strategos"})
    assert d["tablas"][0]["existe"] is None
    assert [(h["regla"], h["nivel"]) for h in d["hallazgos"]] == [("objeto-no-resuelto", "aviso")]


def test_una_base_con_distinta_mayuscula_es_la_misma():
    dep = [_dep("SP1", ref_base="STORAGE", ref_esquema="x", ref_entidad="T1", ref_objeto_tipo="USER_TABLE"), _dep("SP1", ref_base="storage", ref_esquema="x", ref_entidad="T2", ref_objeto_tipo="USER_TABLE")]
    assert tablas_referidas(dep) == {"storage": {("x", "T1"), ("x", "T2")}}

