"""Procesos del diccionario y validación de las bases: solo los de la lista, su detalle y su historial."""

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


def _x(id_, proceso, estado="ok"):
    return dto.Ejecucion(id=id_, proceso=proceso, estado=estado, inicio="2026-10-18T10:00:00", fin=None, codigo=None)


class Lanzador:
    def __init__(self):
        self.tareas = []

    def ejecutar_tarea(self, proceso, tarea):
        self.tareas.append((proceso, tarea))
        return _x("tarea", proceso, "ejecutando")

    def historial(self, limite=30):
        return [_x("1", "construir"), _x("2", "bases"), _x("3", "construir")]


@pytest.fixture
def lanzador():
    x = Lanzador()
    generador = SimpleNamespace(scripts=lambda: [dto.ScriptArchivo(ruta="SQL · dependencias", codigo="SELECT dep")])
    puertos.registrar(Puertos(lector=SimpleNamespace(), lanzador=x, catalogo=SimpleNamespace(CONSULTA="SELECT RCODREP FROM rep.RREGREP01"), generador=generador))
    yield x
    puertos.registrar(None)


def test_solo_lanza_procesos_de_la_lista(lanzador):
    with pytest.raises(NoEncontrado):
        procesos.ejecutar("rm -rf")
    assert procesos.ejecutar("bases").id == "tarea" and lanzador.tareas[0][0] == "bases"


def test_el_catalogo_trae_los_procesos_propios():
    assert [p.id for p in procesos.catalogo()] == ["construir", "bases"]


def test_el_historial_se_filtra_por_proceso(lanzador):
    assert [x.id for x in procesos.historial("construir")] == ["1", "3"]
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


def test_construir_corre_dentro_de_la_api_y_su_script_muestra_las_consultas(lanzador):
    assert procesos.ejecutar("construir").id == "tarea" and lanzador.tareas[0][0] == "construir"
    rutas = [s.ruta for s in procesos.detalle("construir").scripts]
    assert rutas[0].startswith("SQL · catálogo") and "SQL · dependencias" in rutas and "construir.py · construir" in rutas and "armado.py · armar" in rutas
