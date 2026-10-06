from importlib.util import find_spec

from reportes.config import BASES
from reportes.registro import REPORTES


def test_modulos_existen_y_bases_son_validas():
    for r in REPORTES.values():
        assert find_spec(r.modulo) is not None, r.modulo
        assert set(r.bases) <= set(BASES)
