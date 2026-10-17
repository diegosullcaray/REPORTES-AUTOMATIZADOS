"""Casos de uso de configuración: bases de datos y pruebas de conexión (sin tocar los servidores reales)."""

from modulos.sistema.aplicacion.casos_uso import configuracion
from core import bd


def test_prueba_de_servidor_informa_el_error(monkeypatch):
    def falla(*_):
        raise RuntimeError("sin red")

    monkeypatch.setattr(bd, "leer_sql", falla)
    p = configuracion.probar_servidor("mish")
    assert (p.ok, p.detalle) == (False, "RuntimeError: sin red")
