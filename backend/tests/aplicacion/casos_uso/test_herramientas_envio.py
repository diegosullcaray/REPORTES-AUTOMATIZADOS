"""Herramientas MCP propias de envío (casos_uso/herramientas_envio.py): catálogo según servicios activos y envío por el puerto de Google."""

import json

import pytest

from aplicacion.casos_uso import herramientas_envio
from dominio.errores import ErrorIntegracion
from infraestructura.google import cliente as g


def _nombres(monkeypatch, servicios):
    monkeypatch.setenv("GOOGLE_MCP_SERVICIOS", servicios)
    return [h["name"] for h in herramientas_envio.herramientas()]


def test_el_catalogo_sigue_a_los_servicios_activos(monkeypatch):
    assert _nombres(monkeypatch, "drive") == []
    assert _nombres(monkeypatch, "gmail") == ["enviar_correo"]
    assert _nombres(monkeypatch, "gmail,chat") == ["enviar_correo", "enviar_mensaje_chat", "listar_espacios_chat"]


def test_ejecuta_cada_herramienta_con_el_token_de_la_cuenta(monkeypatch):
    enviados = []
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    monkeypatch.setattr(g, "enviar_correo", lambda token, para, asunto, cuerpo: enviados.append(("correo", token, para, asunto, cuerpo)))
    monkeypatch.setattr(g, "enviar_chat", lambda token, para, texto: enviados.append(("chat", token, para, texto)))
    monkeypatch.setattr(g, "espacios_chat", lambda token: [{"name": "spaces/A"}])
    assert "ana@x.pe" in herramientas_envio.ejecutar("enviar_correo", {"para": "ana@x.pe", "asunto": "Hola", "cuerpo": "Texto"})
    assert "ana@x.pe" in herramientas_envio.ejecutar("enviar_mensaje_chat", {"para": "ana@x.pe", "texto": "hola"})
    assert json.loads(herramientas_envio.ejecutar("listar_espacios_chat", {})) == [{"name": "spaces/A"}]
    assert enviados == [("correo", "tok", "ana@x.pe", "Hola", "Texto"), ("chat", "tok", "ana@x.pe", "hola")]


@pytest.mark.parametrize("nombre,argumentos,fragmento", [
    ("enviar_correo", {"para": "a@x.pe"}, "Falta «asunto»"),
    ("enviar_mensaje_chat", {"para": "a@x.pe", "texto": "x" * (herramientas_envio.MAX_TEXTO + 1)}, "supera"),
    ("buscar_archivos", {}, "desconocida"),
])
def test_rechaza_pedidos_invalidos_con_un_error_de_integracion(monkeypatch, nombre, argumentos, fragmento):
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    with pytest.raises(ErrorIntegracion, match=fragmento):
        herramientas_envio.ejecutar(nombre, argumentos)
