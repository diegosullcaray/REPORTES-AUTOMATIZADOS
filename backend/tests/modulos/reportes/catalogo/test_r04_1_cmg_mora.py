"""CMG Mora: abortar o fallar nunca se presenta como éxito (código de salida distinto de 0). La BD se simula."""

import datetime

from modulos.reportes.catalogo.diarios import r04_1_cmg_mora as mora

CORTE = datetime.date(2026, 10, 7)


class Cursor:
    def __init__(self, filas, falla):
        self.filas, self.falla = list(filas), falla

    def execute(self, *_):
        if self.falla:
            raise RuntimeError("SQL caído")

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


def correr(monkeypatch, tmp_path, filas, falla=False):
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion(filas, falla))
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    return mora.generar_inserts_sql(CORTE)


def test_con_datos_y_provisiones_genera_el_txt(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (1,), (10.0, 20.0)]) == 0
    assert (tmp_path / "inserts_2026-10-07.txt").exists()


def test_provisiones_en_cero_aborta_con_error(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (1,), (0, 20.0)]) == 1
    assert not list(tmp_path.glob("*.txt"))


def test_sin_recaudo_del_dia_aborta_con_error(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(0,)]) == 1


def test_tabla_de_provisiones_ausente_aborta_con_error(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [(5,), (None,)]) == 1


def test_un_error_sql_es_error_y_no_exito(monkeypatch, tmp_path):
    assert correr(monkeypatch, tmp_path, [], falla=True) == 1


def test_con_chat_envia_el_txt_del_dia(monkeypatch, tmp_path):
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion([(5,), (1,), (10.0, 20.0)]))
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    enviados = []
    monkeypatch.setattr(mora.entrega_chat, "enviar", lambda reporte, archivos, texto: enviados.append((reporte, [a.name for a in archivos])) or True)
    assert mora.main(["--fecha-corte", "2026-10-07", "--chat"]) == 0
    assert enviados == [("cmg-mora", ["inserts_2026-10-07.txt"])]


def test_chat_que_falla_deja_el_txt_y_termina_en_error(monkeypatch, tmp_path):
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion([(5,), (1,), (10.0, 20.0)]))
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    monkeypatch.setattr(mora.entrega_chat, "enviar", lambda *a: False)
    assert mora.main(["--fecha-corte", "2026-10-07", "--chat"]) == 1
    assert (tmp_path / "inserts_2026-10-07.txt").exists()


def test_sin_chat_no_envia_y_si_falla_la_generacion_tampoco(monkeypatch, tmp_path):
    enviados = []
    monkeypatch.setattr(mora.entrega_chat, "enviar", lambda *a: enviados.append(a) or True)
    monkeypatch.setattr(mora, "carpeta_salida", lambda _n: str(tmp_path))
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion([(5,), (1,), (10.0, 20.0)]))
    assert mora.main(["--fecha-corte", "2026-10-07"]) == 0
    monkeypatch.setattr(mora, "conexion_pyodbc", lambda *_a, **_k: Conexion([(0,)]))
    assert mora.main(["--fecha-corte", "2026-10-07", "--chat"]) == 1
    assert enviados == []
