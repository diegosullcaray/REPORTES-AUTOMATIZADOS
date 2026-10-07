"""Casos de uso de la web: las reglas de cada reporte se validan antes de encolar (no toca las bases reales)."""

from datetime import date

import pytest

from api import servicios
from api.esquemas import PedidoEjecucion


def test_mensual_exige_fin_de_mes():
    with pytest.raises(servicios.PeticionInvalida, match="fin de mes"):
        servicios.argumentos(PedidoEjecucion(reporte="saca-tu-garra", fecha_corte=date(2026, 6, 15)))


def test_corte_futuro_se_rechaza():
    with pytest.raises(servicios.PeticionInvalida, match="futuro"):
        servicios.argumentos(PedidoEjecucion(reporte="saca-tu-garra", fecha_corte=date(2999, 1, 31)))


def test_escritura_en_bd_exige_confirmacion():
    pedido = PedidoEjecucion(reporte="tapp-saldo-medio-territorio", fecha_corte=date(2026, 6, 30))
    with pytest.raises(servicios.PeticionInvalida, match="confirma"):
        servicios.argumentos(pedido)
    pedido.confirmar_escritura = True
    assert "--confirmar-escritura" in servicios.argumentos(pedido)


def test_envio_a_todos_exige_conforme():
    with pytest.raises(servicios.PeticionInvalida, match="confirmar"):
        servicios.argumentos(PedidoEjecucion(reporte="cartera-sin-asignar", fecha_corte=date(2026, 6, 30), correo="todos"))


def test_envio_a_todos_exige_prueba_previa():
    with pytest.raises(servicios.PeticionInvalida, match="prueba"):
        servicios.argumentos(PedidoEjecucion(reporte="cartera-sin-asignar", fecha_corte=date(2000, 1, 3), correo="todos", conforme=True))


def test_logica_propia_recibe_mes_o_fecha():
    assert servicios.argumentos(PedidoEjecucion(reporte="indicadores-clientes", fecha_corte=date(2026, 6, 30))) == ["indicadores-clientes", "--mes", "2026-06"]
    assert servicios.argumentos(PedidoEjecucion(reporte="bancarizados", fecha_corte=date(2026, 6, 30)))[1:] == ["--fecha-corte", "2026-06-30"]
    with pytest.raises(servicios.PeticionInvalida, match="lógica propia"):
        servicios.argumentos(PedidoEjecucion(reporte="bancarizados", fecha_corte=date(2026, 6, 30), forzar=True))


def test_archivo_fuera_de_la_carpeta_no_se_sirve():
    with pytest.raises(servicios.NoEncontrado):
        servicios.ruta_descarga("saca-tu-garra", "../../../.env")


def test_vista_previa_de_excel(tmp_path, monkeypatch):
    import pandas as pd

    monkeypatch.setattr(servicios, "carpeta_salida", lambda _: tmp_path)
    pd.DataFrame({"A": range(250), "B": ["x"] * 250}).to_excel(tmp_path / "r.xlsx", index=False, sheet_name="Datos")
    v = servicios.vista_previa("saca-tu-garra", "r.xlsx")
    hoja = v.hojas[0]
    assert (hoja.nombre, hoja.columnas, hoja.total_filas, len(hoja.filas)) == ("Datos", ["A", "B"], 250, servicios.FILAS_VISTA_PREVIA)
