"""Procesos del repo DICCIONARIO y validación de las bases: solo los de la lista, su detalle y su historial."""

import threading
import time
from types import SimpleNamespace

import pandas as pd
import pytest

from core.excepciones import NoEncontrado
from core.puertos import Nucleo, nucleo
from core.servidores import BASES_DE
from modulos.diccionario.aplicacion import dto
from modulos.diccionario.aplicacion.casos_uso import procesos
from modulos.diccionario.aplicacion.puertos import Puertos, puertos
from modulos.diccionario.dominio.columnas import PROCESOS


def _x(id_, proceso, estado="ok"):
    return dto.Ejecucion(id=id_, proceso=proceso, estado=estado, inicio="2026-10-18T10:00:00", fin=None, codigo=None)


class Lanzador:
    def __init__(self):
        self.lanzados, self.tareas = [], []

    def ejecutar(self, proceso, comando, carpeta):
        self.lanzados.append((proceso, comando, carpeta))
        return _x("abc", proceso, "ejecutando")

    def ejecutar_tarea(self, proceso, tarea):
        self.tareas.append((proceso, tarea))
        return _x("tarea", proceso, "ejecutando")

    def historial(self, limite=30):
        return [_x("1", "generar"), _x("2", "bases"), _x("3", "generar")]


class Lector:
    def carpeta(self):
        return "carpeta"

    def script_npm(self, nombre):
        return [dto.ScriptArchivo(ruta=f"package.json › scripts.{nombre}", codigo="node a.mjs")]

    def archivos(self, patrones):
        return [dto.ArchivoProceso(ruta="diccionario/reportes.md", tamano=10, modificado="2026-10-18T10:00:00", tipo="texto")]

    def texto(self, ruta, patrones):
        if ruta not in {a.ruta for a in self.archivos(patrones)}:
            raise NoEncontrado("no")
        return dto.VistaArchivo(ruta=ruta, texto="# hola", recortado=False)


@pytest.fixture
def lanzador():
    x = Lanzador()
    puertos.registrar(Puertos(lector=Lector(), lanzador=x, catalogo=SimpleNamespace()))
    yield x
    puertos.registrar(None)


def test_solo_lanza_procesos_de_la_lista(lanzador):
    with pytest.raises(NoEncontrado):
        procesos.ejecutar("rm -rf")
    assert procesos.ejecutar("verificar").id == "abc"
    assert lanzador.lanzados == [("verificar", PROCESOS["verificar"].comando, "carpeta")]


def test_el_catalogo_trae_los_cuatro_procesos_y_cuales_dejan_archivos():
    assert {p.id: p.genera for p in procesos.catalogo()} == {"generar": True, "verificar": False, "test": False, "bases": False}


def test_detalle_con_su_script_y_sus_archivos(lanzador):
    d = procesos.detalle("generar")
    assert [s.ruta for s in d.scripts] == ["package.json › scripts.generar"] and [a.ruta for a in d.archivos] == ["diccionario/reportes.md"]
    assert procesos.detalle("verificar").archivos == []                  # no deja archivos: nada que listar
    with pytest.raises(NoEncontrado):
        procesos.detalle("inventado")


def test_solo_se_ve_un_archivo_que_el_proceso_genera(lanzador):
    assert procesos.archivo("generar", "diccionario/reportes.md").texto == "# hola"
    for ruta in ("../.env", "package.json", ""):
        with pytest.raises(NoEncontrado):
            procesos.archivo("generar", ruta)


def test_el_historial_se_filtra_por_proceso(lanzador):
    assert [x.id for x in procesos.historial("generar")] == ["1", "3"]
    assert len(procesos.historial()) == 3


class Bd:
    """mish: todo en línea salvo `staging` (offline) y `appj` (no aparece); slc: sin red; rcc: no contesta hasta que el test termina."""

    def __init__(self):
        self.liberar = threading.Event()

    def leer_sql(self, servidor, consulta, params=None, base=None, timeout=None):
        if servidor == "slc":
            raise OSError("08001")
        if servidor == "rcc":
            self.liberar.wait(5)
            raise OSError("liberado")   # el hilo termina sin volver a pedir `nucleo()`: no queda nada vivo tras el test
        if "@@SERVERNAME" in consulta:
            return pd.DataFrame({"servidor": ["MISHWBDDES01"], "usuario": ["MIS\\api"], "version": ["15.0.2000"]})
        assert consulta == procesos.CONSULTA_BASES
        estados = {b: "ONLINE" for b in BASES_DE[servidor] if b not in ("appj", "staging")} | {"staging": "OFFLINE"}
        return pd.DataFrame({"name": list(estados), "state_desc": list(estados.values())})


@pytest.fixture
def servidores():
    lista = [SimpleNamespace(nombre=n, servidor=f"srv-{n}") for n in ("mish", "slc", "rcc")]
    bd = Bd()
    nucleo.registrar(Nucleo(bd=bd, entorno=SimpleNamespace(servidores=lambda: lista)))
    yield
    bd.liberar.set()
    nucleo.registrar(None)


def test_validar_bases_prueba_cada_servidor_y_cada_base_y_dice_cual_fallo(lanzador, servidores, monkeypatch):
    monkeypatch.setattr(procesos, "LIMITE", 0.5)
    assert procesos.ejecutar("bases").id == "tarea"
    emitido = []
    codigo = lanzador.tareas[0][1](emitido.append)
    log = "".join(emitido)
    assert codigo == 1 and log.startswith("▶ Probando mish, slc, rcc")
    assert "✓ mish (srv-mish): conexión correcta" in log and "SQL Server 15.0.2000" in log and "usuario MIS\\api" in log
    assert "    ✓ storage" in log and "    ✗ staging: OFFLINE" in log                  # una base fuera de línea
    assert "    AVISO appj: no aparece" in log                                           # no la ve: aviso, no falla
    assert "✗ slc (srv-slc)" in log and "VPN" in log                                    # sin conexión
    assert "✗ rcc (srv-rcc): sin respuesta en 0.5 s" in log                             # no contesta: no deja esperando


def test_el_script_de_las_bases_es_el_codigo_real_no_solo_un_select(lanzador, servidores):
    rutas = {s.ruta: s.codigo for s in procesos.detalle("bases").scripts}
    sql = rutas["SQL · lo que se consulta en cada servidor"]
    assert "sys.databases" in sql and "@@SERVERNAME" in sql and "mish: app, gitea" in sql      # las consultas y las bases que espera
    assert "def _probar_servidor" in rutas["procesos.py · _probar_servidor"] and "def _validar_bases" in rutas["procesos.py · _validar_bases"]
    assert "def leer_sql" in rutas["core/bd.py · leer_sql"]


def test_un_error_raro_en_un_servidor_se_ve_como_error_no_como_sin_respuesta(lanzador):
    class BdRara:
        def leer_sql(self, servidor, consulta, params=None, base=None, timeout=None):
            if "@@SERVERNAME" in consulta:
                return pd.DataFrame({"servidor": ["x"], "usuario": ["u"]})   # la consulta de siempre, con otra forma: falta `version`
            return pd.DataFrame({"name": ["app"], "state_desc": ["ONLINE"]})

    nucleo.registrar(Nucleo(bd=BdRara(), entorno=SimpleNamespace(servidores=lambda: [SimpleNamespace(nombre="mish", servidor="srv-mish")])))
    try:
        emitido = []
        t = time.monotonic()
        codigo = procesos._validar_bases(emitido.append)
    finally:
        nucleo.registrar(None)
    log = "".join(emitido)
    assert codigo == 1 and "✗ mish (srv-mish): error inesperado (KeyError)" in log and "sin respuesta" not in log
    assert time.monotonic() - t < procesos.LIMITE   # no espera el tope completo
