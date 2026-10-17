"""Catálogo de reportes: a quién se envía el archivo por Google Chat (se guarda en el .env)."""

import pytest

from modulos.reportes.aplicacion.casos_uso import catalogo
from modulos.reportes.aplicacion.dto import PedidoChat
from core.excepciones import PeticionInvalida
from core import entorno


def test_guardar_destinatarios_de_chat(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("RCC_PASSWORD=x\n", encoding="utf-8")
    monkeypatch.setattr(entorno, "ENV", env)
    monkeypatch.delenv("ENTREGA_CHAT_CMG_MORA", raising=False)
    d = catalogo.guardar_chat("cmg-mora", PedidoChat(destinatarios=" oscar.sanchez@confianza.pe , oscar.sanchez@confianza.pe"))
    assert d.envia_chat and d.chat_destinatarios == ["oscar.sanchez@confianza.pe"]
    assert "ENTREGA_CHAT_CMG_MORA=oscar.sanchez@confianza.pe" in env.read_text(encoding="utf-8")
    with pytest.raises(PeticionInvalida, match="no válido"):
        catalogo.guardar_chat("cmg-mora", PedidoChat(destinatarios="oscar"))
    assert catalogo.guardar_chat("cmg-mora", PedidoChat(destinatarios="")).chat_destinatarios == []
    monkeypatch.delenv("ENTREGA_CHAT_CMG_MORA", raising=False)
