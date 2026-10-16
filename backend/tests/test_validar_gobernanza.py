import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "governance" / "scripts"))
import validar_gobernanza as vg  # noqa: E402


def test_el_repo_no_tiene_errores_de_gobernanza():
    errores = [h for fn, _ in vg.REGLAS.values() for h in fn() if h.nivel == "error"]
    assert errores == []


def test_regla_de_secretos_detecta_literales(tmp_path, monkeypatch):
    malo = tmp_path / "x.py"
    malo.write_text("conn = 'UID=sa;PWD=abc123;'\n", encoding="utf-8")
    monkeypatch.setattr(vg, "FUENTES", [malo])
    monkeypatch.setattr(vg, "BACK", tmp_path)
    assert [h.regla for h in vg.r_secretos()] == ["secretos-en-codigo"]



def _fuente(tmp_path, monkeypatch, relativa, texto):
    archivo = tmp_path / "src" / relativa
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(texto, encoding="utf-8")
    monkeypatch.setattr(vg, "FUENTES", [archivo])
    monkeypatch.setattr(vg, "BACK", tmp_path)


def test_el_dominio_no_puede_importar_la_infraestructura(tmp_path, monkeypatch):
    _fuente(tmp_path, monkeypatch, "dominio/x.py", "from infraestructura import bd\n")
    (h,) = list(vg.r_capas())
    assert h.regla == "arquitectura-capas" and "«dominio» no puede importar «infraestructura»" in h.detalle


def test_la_aplicacion_no_puede_importar_io_ni_frameworks(tmp_path, monkeypatch):
    _fuente(tmp_path, monkeypatch, "aplicacion/x.py", "import smtplib\nfrom urllib.parse import urlparse\nimport pandas\nimport urllib.request\n")
    assert sorted(h.detalle.split("«")[2].split("»")[0] for h in vg.r_capas()) == ["smtplib", "urllib.request"]   # urllib.parse y pandas sí se admiten


def test_una_interfaz_solo_llega_a_la_infraestructura_por_composicion(tmp_path, monkeypatch):
    _fuente(tmp_path, monkeypatch, "interfaces/x.py", "import composicion\nfrom aplicacion import dto\nfrom infraestructura import bd\n")
    assert [("infraestructura" in h.detalle) for h in vg.r_capas()] == [True]


def test_los_reportes_y_la_composicion_pueden_usar_la_infraestructura(tmp_path, monkeypatch):
    _fuente(tmp_path, monkeypatch, "reportes/x.py", "from infraestructura.bd import leer_sql\nfrom aplicacion.ejecucion import correr\n")
    assert list(vg.r_capas()) == []
    _fuente(tmp_path, monkeypatch, "composicion.py", "from infraestructura import bd\nfrom interfaces.http import app\n")
    assert list(vg.r_capas()) == []
