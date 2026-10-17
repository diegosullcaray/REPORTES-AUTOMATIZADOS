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


def _detalles(tmp_path, monkeypatch, relativa, texto, base="src"):
    archivo = tmp_path / base / relativa if base else tmp_path / relativa
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(texto, encoding="utf-8")
    monkeypatch.setattr(vg, "FUENTES", [archivo])
    monkeypatch.setattr(vg, "BACK", tmp_path)
    return [h.detalle for h in vg.r_capas()]


def test_el_dominio_no_puede_importar_la_infraestructura_de_su_modulo(tmp_path, monkeypatch):
    (d,) = _detalles(tmp_path, monkeypatch, "modulos/reportes/dominio/x.py", "from modulos.reportes.infraestructura import excel\n")
    assert "«dominio» no puede importar «infraestructura»" in d


def test_dominio_y_aplicacion_no_pueden_importar_io_ni_frameworks(tmp_path, monkeypatch):
    detalles = _detalles(tmp_path, monkeypatch, "modulos/reportes/aplicacion/x.py", "import smtplib\nfrom urllib.parse import urlparse\nimport pandas\nimport urllib.request\nimport django\n")
    assert sorted(d.split("«")[2].split("»")[0] for d in detalles) == ["django", "smtplib", "urllib.request"]   # urllib.parse y pandas sí se admiten en la aplicación
    assert len(_detalles(tmp_path, monkeypatch, "modulos/reportes/dominio/x.py", "import pandas\n")) == 1


def test_los_adaptadores_del_nucleo_solo_los_usan_la_infraestructura_el_catalogo_y_config(tmp_path, monkeypatch):
    assert any("adaptador" in d for d in _detalles(tmp_path, monkeypatch, "modulos/reportes/aplicacion/x.py", "from core import bd\n"))
    assert any("adaptador" in d for d in _detalles(tmp_path, monkeypatch, "modulos/reportes/interfaces/web/x.py", "from core.entorno import leer\n"))
    for relativa in ("modulos/reportes/infraestructura/x.py", "modulos/reportes/catalogo/diarios/x.py"):
        assert _detalles(tmp_path, monkeypatch, relativa, "from core import bd\nfrom core.configuracion import DIR_OUTPUTS\n") == []
    assert _detalles(tmp_path, monkeypatch, "config/composicion.py", "from core import bd\nfrom modulos.reportes.infraestructura import excel\n", base="") == []
    assert _detalles(tmp_path, monkeypatch, "modulos/reportes/aplicacion/x.py", "from core.puertos import nucleo\nfrom core.excepciones import NoEncontrado\n") == []


def test_un_modulo_solo_usa_la_api_publica_de_los_modulos_de_los_que_depende(tmp_path, monkeypatch):
    ok = "from modulos.notificaciones.aplicacion import correo\nfrom modulos.integraciones.dominio import algo\n"
    assert _detalles(tmp_path, monkeypatch, "modulos/reportes/aplicacion/x.py", ok) == []
    (d,) = _detalles(tmp_path, monkeypatch, "modulos/reportes/aplicacion/x.py", "from modulos.notificaciones.aplicacion.puertos import puertos\n")
    assert "privados" in d
    (d,) = _detalles(tmp_path, monkeypatch, "modulos/reportes/aplicacion/x.py", "from modulos.notificaciones.infraestructura import correo_smtp\n")
    assert "solo usa el dominio y la aplicación" in d


def test_las_dependencias_entre_modulos_no_forman_ciclos(tmp_path, monkeypatch):
    (d,) = _detalles(tmp_path, monkeypatch, "modulos/notificaciones/aplicacion/x.py", "from modulos.reportes.aplicacion import dto\n")
    assert "no puede depender de «reportes»" in d
    assert _detalles(tmp_path, monkeypatch, "modulos/sistema/aplicacion/x.py", "from modulos.reportes.aplicacion import dto\n") == []
    (d,) = _detalles(tmp_path, monkeypatch, "core/x.py", "from modulos.reportes.dominio import fechas\n")
    assert "el núcleo no puede depender" in d


def test_solo_las_entradas_de_un_modulo_importan_config(tmp_path, monkeypatch):
    assert _detalles(tmp_path, monkeypatch, "modulos/reportes/interfaces/cli/x.py", "from config import composicion\n") == []
    (d,) = _detalles(tmp_path, monkeypatch, "modulos/reportes/aplicacion/x.py", "from config import composicion\n")
    assert "solo las entradas" in d


def test_un_archivo_fuera_de_la_estructura_es_un_error(tmp_path, monkeypatch):
    (d,) = _detalles(tmp_path, monkeypatch, "suelto.py", "x = 1\n")
    assert "fuera de la estructura" in d
