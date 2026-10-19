"""Generar el diccionario desde la base: lee el catálogo, consulta cada base, avisa lo que falla y guarda solo si algo contestó."""

from types import SimpleNamespace

import pytest

from modulos.diccionario.aplicacion.casos_uso import construir
from modulos.diccionario.aplicacion.puertos import Puertos, puertos

REPORTES = [
    {"codigo": "R1", "descripcion": "Uno", "procedimiento": "mod_rep.com.SP1", "parametros": []},
    {"codigo": "R2", "descripcion": "Dos", "procedimiento": "strategos.dbo.SP2", "parametros": []},
    {"codigo": "R3", "descripcion": "Tres", "procedimiento": "", "parametros": []},
]
DEP = {"sp_base": "mod_rep", "sp_esquema": "com", "sp_nombre": "SP1", "ref_servidor": None, "ref_base": "storage", "ref_esquema": "com_act", "ref_entidad": "HDGP001",
       "ref_columna": "HFECPRO", "ref_tipo": None, "ref_objeto_tipo": None, "es_lectura": True, "es_escritura": None, "es_select_todo": None, "origen": "dm_sql_referenced_entities", "error": None}


class Generador:
    def __init__(self, caidas=(), sin_codigo=()):
        self.caidas, self.sin_codigo, self.estructuras = set(caidas), set(sin_codigo), []

    def dependencias(self, base, sps):
        if base in self.caidas:
            raise OSError("08001")
        return [DEP] if base == "mod_rep" else []

    def parametros(self, base):
        return []

    def cuerpos(self, base, sps):
        if base in self.sin_codigo:
            raise OSError("sin permiso")
        return [{"esquema": "com", "nombre": "SP1", "definicion": "CREATE PROCEDURE com.SP1 AS SELECT h.HFECPRO, h.NO_EXISTE FROM storage.com_act.HDGP001 h"}] if base == "mod_rep" else []

    def estructura(self, base, tablas):
        self.estructuras.append((base, tablas))
        return [{"base": "storage", "esquema": "com_act", "tabla": "HDGP001", "tipo_objeto": "BASE TABLE", "orden": 1, "columna": "HFECPRO", "tipo": "date", "acepta_nulos": "NO"}]


def _registrar(generador, catalogo=None):
    guardado = []
    lector = SimpleNamespace(guardar=guardado.append)
    puertos.registrar(Puertos(lector=lector, lanzador=SimpleNamespace(), catalogo=catalogo or SimpleNamespace(leer=lambda forzar=False: REPORTES), generador=generador))
    return guardado


@pytest.fixture(autouse=True)
def limpio():
    yield
    puertos.registrar(None)


def test_genera_y_guarda_el_diccionario_y_va_contando_lo_que_hace():
    g = Generador()
    guardado = _registrar(g)
    log = []
    assert construir.construir(log.append) == 0
    texto = "".join(log)
    assert texto.startswith("▶ Leyendo el catálogo") and "✓ 3 reportes · 2 procedimientos en 2 bases" in texto and "✓ Diccionario guardado" in texto
    d, = guardado
    assert d["resumen"]["reportes"] == 3 and [t["nombre"] for t in d["tablas"]] == ["storage.com_act.HDGP001"]
    assert g.estructuras == [("storage", [("com_act", "HDGP001")])]      # pide la estructura a la base de la tabla, no a la del SP


def test_una_base_caida_no_impide_generar_las_demas():
    guardado = _registrar(Generador(caidas={"strategos"}))
    log = []
    assert construir.construir(log.append) == 0
    assert "✗ strategos:" in "".join(log) and len(guardado) == 1
    assert {p["nombre"]: p["estado"] for p in guardado[0]["procedimientos"]}["strategos.dbo.SP2"] == "pendiente"   # no consultada: ni existe ni deja de existir


def test_si_ninguna_base_contesta_no_se_guarda_nada():
    guardado = _registrar(Generador(caidas={"mod_rep", "strategos"}))
    log = []
    assert construir.construir(log.append) == 1
    assert guardado == [] and "no se guardó nada" in "".join(log)


def test_sin_catalogo_no_se_guarda_nada_y_dice_por_que():
    def sin_vpn(forzar=False):
        raise OSError("08001")

    guardado = _registrar(Generador(), SimpleNamespace(leer=sin_vpn))
    log = []
    assert construir.construir(log.append) == 1
    assert guardado == [] and "✗ No pude leer el catálogo" in "".join(log) and "VPN" in "".join(log)


def test_analiza_el_codigo_de_los_sp_y_lo_suma_al_diccionario():
    guardado = _registrar(Generador())
    log = []
    assert construir.construir(log.append) == 0
    assert "▶ Analizando el código de 1 procedimientos" in "".join(log)
    assert ("columna-inexistente", "storage.com_act.HDGP001.NO_EXISTE") in {(h["regla"], h["objeto"]) for h in guardado[0]["hallazgos"]}


def test_sin_permiso_para_leer_el_codigo_el_diccionario_sale_igual_y_lo_avisa():
    guardado = _registrar(Generador(sin_codigo={"mod_rep"}))
    log = []
    assert construir.construir(log.append) == 0
    assert "AVISO mod_rep: no pude leer el código" in "".join(log) and len(guardado) == 1

