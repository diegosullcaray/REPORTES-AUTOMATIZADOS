"""Carpeta de salida de cada reporte (aplicacion/rutas.py): la raíz la da el puerto de entorno."""

from modulos.reportes.aplicacion.rutas import carpeta_salida
from core import configuracion


def test_carpeta_de_salida_cuelga_de_la_raiz_de_salidas(monkeypatch, tmp_path):
    monkeypatch.setattr(configuracion, "DIR_OUTPUTS", tmp_path)
    assert carpeta_salida("cmg-mora") == tmp_path / "diarias" / "04_cmg_mora"
    assert carpeta_salida("desembolsos-por-canal") == tmp_path / "mensuales" / "piero" / "01_desembolsos_por_canal"
