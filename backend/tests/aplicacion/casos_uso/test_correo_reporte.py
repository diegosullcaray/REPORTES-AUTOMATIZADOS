"""Correo de archivos generados por Gmail (aplicacion/casos_uso/correo_reporte.py, infraestructura/google/cliente.py): armado, validaciones y destinatarios, sin red."""

import pytest

from aplicacion import dto as e
from aplicacion.casos_uso import correo_reporte as envio_correo
from aplicacion.errores import PeticionInvalida
from infraestructura.google import cliente as g


@pytest.fixture
def excel(tmp_path):
    ruta = tmp_path / "saldo_2026-10-15.xlsx"
    ruta.write_bytes(b"PK-excel")
    return ruta


def test_armar_correo_con_copia_firma_y_adjunto(excel, monkeypatch):
    monkeypatch.delenv("USER_GOOGLE_EMAIL", raising=False)
    msg = g.armar_correo(["ana@x.pe", "luis@x.pe"], ["jefe@x.pe"], "Saldos", "Hola <b>\nAdjunto", "<p>Diego · MIS</p>", [excel])
    assert msg["To"] == "ana@x.pe, luis@x.pe" and msg["Cc"] == "jefe@x.pe"
    html = msg.get_body(preferencelist=("html",)).get_content()
    assert "Hola &lt;b&gt;<br>Adjunto" in html and "<p>Diego · MIS</p>" in html   # el texto va escapado, la firma tal cual
    assert [a.get_filename() for a in msg.iter_attachments()] == ["saldo_2026-10-15.xlsx"]


def test_firma_prefiere_la_direccion_predeterminada(monkeypatch):
    monkeypatch.setattr(g, "_http", lambda *a, **k: {"sendAs": [{"signature": "otra"}, {"isDefault": True, "signature": "<b>mia</b>"}]})
    assert g.firma_gmail("tok") == "<b>mia</b>"
    monkeypatch.setattr(g, "_http", lambda *a, **k: {})
    assert g.firma_gmail("tok") == ""


def test_valida_antes_de_enviar(monkeypatch):
    monkeypatch.setattr(envio_correo, "archivos", lambda nombre: [e.Archivo(nombre="a.xlsx", tipo="excel", tamano=1, modificado="2026-10-15T10:00:00")])
    monkeypatch.setattr(g, "token_de_acceso", lambda: pytest.fail("no debe pedir token si el pedido es inválido"))
    base = dict(para=["ana@x.pe"], asunto="Saldos", archivos=["a.xlsx"])
    for cambio, texto in [({"asunto": " "}, "asunto"), ({"archivos": []}, "archivos"), ({"archivos": ["../.env"]}, "archivo generado"),
                          ({"para": ["roto"]}, "no válido"), ({"para": []}, "al menos")]:
        with pytest.raises(PeticionInvalida, match=texto):
            envio_correo.enviar("saca-tu-garra", e.PedidoEnvioArchivos(**{**base, **cambio}))


def test_prueba_va_solo_a_correo_prueba_sin_copia(monkeypatch, excel):
    monkeypatch.setenv("CORREO_PRUEBA", "yo@x.pe")
    monkeypatch.setattr(envio_correo, "archivos", lambda nombre: [e.Archivo(nombre=excel.name, tipo="excel", tamano=1, modificado="2026-10-15T10:00:00")])
    monkeypatch.setattr(envio_correo, "ruta_descarga", lambda nombre, archivo: excel)
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    monkeypatch.setattr(g, "firma_gmail", lambda token: "<i>firma</i>")
    enviados = []
    monkeypatch.setattr(g, "enviar_mensaje", lambda token, msg: enviados.append(msg) or "id")
    r = envio_correo.enviar("saca-tu-garra", e.PedidoEnvioArchivos(para=["ana@x.pe"], cc=["jefe@x.pe"], asunto="Saldos", archivos=[excel.name], prueba=True))
    assert r.ok and enviados[0]["To"] == "yo@x.pe" and enviados[0]["Cc"] is None and enviados[0]["Subject"] == "[PRUEBA] Saldos"


def test_error_de_google_se_devuelve_sin_romper(monkeypatch, excel):
    monkeypatch.setattr(envio_correo, "archivos", lambda nombre: [e.Archivo(nombre=excel.name, tipo="excel", tamano=1, modificado="2026-10-15T10:00:00")])
    monkeypatch.setattr(envio_correo, "ruta_descarga", lambda nombre, archivo: excel)
    monkeypatch.setattr(g, "token_de_acceso", lambda: (_ for _ in ()).throw(g.GoogleError("no autorizada")))
    r = envio_correo.enviar("saca-tu-garra", e.PedidoEnvioArchivos(para=["ana@x.pe"], asunto="Saldos", archivos=[excel.name]))
    assert not r.ok and "no autorizada" in r.detalle
