"""Cartera sin asignar: Excel + imagen + correo de prueba -> conforme -> todos (sin enviar nada real)."""

import smtplib
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from reportes import config
from reportes.comun import correo, ejecutor
from reportes.comun.fechas import resolver_corte
from reportes.diarios.r02_cartera_sin_asignar import REPORTE
from reportes.verificacion import Estado, Resultado
from reportes.tablas import Tabla

FECHA = ["--fecha-corte", "2026-10-05"]


class FakeSMTP:
    enviados: list = []
    login_con: list = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port = host, port

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def login(self, usuario, clave):
        FakeSMTP.login_con.append((usuario, clave))

    def send_message(self, msg, from_addr=None, to_addrs=None):
        FakeSMTP.enviados.append((msg, list(to_addrs)))


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    FakeSMTP.enviados, FakeSMTP.login_con = [], []
    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSMTP)
    monkeypatch.setattr(config, "DIR_OUTPUTS", tmp_path / "outputs")
    monkeypatch.setattr(ejecutor, "DIR_OUTPUTS", tmp_path / "outputs")
    for k, v in {"SMTP_USER": "mis@confianza.pe", "SMTP_PASSWORD": "clave-de-prueba", "CORREO_PRUEBA": "diego.sullcaray@confianza.pe"}.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("GOOGLE_CHAT_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("LOGO_PATH", raising=False)
    monkeypatch.delenv("FECHA_CORTE_DIARIA", raising=False)
    lista = tmp_path / "correos.txt"
    lista.write_text("# destinatarios\na@confianza.pe\nb@confianza.pe\nA@confianza.pe\n\nc@confianza.pe\n", encoding="utf-8")
    monkeypatch.setenv("CORREOS_SIN_ASIGNAR_ARCHIVO", str(lista))
    t = Tabla("storage.com_act.hcda001", "historica", "HFECPRO", "confirmada")
    monkeypatch.setattr(ejecutor, "verificar_reporte", lambda c, f: [Resultado(t, Estado.OK, f)])
    df = pd.DataFrame({"NIVEL": ["FC", "FC"], "Asesor_Operativo": ["--", "--"], "Cuenta_Cliente": [1, 2], "Nom_Cliente": ["A", "B"],
                       "Operacion": [10, 11], "Saldo_Capital": [100.0, 50.5], "Grupo": ["GRUPAL", "INDIVIDUAL"], "Territorio": ["LIMA", "NULL"],
                       "Corredor": ["LIMA ESTE", None], "Agencia_Cli": ["AG ATE", "AG X"], "Unidad_Negocio": ["U1", "U2"]})
    monkeypatch.setattr(ejecutor, "ejecutar_lote", lambda s, sql, base=None: [df])
    return tmp_path


def test_destinatarios_sin_duplicados_ni_comentarios(entorno):
    assert correo.leer_destinatarios() == ["a@confianza.pe", "b@confianza.pe", "c@confianza.pe"]


def test_el_dia_por_defecto_es_siempre_ayer_aunque_sea_lunes():
    assert resolver_corte("diaria", hoy=date(2026, 10, 5), lunes_sabado=False)[0] == date(2026, 10, 4)   # lunes -> domingo (Date - 1)
    assert resolver_corte("diaria", hoy=date(2026, 10, 5))[0] == date(2026, 10, 3)                       # regla de CMG Mora


def test_por_defecto_envia_solo_una_prueba_al_correo_de_prueba(entorno, capsys):
    assert ejecutor.correr(REPORTE, FECHA) == ejecutor.SALIDA_OK
    assert len(FakeSMTP.enviados) == 1
    msg, para = FakeSMTP.enviados[0]
    assert para == ["diego.sullcaray@confianza.pe"]
    assert msg["Subject"] == "[PRUEBA] Reporte Sin Asignar - 2026-10-05"
    assert FakeSMTP.login_con == [("mis@confianza.pe", "clave-de-prueba")]
    adjuntos = [p.get_filename() for p in msg.walk() if p.get_filename()]
    assert "Cartera-Sin asignar-2026-10-05.xlsx" in adjuntos and "Reporte_Temporal_2026-10-05.jpg" in adjuntos
    assert "cid:Reporte_Temporal.jpg" in msg.get_body(("html",)).get_content()
    assert "clave-de-prueba" not in capsys.readouterr().out                    # la contraseña nunca se imprime
    assert (entorno / "outputs" / "diarias" / "02_cartera_sin_asignar" / "estado_envio_20261005.json").exists()


def test_correo_no_solo_genera_el_excel(entorno):
    assert ejecutor.correr(REPORTE, FECHA + ["--correo", "no"]) == ejecutor.SALIDA_OK
    assert FakeSMTP.enviados == []


def test_todos_exige_conforme(entorno, capsys):
    assert ejecutor.correr(REPORTE, FECHA) == 0
    FakeSMTP.enviados.clear()
    assert ejecutor.correr(REPORTE, FECHA + ["--correo", "todos"]) == ejecutor.SALIDA_CONFIG
    assert "--conforme" in capsys.readouterr().out and FakeSMTP.enviados == []


def test_todos_exige_una_prueba_previa(entorno, capsys):
    assert ejecutor.correr(REPORTE, FECHA + ["--correo", "todos", "--conforme"]) == ejecutor.SALIDA_CONFIG
    assert "prueba" in capsys.readouterr().out and FakeSMTP.enviados == []


def test_todos_envia_la_prueba_aprobada_a_toda_la_lista_sin_consultar_de_nuevo(entorno, monkeypatch):
    assert ejecutor.correr(REPORTE, FECHA) == 0
    FakeSMTP.enviados.clear()
    monkeypatch.setattr(ejecutor, "ejecutar_lote", lambda *a, **k: pytest.fail("no debe volver a consultar la base"))
    avisos = []
    monkeypatch.setenv("GOOGLE_CHAT_WEBHOOK_URL", "https://chat.example/webhook")
    monkeypatch.setattr(correo, "notificar_chat", lambda url, texto: avisos.append((url, texto)))
    assert ejecutor.correr(REPORTE, FECHA + ["--correo", "todos", "--conforme"]) == ejecutor.SALIDA_OK
    (msg, para), = FakeSMTP.enviados
    assert para == ["a@confianza.pe", "b@confianza.pe", "c@confianza.pe"]
    assert msg["Subject"] == "Reporte Sin Asignar - 2026-10-05" and "CORREO DE PRUEBA" not in msg.get_body(("html",)).get_content()
    assert len(avisos) == 1 and "REPORTE GENERADO Y ENVIADO" in avisos[0][1] and "Cartera-Sin asignar-2026-10-05.xlsx" in avisos[0][1]


def test_no_se_envia_dos_veces_a_todos_sin_reenviar(entorno, capsys):
    ejecutor.correr(REPORTE, FECHA)
    assert ejecutor.correr(REPORTE, FECHA + ["--correo", "todos", "--conforme"]) == 0
    FakeSMTP.enviados.clear()
    assert ejecutor.correr(REPORTE, FECHA + ["--correo", "todos", "--conforme"]) == ejecutor.SALIDA_CONFIG
    assert "--reenviar" in capsys.readouterr().out and FakeSMTP.enviados == []
    assert ejecutor.correr(REPORTE, FECHA + ["--correo", "todos", "--conforme", "--reenviar"]) == 0


def test_sin_credenciales_el_excel_se_genera_y_el_correo_no(entorno, monkeypatch, capsys):
    monkeypatch.delenv("SMTP_PASSWORD")
    assert ejecutor.correr(REPORTE, FECHA) == ejecutor.SALIDA_CONFIG
    salida = capsys.readouterr().out
    assert "SMTP_PASSWORD" in salida and "El Excel se generó" in salida and FakeSMTP.enviados == []
    assert list((entorno / "outputs" / "diarias" / "02_cartera_sin_asignar").glob("*.xlsx"))


def test_rechazo_de_la_cuenta_se_informa_sin_traza(entorno, monkeypatch, capsys):
    def falla(self, usuario, clave):
        raise smtplib.SMTPAuthenticationError(535, b"bad credentials")

    monkeypatch.setattr(FakeSMTP, "login", falla)
    assert ejecutor.correr(REPORTE, FECHA) == ejecutor.SALIDA_ERROR
    assert "rechazó la cuenta MIS" in capsys.readouterr().out


def test_el_codigo_no_trae_secretos():
    texto = "\n".join(p.read_text(encoding="utf-8") for p in (Path(__file__).resolve().parents[1] / "src").rglob("*.py"))
    assert "smtp.gmail.com" in texto and "chat.googleapis.com" not in texto and "AIzaSy" not in texto
