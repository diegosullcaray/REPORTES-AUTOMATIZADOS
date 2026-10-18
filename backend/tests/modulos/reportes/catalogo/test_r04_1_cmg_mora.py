"""CMG Mora: abortar o fallar nunca se presenta como éxito (código de salida distinto de 0). La BD se simula."""

import datetime

from modulos.reportes.catalogo.diarios import r04_1_cmg_mora as mora

CORTE = datetime.date(2026, 10, 7)

# Orden de lecturas: recaudo (conteo), gasto, OBJECT_ID de PROV_PROY, suma de provisiones
COMPLETO = [(5,), (20.0,), (1,), (10.0,)]


class Cursor:
    description = [("SFECPRO",), ("STIPCOD",)]

    def __init__(self, filas, falla):
        self.filas, self.falla = list(filas), falla

    def execute(self, *_):
        if self.falla:
            raise RuntimeError("SQL caído")

    def executemany(self, *_):
        pass

    def fetchone(self):
        return self.filas.pop(0)

    def fetchall(self):
        return [("INSERT INTO t VALUES (1);",)]


class Conexion:
    def __init__(self, filas, falla=False):
        self.cursor_ = Cursor(filas, falla)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def cursor(self):
        return self.cursor_


def correr(monkeypatch, tmp_path, filas, falla=False, fase=None):
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion(filas, falla))
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    return mora.generar_inserts_sql(CORTE, fase)


def test_con_datos_y_provisiones_genera_el_txt(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, COMPLETO) == 0
    assert (tmp_path / "inserts_2026-10-07.txt").exists()


def test_provisiones_en_cero_aborta_con_error(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (20.0,), (1,), (0,)]) == 1
    assert not list(tmp_path.glob("*.txt"))


def test_gasto_en_cero_aborta_con_error(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (0,), (1,), (10.0,)]) == 1


def test_sin_recaudo_del_dia_aborta_con_error(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(0,)]) == 1


def test_tabla_de_provisiones_ausente_aborta_con_error(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (20.0,), (None,)]) == 1


def test_un_error_sql_es_error_y_no_exito(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [], falla=True) == 1


def test_flujo_por_fases_deja_dos_excel_y_luego_los_inserts(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (20.0,)], fase="operaciones") == 0
    assert correr(monkeypatch, tmp_path, [(1,), (10.0,)], fase="provisiones") == 0
    assert (tmp_path / "operaciones_2026-10-07.xlsx").exists() and (tmp_path / "provisiones_2026-10-07.xlsx").exists()
    assert correr(monkeypatch, tmp_path, [], fase="generar") == 0
    assert (tmp_path / "inserts_2026-10-07.txt").exists()


def test_provisiones_aun_sin_cargar_no_deja_excel(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(None,)], fase="provisiones") == 1
    assert not list(tmp_path.glob("*.xlsx"))


def test_generar_sin_los_dos_excel_falla(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (20.0,)], fase="operaciones") == 0
    assert correr(monkeypatch, tmp_path, [], fase="generar") == 1  # falta provisiones_*.xlsx


def test_con_chat_envia_el_txt_del_dia(monkeypatch, tmp_path):
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion(list(COMPLETO)))
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    enviados = []
    monkeypatch.setattr(mora.entrega_chat, "enviar", lambda reporte, archivos, texto: enviados.append((reporte, [a.name for a in archivos])) or True)
    assert mora.main(["--fecha-corte", "2026-10-07", "--chat"]) == 0
    assert enviados == [("cmg-mora", ["inserts_2026-10-07.txt"])]


def test_chat_que_falla_deja_el_txt_y_termina_en_error(monkeypatch, tmp_path):
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion(list(COMPLETO)))
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    monkeypatch.setattr(mora.entrega_chat, "enviar", lambda *a: False)
    assert mora.main(["--fecha-corte", "2026-10-07", "--chat"]) == 1
    assert (tmp_path / "inserts_2026-10-07.txt").exists()


def test_sin_chat_no_envia_y_si_falla_la_generacion_tampoco(monkeypatch, tmp_path):
    enviados = []
    monkeypatch.setattr(mora.entrega_chat, "enviar", lambda *a: enviados.append(a) or True)
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion(list(COMPLETO)))
    assert mora.main(["--fecha-corte", "2026-10-07"]) == 0
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion([(0,)]))
    assert mora.main(["--fecha-corte", "2026-10-07", "--chat"]) == 1
    assert enviados == []
