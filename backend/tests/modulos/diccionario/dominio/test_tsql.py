"""Analizador estático de T-SQL: tablas, columnas con su confianza, SP invocados, columnas de salida, SQL dinámico y firma de parámetros."""

from modulos.diccionario.dominio.tsql import analizar_procedimiento as analizar


def _tabla(a, completo):
    return next(t for t in a["tablas"] if t["completo"] == completo)


def _columnas(t):
    return {c["nombre"]: c["confianza"] for c in t["columnas"]}


def test_columnas_calificadas_son_exactas_y_las_sueltas_de_una_sola_tabla_son_inferidas():
    a = analizar("CREATE PROCEDURE com.SP1 @fec date AS SELECT h.HFECPRO, HCODA FROM storage.com_act.HDGP001 h WHERE h.HTIPCOD = 1", base="mod_rep", esquema="com")
    t = _tabla(a, "storage.com_act.HDGP001")
    assert t["usos"] == ["lee"] and _columnas(t) == {"HCODA": "inferida", "HFECPRO": "exacta", "HTIPCOD": "exacta"}
    assert a["resultados"] == [["HFECPRO", "HCODA"]]


def test_la_cabecera_trae_esquema_nombre_y_parametros_con_su_valor_por_defecto():
    a = analizar("CREATE PROCEDURE [com].[SP1] @fec date, @tip varchar(10) = 'A', @sal int OUTPUT AS SELECT 1")
    p = a["procedimiento"]
    assert (p["esquema"], p["nombre"]) == ("com", "SP1")
    assert [(x["nombre"], x["tipo"], x["porDefecto"], x["salida"]) for x in p["parametros"]] == [
        ("@fec", "date", None, False), ("@tip", "varchar(10)", "'A'", False), ("@sal", "int", None, True)]


def test_insert_update_delete_y_el_nombre_sin_esquema_toma_el_del_sp():
    a = analizar("CREATE PROCEDURE com.SP1 AS INSERT INTO t1 (a, b) SELECT x.a, x.b FROM com.t2 x; UPDATE t3 SET c = 1 WHERE d = 2; DELETE FROM t4", base="mod_rep", esquema="com")
    assert [(t["completo"], t["usos"]) for t in a["tablas"]] == [
        ("mod_rep.com.t1", ["inserta"]), ("mod_rep.com.t2", ["lee"]), ("mod_rep.com.t3", ["actualiza"]), ("mod_rep.com.t4", ["elimina"])]
    assert _columnas(_tabla(a, "mod_rep.com.t1")) == {"a": "exacta", "b": "exacta"}
    assert _columnas(_tabla(a, "mod_rep.com.t3")) == {"c": "inferida", "d": "inferida"}
    assert a["resultados"] == []                                       # el SELECT alimenta un INSERT: no devuelve filas


def test_una_columna_sin_calificar_con_dos_tablas_queda_sin_resolver():
    a = analizar("CREATE PROCEDURE dbo.SP1 AS SELECT a.X, COL FROM base1.dbo.ta a JOIN base1.dbo.tb b ON a.id = b.id", base="b", esquema="dbo")
    assert [(s["columna"], s["candidatas"]) for s in a["sin_resolver"]] == [("COL", ["base1.dbo.ta", "base1.dbo.tb"])]


def test_cte_temporal_y_derivada_no_son_tablas_del_diccionario():
    a = analizar("CREATE PROCEDURE dbo.SP1 AS WITH c AS (SELECT a FROM dbo.real) SELECT c.a INTO #tmp FROM c; SELECT z FROM (SELECT 1 z) d JOIN #tmp t ON 1 = 1", base="b")
    assert [t["completo"] for t in a["tablas"]] == ["b.dbo.real"] and a["ctes"] == ["c"] and a["temporales"] == ["#tmp"]


def test_invocaciones_y_sql_dinamico():
    a = analizar("CREATE PROCEDURE dbo.SP1 AS EXEC dbo.otro @p = 1, @q = @x OUTPUT; EXEC (@sql); EXEC sp_executesql @sql", base="b")
    assert [i["nombre"] for i in a["invocaciones"]] == ["dbo.otro"] and a["invocaciones"][0]["argumentos"] == ["@p = 1", "@q = @x OUTPUT"]
    assert a["sql_dinamico"] is True
    assert analizar("CREATE PROCEDURE dbo.SP1 AS EXEC dbo.otro", base="b")["sql_dinamico"] is False


def test_los_comentarios_y_las_cadenas_no_se_confunden_con_codigo():
    a = analizar("CREATE PROCEDURE dbo.SP1 AS /* FROM fantasma */ SELECT 'FROM otra' AS x -- FROM nada\nFROM dbo.real", base="b")
    assert [t["completo"] for t in a["tablas"]] == ["b.dbo.real"]


def test_los_argumentos_de_fecha_no_son_columnas():
    a = analizar("CREATE PROCEDURE dbo.SP1 AS SELECT DATEADD(day, 1, f) FROM dbo.t", base="b")
    assert _columnas(_tabla(a, "b.dbo.t")) == {"f": "inferida"}


def test_texto_sin_create_se_analiza_igual_y_lo_avisa():
    a = analizar("SELECT x FROM dbo.t", base="b")
    assert a["procedimiento"] is None and a["advertencias"] and [t["completo"] for t in a["tablas"]] == ["b.dbo.t"]
