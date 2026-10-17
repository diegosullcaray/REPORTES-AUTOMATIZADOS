"""API pública del módulo de notificaciones (modulos/notificaciones/aplicacion/correo.py): delega en el adaptador de correo."""

from modulos.notificaciones.aplicacion import correo
from modulos.notificaciones.infraestructura import correo_smtp


def test_las_funciones_publicas_delegan_en_el_adaptador(monkeypatch):
    llamadas = []
    monkeypatch.setattr(correo_smtp, "config_desde_env", lambda: llamadas.append("config") or "cfg")
    monkeypatch.setattr(correo_smtp, "leer_destinatarios", lambda ruta=None: llamadas.append(("lista", ruta)) or ["a@x.pe"])
    monkeypatch.setattr(correo_smtp, "construir_mensaje", lambda cfg, asunto, html, para, **op: llamadas.append(("msg", cfg, asunto, para, op)) or "mensaje")
    monkeypatch.setattr(correo_smtp, "enviar", lambda cfg, msg, para: llamadas.append(("envio", cfg, msg, para)))
    monkeypatch.setattr(correo_smtp, "notificar_chat", lambda url, texto: llamadas.append(("chat", url, texto)))
    assert correo.config_desde_env() == "cfg" and correo.leer_destinatarios() == ["a@x.pe"]
    assert correo.construir_mensaje("cfg", "Asunto", "<p>x</p>", ["a@x.pe"], en_linea={}) == "mensaje"
    correo.enviar("cfg", "mensaje", ["a@x.pe"])
    correo.notificar_chat("https://chat", "hola")
    assert llamadas == ["config", ("lista", None), ("msg", "cfg", "Asunto", ["a@x.pe"], {"en_linea": {}}), ("envio", "cfg", "mensaje", ["a@x.pe"]), ("chat", "https://chat", "hola")]
