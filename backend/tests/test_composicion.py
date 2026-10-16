"""Raíz de composición (composicion.py): conecta los adaptadores reales a todos los puertos."""

import composicion
from aplicacion import puertos as modulo


def test_construye_un_adaptador_por_cada_puerto():
    p = composicion.construir()
    assert set(vars(p)) == set(modulo.Puertos.__dataclass_fields__)
    assert p.bd.__name__ == "infraestructura.bd" and p.google.__name__ == "infraestructura.google.cliente"
    assert callable(p.bd.leer_sql) and callable(p.entorno.leer) and callable(p.cola.encolar) and callable(p.excel.guardar_libro)


def test_las_pruebas_arrancan_con_los_puertos_reales_disponibles():
    assert modulo.fabrica is composicion.construir
    assert modulo.puertos().entorno.raiz().name == "backend"
