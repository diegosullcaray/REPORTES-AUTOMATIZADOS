"""Entrega por Google Chat (reportes/comun/entrega_chat.py): destinatarios del .env y resultado por destinatario, sin red."""

import pytest

from mcp_google import cliente as g
from reportes.comun import entrega_chat


@pytest.fixture
def archivo(tmp_path):
    ruta = tmp_path / "inserts_2026-10-12.txt"
    ruta.write_text("INSERT …;\n", encoding="utf-8")
    return ruta


def test_variable_y_destinatarios(monkeypatch):
    assert entrega_chat.variable("cmg-mora") == "ENTREGA_CHAT_CMG_MORA"
    monkeypatch.setenv("ENTREGA_CHAT_CMG_MORA", " oscar.sanchez@confianza.pe , no-es-correo,ana@x.pe")
    assert entrega_chat.destinatarios("cmg-mora") == ["oscar.sanchez@confianza.pe", "ana@x.pe"]


def test_envia_el_archivo_a_cada_destinatario(monkeypatch, archivo, capsys):
    monkeypatch.setenv("ENTREGA_CHAT_CMG_MORA", "oscar.sanchez@confianza.pe")
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    enviados = []
    monkeypatch.setattr(g, "enviar_chat", lambda token, para, texto, adjuntos: enviados.append((para, [a.name for a in adjuntos])))
    assert entrega_chat.enviar("cmg-mora", [archivo], "hola") is True
    assert enviados == [("oscar.sanchez@confianza.pe", ["inserts_2026-10-12.txt"])]
    assert "✓ Enviado por Google Chat a oscar.sanchez@confianza.pe" in capsys.readouterr().out


def test_sin_destinatarios_o_sin_autorizar_no_envia(monkeypatch, archivo, capsys):
    monkeypatch.delenv("ENTREGA_CHAT_CMG_MORA", raising=False)
    assert entrega_chat.enviar("cmg-mora", [archivo], "hola") is False
    assert "ENTREGA_CHAT_CMG_MORA" in capsys.readouterr().out
    monkeypatch.setenv("ENTREGA_CHAT_CMG_MORA", "oscar.sanchez@confianza.pe")
    monkeypatch.setattr(g, "token_de_acceso", lambda: (_ for _ in ()).throw(g.GoogleError("no autorizada")))
    assert entrega_chat.enviar("cmg-mora", [archivo], "hola") is False


def test_falla_en_un_destinatario(monkeypatch, archivo):
    monkeypatch.setenv("ENTREGA_CHAT_CMG_MORA", "a@x.pe,b@x.pe")
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")

    def enviar(token, para, texto, adjuntos):
        if para == "b@x.pe":
            raise g.GoogleError("403")
    monkeypatch.setattr(g, "enviar_chat", enviar)
    assert entrega_chat.enviar("cmg-mora", [archivo], "hola") is False


def test_archivo_inexistente(monkeypatch, tmp_path):
    monkeypatch.setenv("ENTREGA_CHAT_CMG_MORA", "a@x.pe")
    assert entrega_chat.enviar("cmg-mora", [tmp_path / "no.txt"], "hola") is False
