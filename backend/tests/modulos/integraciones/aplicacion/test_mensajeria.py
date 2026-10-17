"""API pública del módulo de integraciones (modulos/integraciones/aplicacion/mensajeria.py): delega en el adaptador de Google."""

from modulos.integraciones.aplicacion import mensajeria
from modulos.integraciones.infraestructura.google import cliente as g


def test_las_funciones_publicas_delegan_en_el_adaptador(monkeypatch):
    llamadas = []
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    monkeypatch.setattr(g, "firma_gmail", lambda token: llamadas.append(("firma", token)) or "<b>yo</b>")
    monkeypatch.setattr(g, "armar_correo", lambda para, cc, asunto, texto, firma="", adjuntos=None: llamadas.append(("armar", para, cc, asunto, firma, adjuntos)) or "msg")
    monkeypatch.setattr(g, "enviar_mensaje", lambda token, msg: llamadas.append(("enviar", token, msg)) or "id")
    monkeypatch.setattr(g, "enviar_chat", lambda token, para, texto, adjuntos=None: llamadas.append(("chat", token, para, texto, adjuntos)) or "ok")
    assert mensajeria.token_de_acceso() == "tok" and mensajeria.firma_gmail("tok") == "<b>yo</b>"
    assert mensajeria.armar_correo(["a@x.pe"], [], "Hola", "texto", "<b>yo</b>", None) == "msg"
    assert mensajeria.enviar_mensaje("tok", "msg") == "id" and mensajeria.enviar_chat("tok", "a@x.pe", "hola") == "ok"
    assert llamadas == [("firma", "tok"), ("armar", ["a@x.pe"], [], "Hola", "<b>yo</b>", None), ("enviar", "tok", "msg"), ("chat", "tok", "a@x.pe", "hola", None)]
