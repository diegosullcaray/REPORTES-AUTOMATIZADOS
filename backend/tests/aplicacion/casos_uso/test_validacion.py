"""Historial de la validación masiva y envío del mensaje por Google Chat (aplicacion/casos_uso/validacion.py), sin red ni bases de datos."""

from datetime import date

import pytest

from aplicacion import dto as e
from aplicacion.casos_uso import validacion
from aplicacion.errores import NoEncontrado, PeticionInvalida
from infraestructura import entorno, historial_validacion
from infraestructura.google import cliente as g


@pytest.fixture(autouse=True)
def aislado(tmp_path, monkeypatch):
    monkeypatch.setattr(historial_validacion, "DIR", tmp_path / "validaciones")
    monkeypatch.setattr(entorno, "ENV", tmp_path / ".env")
    monkeypatch.delenv("ENTREGA_CHAT_VALIDACION_PIERO", raising=False)


def verificacion(listo: bool, solicitud: str | None = "Por favor actualicen las tablas.", grupo: str = "piero") -> e.VerificacionGrupo:
    tabla = lambda nombre, estado: e.TablaValidada(nombre=nombre, servidor="mish", estado=estado, ultima_fecha=None, detalle="", reportes=["r1"])
    tablas = [tabla("A", "OK"), tabla("B", "OK" if listo else "DESACTUALIZADA"), tabla("C", "ERROR")]
    return e.VerificacionGrupo(grupo=grupo, titulo="Heredados", corte=date(2026, 9, 30), listo=listo,
                               reportes=[e.ResumenValidacion(nombre="r1", orden="01", tablas=3, pendientes=0 if listo else 1, dudosas=1, listo=listo)],
                               tablas=tablas, problemas=[], solicitud=solicitud)


def test_registra_y_lista_de_la_mas_reciente_a_la_mas_antigua():
    primera, segunda = validacion.registrar(verificacion(False)), validacion.registrar(verificacion(True, None))
    h = validacion.historial("piero")
    assert [x.id for x in h] == [segunda.id, primera.id]
    assert (h[1].tablas_total, h[1].tablas_ok, h[1].tablas_pendientes, h[1].tablas_dudosas) == (3, 1, 1, 1)
    assert validacion.historial("piero", 1)[0].id == segunda.id and validacion.historial("erick") == []


def test_poda_las_fichas_mas_antiguas(monkeypatch):
    monkeypatch.setattr(validacion, "MAX_FICHAS", 2)
    ids = [validacion.registrar(verificacion(False)).id for _ in range(3)]
    assert [x.id for x in validacion.historial("piero")] == [ids[2], ids[1]]


def test_grupo_desconocido_no_toca_el_disco():
    with pytest.raises(NoEncontrado):
        validacion.historial("../../x")


def test_guarda_destinatarios_en_el_env_y_valida_los_correos():
    r = validacion.guardar_destinos("piero", e.PedidoChat(destinatarios=" ana@x.pe, ana@x.pe ,luis@x.pe"))
    assert r.destinatarios == ["ana@x.pe", "luis@x.pe"]
    assert "ENTREGA_CHAT_VALIDACION_PIERO=ana@x.pe,luis@x.pe" in entorno.ENV.read_text(encoding="utf-8")
    with pytest.raises(PeticionInvalida, match="no válido"):
        validacion.guardar_destinos("piero", e.PedidoChat(destinatarios="roto"))
    assert validacion.guardar_destinos("piero", e.PedidoChat(destinatarios="")).destinatarios == []


def test_envia_el_mensaje_de_la_ultima_verificacion_y_lo_marca(monkeypatch):
    validacion.guardar_destinos("piero", e.PedidoChat(destinatarios="ana@x.pe,luis@x.pe"))
    validacion.registrar(verificacion(False, "Mensaje para Producción"))
    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    enviados = []
    monkeypatch.setattr(g, "enviar_chat", lambda token, para, texto, adjuntos=None: enviados.append((para, texto)))
    r = validacion.enviar_chat("piero")
    assert r.ok and enviados == [("ana@x.pe", "Mensaje para Producción"), ("luis@x.pe", "Mensaje para Producción")]
    ultima = validacion.historial("piero", 1)[0]
    assert ultima.chat_a == ["ana@x.pe", "luis@x.pe"] and ultima.chat_enviado


def test_si_un_compañero_falla_se_informa_y_los_demas_reciben(monkeypatch):
    validacion.guardar_destinos("piero", e.PedidoChat(destinatarios="ana@x.pe,luis@x.pe"))
    validacion.registrar(verificacion(False))

    def enviar(token, para, texto, adjuntos=None):
        if para == "ana@x.pe":
            raise g.GoogleError("sin acceso")

    monkeypatch.setattr(g, "token_de_acceso", lambda: "tok")
    monkeypatch.setattr(g, "enviar_chat", enviar)
    r = validacion.enviar_chat("piero")
    assert not r.ok and "luis@x.pe" in r.detalle and "ana@x.pe: sin acceso" in r.detalle
    assert validacion.historial("piero", 1)[0].chat_a == ["luis@x.pe"]


def test_no_envia_sin_mensaje_sin_destinatarios_o_demasiado_largo(monkeypatch):
    monkeypatch.setattr(g, "token_de_acceso", lambda: pytest.fail("no debe pedir token"))
    with pytest.raises(PeticionInvalida, match="verifica primero"):
        validacion.enviar_chat("piero")
    validacion.registrar(verificacion(True, None))
    with pytest.raises(PeticionInvalida, match="verifica primero"):
        validacion.enviar_chat("piero")
    validacion.registrar(verificacion(False, "x" * (validacion.MAX_CHAT + 1)))
    with pytest.raises(PeticionInvalida, match="caracteres"):
        validacion.enviar_chat("piero")
    validacion.registrar(verificacion(False))
    with pytest.raises(PeticionInvalida, match="a quién"):
        validacion.enviar_chat("piero")
