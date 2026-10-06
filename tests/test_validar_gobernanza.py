import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "governance" / "scripts"))
import validar_gobernanza as vg  # noqa: E402


def test_el_repo_no_tiene_errores_de_gobernanza():
    errores = [h for fn, _ in vg.REGLAS.values() for h in fn() if h.nivel == "error"]
    assert errores == []


def test_regla_de_secretos_detecta_literales(tmp_path, monkeypatch):
    malo = tmp_path / "x.py"
    malo.write_text("conn = 'UID=sa;PWD=abc123;'\n", encoding="utf-8")
    monkeypatch.setattr(vg, "FUENTES", [malo])
    monkeypatch.setattr(vg, "SQLS", [])
    monkeypatch.setattr(vg, "RAIZ", tmp_path)
    assert [h.regla for h in vg.r_secretos()] == ["secretos-en-codigo"]
