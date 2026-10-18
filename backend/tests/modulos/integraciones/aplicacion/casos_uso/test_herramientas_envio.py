"""Herramientas MCP propias de envío (casos_uso/herramientas_envio.py): catálogo según servicios activos y envío por el puerto de Google."""

import json

import pytest

from modulos.integraciones.aplicacion.casos_uso import herramientas_envio
from core.excepciones import ErrorIntegracion
from modulos.integraciones.infraestructura.google import cliente as g


def _nombres(monkeypatch, servicios):
    monkeypatch.setenv("GOOGLE_MCP_SERVICIOS", servicios)
    return [h["name"] for h in herramientas_envio.herramientas()]


def test_el_catalogo_sigue_a_los_servicios_activos(monkeypatch):
    assert _nombres(monkeypatch, "drive") == []
    assert _nombres(monkeypatch, "gmail") == ["enviar_correo"]
    assert _nombres(monkeypatch, "gmail,chat") == ["enviar_correo", "enviar_mensaje_chat", "listar_espacios_chat"]


def test_ejecuta_cada_herramienta_con_el_token_de_la_cuenta(monkeypatch):
    monkeypatch.setenv("USER_GOOGLE_EMAIL", "yo@x.pe")
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


def test_no_envia_fuera_de_la_organizacion_ni_a_otro_que_el_de_prueba(monkeypatch):
    enviados = []
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    monkeypatch.setattr(g, "enviar_correo", lambda *a: enviados.append(a))
    monkeypatch.setattr(g, "enviar_chat", lambda *a: enviados.append(a))
    monkeypatch.setenv("USER_GOOGLE_EMAIL", "yo@x.pe")
    monkeypatch.setenv("CORREO_PRUEBA", "prueba@gmail.com")
    herramientas_envio.ejecutar("enviar_correo", {"para": "ana@x.pe, PRUEBA@gmail.com", "asunto": "a", "cuerpo": "b"})
    herramientas_envio.ejecutar("enviar_mensaje_chat", {"para": "spaces/AAA", "texto": "hola"})
    for para in ("ext@otro.com", "ana@x.pe,ext@otro.com", "ana@x.pe.otro.com"):
        with pytest.raises(ErrorIntegracion, match="no envía fuera"):
            herramientas_envio.ejecutar("enviar_correo", {"para": para, "asunto": "a", "cuerpo": "b"})
    with pytest.raises(ErrorIntegracion, match="no envía fuera"):
        herramientas_envio.ejecutar("enviar_mensaje_chat", {"para": "ext@otro.com", "texto": "hola"})
    assert len(enviados) == 2
