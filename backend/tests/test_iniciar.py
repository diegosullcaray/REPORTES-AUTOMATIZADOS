"""iniciar.py: detecta que hay dependencias por instalar (un paquete nuevo en package.json o requirements.txt) antes de arrancar."""

import importlib.util
import json
import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("iniciar", RAIZ / "iniciar.py")
iniciar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(iniciar)


@pytest.fixture
def web(tmp_path, monkeypatch):
    monkeypatch.setattr(iniciar, "FRONTEND", tmp_path)
    (tmp_path / "package.json").write_text(json.dumps({"dependencies": {"echarts": "^6"}, "devDependencies": {"typescript": "^5"}}), encoding="utf-8")
    return tmp_path


def _instalar(web, *paquetes):
    for n in paquetes:
        (web / "node_modules" / n).mkdir(parents=True, exist_ok=True)
        (web / "node_modules" / n / "package.json").write_text("{}", encoding="utf-8")


def test_web_sin_node_modules(web):
    assert iniciar.motivo_para_instalar_web() == "no existe node_modules"


def test_web_con_un_paquete_nuevo_sin_instalar(web):
    _instalar(web, "typescript")           # falta echarts: antes de este cambio, con node_modules ya no se revisaba nada
    assert iniciar.motivo_para_instalar_web() == "falta echarts"


def test_web_al_dia(web):
    _instalar(web, "echarts", "typescript")
    assert iniciar.motivo_para_instalar_web() is None


def test_web_con_el_lock_mas_nuevo_que_lo_instalado(web):
    _instalar(web, "echarts", "typescript")
    oculto, lock = web / "node_modules" / ".package-lock.json", web / "package-lock.json"
    oculto.write_text("{}", encoding="utf-8")
    lock.write_text("{}", encoding="utf-8")
    os.utime(oculto, (1_000_000, 1_000_000))
    os.utime(lock, (2_000_000, 2_000_000))
    assert iniciar.motivo_para_instalar_web() == "package-lock.json cambió"


def _comprobar_backend(tmp_path, lineas):
    req = tmp_path / "requirements.txt"
    req.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return subprocess.run([sys.executable, "-c", iniciar._COMPROBAR_BACKEND, str(req)], capture_output=True, text=True)


def test_backend_al_dia(tmp_path):
    r = _comprobar_backend(tmp_path, ["# comentario", "", f"pytest=={metadata.version('pytest')}", "pandas>=1  # sin versión fija: no se compara"])
    assert (r.returncode, r.stdout.strip()) == (0, "")


def test_backend_dice_cuales_faltan_o_cambiaron_de_version(tmp_path):
    r = _comprobar_backend(tmp_path, ["pytest==0.0.1", "paquete-que-no-existe-xyz==1.2.3", f"pandas=={metadata.version('pandas')}"])
    assert r.returncode == 1 and r.stdout.strip() == "pytest==0.0.1, paquete-que-no-existe-xyz==1.2.3"
