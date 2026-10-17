"""Archivos generados por cada reporte: descarga segura, listado y vista previa."""

import pytest

from modulos.reportes.aplicacion.casos_uso import archivos
from core.excepciones import NoEncontrado
from modulos.reportes.infraestructura import cola_ejecuciones


def test_archivo_fuera_de_la_carpeta_no_se_sirve():
    with pytest.raises(NoEncontrado):
        archivos.ruta_descarga("saca-tu-garra", "../../../.env")


def test_vista_previa_de_excel(tmp_path, monkeypatch):
    import pandas as pd

    monkeypatch.setattr(archivos, "carpeta_salida", lambda _: tmp_path)
    pd.DataFrame({"A": range(250), "B": ["x"] * 250}).to_excel(tmp_path / "r.xlsx", index=False, sheet_name="Datos")
    v = archivos.vista_previa("saca-tu-garra", "r.xlsx")
    hoja = v.hojas[0]
    assert (hoja.nombre, hoja.columnas, hoja.total_filas, len(hoja.filas)) == ("Datos", ["A", "B"], 250, archivos.FILAS_VISTA_PREVIA)


def test_archivos_solo_muestra_lo_generado(tmp_path, monkeypatch):
    """El estado_envio_*.json del correo es interno: no aparece entre los archivos ni en las ejecuciones."""
    monkeypatch.setattr(archivos, "carpeta_salida", lambda _: tmp_path)
    for nombre in ("cartera.xlsx", "resumen.png", "estado_envio_20261012.json", "~$cartera.xlsx"):
        (tmp_path / nombre).write_bytes(b"x")
    assert sorted(a.nombre for a in archivos.archivos("cartera-sin-asignar")) == ["cartera.xlsx", "resumen.png"]
    assert sorted(cola_ejecuciones._foto(tmp_path)) == ["cartera.xlsx", "resumen.png"]
