"""Consola (interfaces/cli/principal.py): comandos de `main.py` y códigos de salida."""

from dominio.reportes import REPORTES
from infraestructura import bd
from interfaces.cli.principal import main


def test_listar_muestra_todos_los_reportes(capsys):
    assert main(["listar"]) == 0
    salida = capsys.readouterr().out
    assert all(nombre in salida for nombre in REPORTES)


def test_reporte_desconocido_sale_con_codigo_2(capsys):
    assert main(["no-existe"]) == 2
    assert "Reporte desconocido" in capsys.readouterr().err


def test_probar_conexiones_sale_con_error_si_alguna_falla(monkeypatch, capsys):
    monkeypatch.setattr(bd, "probar_conexiones", lambda: {"mish": "OK", "slc": "ERROR: sin red", "rcc": "OK"})
    assert main(["probar-conexiones"]) == 1
    assert "ERROR: sin red" in capsys.readouterr().out
    monkeypatch.setattr(bd, "probar_conexiones", lambda: {"mish": "OK"})
    assert main(["probar-conexiones"]) == 0
