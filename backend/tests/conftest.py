import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture(autouse=True)
def _historial_de_validacion_aislado(tmp_path, monkeypatch):
    """Ninguna prueba escribe el historial de validaciones en data/outputs (los endpoints lo registran al verificar)."""
    from api import validacion

    monkeypatch.setattr(validacion, "DIR", tmp_path / "validaciones")
