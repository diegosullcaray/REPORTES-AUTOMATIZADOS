import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import composicion  # noqa: E402,F401 - conecta los adaptadores reales a los puertos


@pytest.fixture(autouse=True)
def _historial_de_validacion_aislado(tmp_path, monkeypatch):
    """Ninguna prueba escribe el historial de validaciones en data/outputs (los endpoints lo registran al verificar)."""
    from infraestructura import historial_validacion

    monkeypatch.setattr(historial_validacion, "DIR", tmp_path / "validaciones")
