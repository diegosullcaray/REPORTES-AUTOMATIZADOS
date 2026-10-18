import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # backend/: el proyecto Django (config/)

from config import composicion  # noqa: F401 - conecta los adaptadores reales a los puertos

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()


@pytest.fixture(autouse=True)
def _historial_de_validacion_aislado(tmp_path, monkeypatch):
    """Ninguna prueba escribe el historial de validaciones en data/outputs (los endpoints lo registran al verificar)."""
    from modulos.reportes.infraestructura import historial_validacion

    monkeypatch.setattr(historial_validacion, "DIR", tmp_path / "validaciones")


@pytest.fixture(autouse=True)
def _etiquetas_aisladas(tmp_path, monkeypatch):
    """Ninguna prueba escribe las etiquetas de los grupos en data/outputs."""
    from modulos.reportes.infraestructura import etiquetas

    monkeypatch.setattr(etiquetas, "RUTA", tmp_path / "etiquetas.json")
