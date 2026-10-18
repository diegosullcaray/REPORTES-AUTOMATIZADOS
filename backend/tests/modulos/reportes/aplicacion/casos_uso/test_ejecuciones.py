"""Casos de uso de ejecuciones: las reglas de cada reporte se validan antes de encolar (no toca las bases reales)."""

from datetime import date

import pytest

from modulos.reportes.aplicacion.casos_uso import ejecuciones
from modulos.reportes.aplicacion.dto import PedidoEjecucion
from core.excepciones import PeticionInvalida


def test_mensual_exige_fin_de_mes():
    with pytest.raises(PeticionInvalida, match="fin de mes"):
        ejecuciones.argumentos(PedidoEjecucion(reporte="saca-tu-garra", fecha_corte=date(2026, 6, 15)))


def test_corte_futuro_se_rechaza():
    with pytest.raises(PeticionInvalida, match="futuro"):
        ejecuciones.argumentos(PedidoEjecucion(reporte="saca-tu-garra", fecha_corte=date(2999, 1, 31)))


def test_escritura_en_bd_exige_confirmacion():
    pedido = PedidoEjecucion(reporte="tapp-saldo-medio-territorio", fecha_corte=date(2026, 6, 30))
    with pytest.raises(PeticionInvalida, match="confirma"):
        ejecuciones.argumentos(pedido)
    pedido.confirmar_escritura = True
    assert "--confirmar-escritura" in ejecuciones.argumentos(pedido)


def test_envio_a_todos_exige_conforme():
    with pytest.raises(PeticionInvalida, match="confirmar"):
        ejecuciones.argumentos(PedidoEjecucion(reporte="cartera-sin-asignar", fecha_corte=date(2026, 6, 30), correo="todos"))


def test_envio_a_todos_exige_prueba_previa():
    with pytest.raises(PeticionInvalida, match="prueba"):
        ejecuciones.argumentos(PedidoEjecucion(reporte="cartera-sin-asignar", fecha_corte=date(2000, 1, 3), correo="todos", conforme=True))


def test_logica_propia_recibe_mes_o_fecha():
    assert ejecuciones.argumentos(PedidoEjecucion(reporte="indicadores-clientes", fecha_corte=date(2026, 6, 30))) == ["indicadores-clientes", "--mes", "2026-06"]
    assert ejecuciones.argumentos(PedidoEjecucion(reporte="bancarizados", fecha_corte=date(2026, 6, 30)))[1:] == ["--fecha-corte", "2026-06-30"]
    with pytest.raises(PeticionInvalida, match="lógica propia"):
        ejecuciones.argumentos(PedidoEjecucion(reporte="bancarizados", fecha_corte=date(2026, 6, 30), forzar=True))


def test_cmg_mora_con_chat_exige_destinatario(monkeypatch):
    pedido = PedidoEjecucion(reporte="cmg-mora", fecha_corte=date(2026, 10, 7), chat=True)
    monkeypatch.delenv("ENTREGA_CHAT_CMG_MORA", raising=False)
    with pytest.raises(PeticionInvalida, match="Google Chat"):
        ejecuciones.argumentos(pedido)
    monkeypatch.setenv("ENTREGA_CHAT_CMG_MORA", "oscar.sanchez@confianza.pe")
    assert ejecuciones.argumentos(pedido) == ["cmg-mora", "--fecha-corte", "2026-10-07", "--chat"]
    with pytest.raises(PeticionInvalida, match="no envía"):
        ejecuciones.argumentos(PedidoEjecucion(reporte="saca-tu-garra", fecha_corte=date(2026, 6, 30), chat=True))


def test_reporte_con_la_plantilla_sin_completar_no_se_ejecuta(monkeypatch):
    from types import SimpleNamespace

    from modulos.reportes.aplicacion.nuevo_reporte import PLANTILLA_SQL

    monkeypatch.setattr(ejecuciones, "lote", lambda _: SimpleNamespace(sql=PLANTILLA_SQL, escribe_en_bd=False, entrega=None))
    with pytest.raises(PeticionInvalida, match="Completa el T-SQL"):
        ejecuciones.argumentos(PedidoEjecucion(reporte="saca-tu-garra", fecha_corte=date(2026, 6, 30)))
