"""Consultas de metadatos a cada base: los nombres viajan como parámetros (nunca dentro del texto SQL) y se leen todos los resultados del lote."""

from contextlib import contextmanager

import pytest

from modulos.diccionario.infraestructura import generador_bd


class Cursor:
    """Un lote que devuelve primero un conjunto sin columnas (como un INSERT) y al final el SELECT."""

    def __init__(self, registro, columnas, filas):
        self.registro, self.columnas, self.filas, self.paso = registro, columnas, filas, 0

    def execute(self, sql, *params):
        self.registro.append((sql, params))

    @property
    def description(self):
        return [(c,) for c in self.columnas] if self.paso == 1 else None

    def fetchall(self):
        return self.filas

    def nextset(self):
        self.paso += 1
        return self.paso < 2

    def close(self):
        pass


@pytest.fixture
def servidor(monkeypatch):
    registro, abiertas = [], []

    @contextmanager
    def conexion(servidor, base=None, autocommit=True):
        abiertas.append((servidor, base))
        yield type("Conn", (), {"timeout": 0, "cursor": lambda self: Cursor(registro, ["base", "valor"], [("mod_rep", 1)])})()

    monkeypatch.setattr(generador_bd.bd, "conexion_pyodbc", conexion)
    return registro, abiertas


def test_las_dependencias_pasan_los_nombres_como_parametros_y_van_al_servidor_de_su_base(servidor):
    registro, abiertas = servidor
    hostil = "x'; DROP TABLE y; --"
    filas = generador_bd.dependencias("mod_rep", [("com", "SP1"), ("com", hostil)])
    assert filas == [{"base": "mod_rep", "valor": 1}] and abiertas == [("mish", "mod_rep")]
    sql, params = registro[0]
    assert hostil not in sql and "DROP TABLE y" not in sql and hostil in params           # el nombre hostil nunca toca el texto de la consulta
    assert sql.count("?") == len(params) == 4 and "sys.dm_sql_referenced_entities" in sql and "{" not in sql


def test_muchos_procedimientos_se_reparten_en_varios_insert(servidor):
    registro, _ = servidor
    pares = [("com", f"SP{i}") for i in range(generador_bd.TRAMO + 1)]
    generador_bd.dependencias("mod_rep", pares)
    sql, params = registro[0]
    assert sql.count("INSERT INTO @catalogo") == 2 and len(params) == 2 * len(pares) and sql.count("?") == len(params)   # ≤ 1000 filas por VALUES y ≤ 2100 parámetros


def test_los_parametros_de_los_sp_son_solo_lectura_del_catalogo(servidor):
    registro, _ = servidor
    generador_bd.parametros("strategos")
    assert registro[0][0] == generador_bd.PARAMETROS and registro[0][1] == () and "sys.parameters" in registro[0][0]
    assert not any(p in registro[0][0].upper() for p in ("INSERT", "UPDATE", "DELETE", "EXEC"))


def test_la_estructura_se_pide_por_tramos_de_tablas(servidor):
    registro, abiertas = servidor
    tablas = [("com_act", f"T{i}") for i in range(1001)]
    generador_bd.estructura("storage", tablas)
    assert len(registro) == 3 and abiertas == [("mish", "storage")] * 3                        # 500 + 500 + 1
    assert all(sql.count("?") == len(params) for sql, params in registro) and "INFORMATION_SCHEMA.COLUMNS" in registro[0][0]


def test_las_consultas_se_muestran_tal_cual_en_la_pestana_script():
    rutas = [s.ruta for s in generador_bd.scripts()]
    assert rutas == ["SQL · dependencias de los procedimientos (por base)", "SQL · parámetros de los procedimientos (por base)", "SQL · código de los procedimientos (por base)", "SQL · estructura de las tablas que usan (por base)"]
    assert all("{" not in s.codigo for s in generador_bd.scripts())                          # sin marcadores sin resolver


def test_el_codigo_de_los_sp_se_pide_con_parametros_y_se_descartan_los_que_no_se_pueden_ver(monkeypatch):
    sql_vistos = []

    class C:
        def execute(self, sql, *params):
            sql_vistos.append((sql, params))

        description = [("esquema",), ("nombre",), ("definicion",)]

        def fetchall(self):
            return [("com", "A", "CREATE PROCEDURE ..."), ("com", "B", None)]       # B: sin VIEW DEFINITION

        def nextset(self):
            return False

        def close(self):
            pass

    @contextmanager
    def conexion(servidor, base=None, autocommit=True):
        yield type("Conn", (), {"timeout": 0, "cursor": lambda self: C()})()

    monkeypatch.setattr(generador_bd.bd, "conexion_pyodbc", conexion)
    r = generador_bd.cuerpos("mod_rep", [("com", "A"), ("com", "B")])
    assert [x["nombre"] for x in r] == ["A"] and "sys.sql_modules" in sql_vistos[0][0] and sql_vistos[0][1] == ("com", "A", "com", "B")

