from reportes import cli_tablas


def test_listar_y_tablas_sin_conectar(capsys):
    assert cli_tablas.cmd_tablas([]) == 0
    assert cli_tablas.cmd_tablas(["saca-tu-garra"]) == 0
    assert "storage.com_act.hcda001" in capsys.readouterr().out


def test_reporte_desconocido_devuelve_2():
    assert cli_tablas.cmd_tablas(["no_existe"]) == 2


def test_solicitud_sin_verificar_lista_tablas_con_fecha(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli_tablas, "DIR_OUTPUTS", tmp_path)
    assert cli_tablas.cmd_solicitud(["saldo-medio-vigente", "--fecha-corte", "2026-10-31"]) == 0
    assert "31/10/2026" in capsys.readouterr().out
    assert (tmp_path / "solicitudes" / "solicitud_saldo-medio-vigente_20261031.txt").exists()
