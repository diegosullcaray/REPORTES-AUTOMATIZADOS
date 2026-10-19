"""Diccionario de datos: consultas sobre un diccionario.json mínimo (no lee el repo DICCIONARIO real) y su cruce con el registro de tablas."""

from types import SimpleNamespace

import pytest

from core.excepciones import NoEncontrado
from modulos.diccionario.aplicacion.casos_uso import diccionario
from modulos.diccionario.aplicacion.puertos import Puertos, puertos
from modulos.reportes.dominio.tablas import Tabla

SP = "mod_rep.com.SP1"
DICCIONARIO = {
    "reportes": [
        {"codigo": "R1", "descripcion": "Uno", "procedimiento": SP, "parametros": ["fecha"], "front": ["reportes / mensual"]},
        {"codigo": "R2", "descripcion": "Dos", "procedimiento": "x.y.NOEXISTE", "parametros": [], "front": []},
    ],
    "procedimientos": [{
        "nombre": SP, "base": "mod_rep", "estado": "validado", "reportes": ["R1"], "invoca": [], "resultados": [["*"]],
        "parametros": [{"nombre": "@fecha", "tipo": "date", "porDefecto": None, "salida": False}],
        "tablas": [{"nombre": "storage.com_act.HDGP001", "usos": ["lee"], "columnas": [{"nombre": "HFECPRO", "confianza": "confirmada"}, {"nombre": "HCODA", "confianza": "motor"}]}],
    }],
    "tablas": [
        {"nombre": "storage.com_act.HDGP001", "base": "storage", "tipo": "tabla", "existe": True, "descripcion": None, "ficha": None,
         "columnas": [{"nombre": "HFECPRO", "tipo": "date", "aceptaNulos": False, "confianza": "exacta", "procedimientos": [SP]},
                      {"nombre": "HCODA", "tipo": None, "aceptaNulos": None, "confianza": "motor", "procedimientos": [SP]}]},
        {"nombre": "zz.dbo.Nueva", "base": "zz", "tipo": "tabla", "existe": True, "descripcion": None, "ficha": None,
         "columnas": [{"nombre": "FECHA_X", "tipo": None, "aceptaNulos": None, "confianza": "inferida", "procedimientos": [SP]}]},
        {"nombre": "zz.dbo.Fantasma", "base": "zz", "tipo": None, "existe": False, "descripcion": None, "ficha": None, "columnas": []},
    ],
    "hallazgos": [
        {"nivel": "error", "regla": "tabla-inexistente", "origen": "produccion", "objeto": SP, "detalle": "la usa R1", "enLineaBase": False},
        {"nivel": "aviso", "regla": "sql-dinamico", "origen": "analisis", "objeto": "otro.sp", "detalle": "", "enLineaBase": True},
    ],
}
REGISTRO = {
    "storage.com_act.hdgp001": Tabla("storage.com_act.hdgp001", "historica", None, "por_confirmar"),
    "storage.com_act.solo_mia": Tabla("storage.com_act.solo_mia", "historica", "HFECPRO", "confirmada"),
}


def _sin_base():
    raise OSError("08001 sin conexión")


@pytest.fixture(autouse=True)
def dic(monkeypatch):
    lector = SimpleNamespace(leer=lambda: DICCIONARIO, carpeta=lambda: "carpeta", origen=lambda: ("repo", "2026-10-18T10:00:00"))
    puertos.registrar(Puertos(lector=lector, lanzador=SimpleNamespace(), catalogo=SimpleNamespace(leer=_sin_base, FUENTE="mod_rep.rep.RREGREP01"), generador=SimpleNamespace()))
    monkeypatch.setattr(diccionario, "TABLAS", REGISTRO)
    monkeypatch.setattr(diccionario, "USO", {"mi-reporte": ("storage.com_act.hdgp001",)})
    yield
    puertos.registrar(None)


def test_resumen_cuenta_lo_que_hay():
    r = diccionario.resumen()
    assert (r.reportes, r.procedimientos, r.validados, r.tablas, r.columnas) == (2, 1, 1, 3, 3)
    assert (r.errores, r.avisos, r.errores_nuevos) == (1, 1, 1)
    assert [(b.base, b.tablas) for b in r.bases] == [("mod_rep", 1)]


def test_hallazgos_van_primero_los_errores():
    assert [h.nivel for h in diccionario.hallazgos()] == ["error", "aviso"]


def test_reporte_al_detalle():
    d = diccionario.reporte("R1")
    assert (d.estado, d.base, d.tablas) == ("validado", "mod_rep", 1)
    assert d.procedimiento_detalle.tablas[0].columnas[0].es_fecha and [h.regla for h in d.hallazgos] == ["tabla-inexistente"]
    sin = diccionario.reporte("R2")
    assert (sin.estado, sin.procedimiento_detalle) == ("sin extraer", None)
    with pytest.raises(NoEncontrado):
        diccionario.reporte("NO")


def test_bases_cuentan_procedimientos_reportes_y_tablas():
    por_base = {b.base: b for b in diccionario.bases()}
    assert set(por_base) == {"mod_rep", "x", "storage", "zz"}   # «x» es la base del procedimiento que el catálogo nombra y no existe
    mod_rep = por_base["mod_rep"]
    assert (mod_rep.procedimientos, mod_rep.validados, mod_rep.reportes, mod_rep.tablas_propias, mod_rep.tablas_usadas) == (1, 1, 1, 0, 1)
    assert (por_base["storage"].procedimientos, por_base["storage"].tablas_propias, por_base["zz"].tablas_propias) == (0, 1, 2)


def test_una_base_tiene_dos_secciones_procedimientos_y_tablas_que_ocupa():
    d = diccionario.base("MOD_REP")   # sin distinguir mayúsculas
    assert d.base == "mod_rep" and [(p.nombre, p.reportes, p.tablas) for p in d.procedimientos] == [(SP, ["R1"], 1)]
    assert [(t.nombre, t.propia, t.usada_por) for t in d.tablas] == [("storage.com_act.HDGP001", False, 1)]   # la usa desde otra base
    zz = diccionario.base("zz")
    assert [(t.nombre, t.propia) for t in zz.tablas] == [("zz.dbo.Fantasma", True), ("zz.dbo.Nueva", True)]
    sin = diccionario.base("x")
    assert [(p.nombre, p.estado) for p in sin.procedimientos] == [("x.y.NOEXISTE", "sin extraer")]
    with pytest.raises(NoEncontrado):
        diccionario.base("inventada")


def test_tabla_cruza_con_el_registro_sin_distinguir_mayusculas():
    t = diccionario.tabla("STORAGE.com_act.hdgp001")
    assert t.en_registro and t.reportes_mis == ["R1"] and t.registro.reportes == ["mi-reporte"]
    assert [c.es_fecha for c in t.columnas_detalle] == [True, False]
    assert diccionario.tabla("zz.dbo.nueva").registro is None
    with pytest.raises(NoEncontrado):
        diccionario.tabla("no.existe.x")


def test_potencial_sugiere_fechas_y_lista_lo_que_falta_y_lo_disponible():
    p = diccionario.potencial()
    assert (p.tablas_registradas, p.en_diccionario, p.faltan_en_diccionario) == (2, 1, ["storage.com_act.solo_mia"])
    assert [(s.tabla, s.candidatas) for s in p.fechas] == [("storage.com_act.hdgp001", ["HFECPRO"])]
    assert [(d.nombre, d.reportes_mis, d.fechas) for d in p.disponibles] == [("zz.dbo.nueva", 1, ["FECHA_X"])]  # la que no existe en la base no se ofrece


def test_api_responde_y_protege_con_sesion():
    from modulos.sistema.aplicacion.casos_uso import sesion
    from tests.cliente_web import TestClient

    cliente = TestClient()
    assert cliente.get("/api/diccionario/resumen").status_code == 401
    cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))
    assert cliente.get("/api/diccionario/resumen").json()["reportes"] == 2
    assert cliente.get("/api/diccionario/tablas/zz.dbo.nueva").json()["nombre"] == "zz.dbo.Nueva"
    assert cliente.get("/api/diccionario/reportes/NO").status_code == 404
    assert "mod_rep" in [b["base"] for b in cliente.get("/api/diccionario/bases").json()]
    assert cliente.get("/api/diccionario/bases/inventada").status_code == 404
    assert cliente.post("/api/diccionario/procesos/inventado/ejecutar").status_code == 404


def test_sin_conexion_el_catalogo_sale_del_json_y_dice_por_que():
    r = diccionario.resumen()
    assert (r.reportes, r.catalogo.fuente) == (2, "diccionario guardado")
    assert r.catalogo.motivo and not r.catalogo.nuevos and not r.catalogo.retirados


def test_el_catalogo_sale_de_la_base_y_se_cruza_con_el_json():
    base = [  # RREGREP01: R1 cambió de descripción, R2 ya no está, R3 es nueva
        {"codigo": "R1", "descripcion": "Uno en la base", "procedimiento": SP, "parametros": ["fec"]},
        {"codigo": "R3", "descripcion": "Nuevo", "procedimiento": "mod_rep.com.SP3", "parametros": []},
    ]
    puertos().catalogo = SimpleNamespace(leer=lambda: base, FUENTE="mod_rep.rep.RREGREP01")
    r = diccionario.resumen()
    assert (r.reportes, r.catalogo.fuente, r.catalogo.nuevos, r.catalogo.retirados) == (2, "mod_rep.rep.RREGREP01", ["R3"], ["R2"])
    d = diccionario.reporte("R1")
    assert (d.descripcion, d.front) == ("Uno en la base", ["reportes / mensual"])   # la descripción manda la base; las pantallas, el diccionario
    assert diccionario.reporte("R3").front == [] and diccionario.reporte("R3").estado == "sin extraer"   # aún sin extraer
    with pytest.raises(NoEncontrado):
        diccionario.reporte("R2")
    assert {p.nombre for p in diccionario.base("mod_rep").procedimientos} == {SP, "mod_rep.com.SP3"}


def test_sin_diccionario_guardado_igual_funciona_con_solo_el_catalogo():
    from core.excepciones import NoEncontrado as _Sin

    def sin_archivo():
        raise _Sin("Todavía no hay diccionario")

    puertos().lector = SimpleNamespace(leer=sin_archivo, carpeta=lambda: "c", origen=lambda: None)
    puertos().catalogo = SimpleNamespace(leer=lambda: [{"codigo": "R9", "descripcion": "Nuevo", "procedimiento": "mod_rep.com.SP9", "parametros": []}], FUENTE="mod_rep.rep.RREGREP01")
    r = diccionario.resumen()
    assert (r.datos.origen, r.datos.generado, r.reportes, r.catalogo.fuente) == ("ninguno", None, 1, "mod_rep.rep.RREGREP01")
    assert (r.tablas, r.errores, r.errores_nuevos) == (0, 0, 0)
    assert [(b.base, b.procedimientos, b.reportes) for b in diccionario.bases()] == [("mod_rep", 1, 1)]
    assert diccionario.base("mod_rep").procedimientos[0].estado == "sin extraer"        # existe en el catálogo; falta generar el detalle


def test_sin_diccionario_y_sin_catalogo_dice_que_hacer():
    def sin_archivo():
        from core.excepciones import NoEncontrado as _Sin

        raise _Sin("x")

    puertos().lector = SimpleNamespace(leer=sin_archivo, carpeta=lambda: "c", origen=lambda: None)
    with pytest.raises(NoEncontrado, match="No hay diccionario guardado y no pude leer el catálogo"):
        diccionario.resumen()


def test_el_origen_del_diccionario_se_informa():
    r = diccionario.resumen()
    assert (r.datos.origen, r.datos.generado) == ("repo", "2026-10-18T10:00:00") and r.errores_nuevos == 1      # «nuevos» solo con la línea base del repo
    puertos().lector = SimpleNamespace(leer=lambda: DICCIONARIO, carpeta=lambda: "c", origen=lambda: ("bd", "2026-10-18T11:00:00"))
    r = diccionario.resumen()
    assert r.datos.origen == "bd" and r.errores_nuevos == 0
