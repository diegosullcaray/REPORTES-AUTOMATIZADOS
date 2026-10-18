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


def test_script_no_puede_declararse_creado_desde_la_web(tmp_path, monkeypatch):
    from modulos.reportes.aplicacion.dto import PedidoScript

    archivo = tmp_path / "r.py"
    archivo.write_text('"""Reporte del legado."""\n', encoding="utf-8")
    monkeypatch.setattr(catalogo, "_archivo_script", lambda _: archivo)
    with pytest.raises(PeticionInvalida, match="creados así"):
        catalogo.guardar_script("saca-tu-garra", PedidoScript(codigo='"""Creado desde la web."""\n'))
    assert catalogo.guardar_script("saca-tu-garra", PedidoScript(codigo='"""Otro texto."""\n')).codigo.startswith('"""Otro')


def test_script_de_reporte_web_no_puede_escribir_en_la_base(tmp_path, monkeypatch):
    from modulos.reportes.aplicacion.dto import PedidoScript

    archivo = tmp_path / "r.py"
    archivo.write_text('"""Creado desde la web."""\n', encoding="utf-8")
    monkeypatch.setattr(catalogo, "_archivo_script", lambda _: archivo)
    with pytest.raises(PeticionInvalida, match="solo lee"):
        catalogo.guardar_script("saca-tu-garra", PedidoScript(codigo='"""Creado desde la web."""\nSQL = r"""\ndelete from dbo.t\n"""\n'))
