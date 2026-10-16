"""Listas de correos de entrega (aplicacion/destinatarios.py): lectura del .env por el puerto y validación al guardar."""

import pytest

from aplicacion import destinatarios
from aplicacion.errores import PeticionInvalida
from infraestructura import entorno


def test_lee_solo_los_correos_validos(monkeypatch):
    monkeypatch.setenv("ENTREGA_CHAT_X", " ana@x.pe , roto,luis@x.pe")
    assert destinatarios.leer("ENTREGA_CHAT_X") == ["ana@x.pe", "luis@x.pe"]
    monkeypatch.delenv("ENTREGA_CHAT_X")
    assert destinatarios.leer("ENTREGA_CHAT_X") == []


def test_normaliza_quita_repetidos_y_valida():
    assert destinatarios.normalizar(" ana@x.pe, ana@x.pe ,luis@x.pe") == ["ana@x.pe", "luis@x.pe"]
    with pytest.raises(PeticionInvalida, match="no válido"):
        destinatarios.normalizar("roto")
    with pytest.raises(PeticionInvalida, match="Máximo 2"):
        destinatarios.normalizar("a@x.pe,b@x.pe,c@x.pe", maximo=2)


def test_guardar_escribe_en_el_env_y_en_el_proceso(tmp_path, monkeypatch):
    monkeypatch.setattr(entorno, "ENV", tmp_path / ".env")
    monkeypatch.delenv("ENTREGA_CHAT_X", raising=False)
    assert destinatarios.guardar("ENTREGA_CHAT_X", "ana@x.pe, ana@x.pe") == ["ana@x.pe"]
    assert "ENTREGA_CHAT_X=ana@x.pe" in (tmp_path / ".env").read_text(encoding="utf-8")
    assert destinatarios.leer("ENTREGA_CHAT_X") == ["ana@x.pe"]
    destinatarios.guardar("ENTREGA_CHAT_X", "")
    assert destinatarios.leer("ENTREGA_CHAT_X") == []
