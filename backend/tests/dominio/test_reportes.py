from importlib.util import find_spec

from infraestructura.configuracion import SERVIDORES
from dominio.reportes import REPORTES


def test_modulos_existen_y_bases_son_validas():
    for r in REPORTES.values():
        assert find_spec(r.modulo) is not None, r.modulo
        assert set(r.servidores) <= set(SERVIDORES)
