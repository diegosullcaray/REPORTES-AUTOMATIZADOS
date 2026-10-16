# Pruebas

- `pytest` en `tests/`, organizado **por capa** (`tests/dominio`, `aplicacion`, `infraestructura`, `interfaces`, `reportes`); `tests/conftest.py` añade `src/` al path y conecta los adaptadores (`import composicion`).
- **Nunca** se prueba contra las bases reales: se prueban reglas de fecha, transformaciones puras y configuración. Las consultas se validan manualmente en un entorno con acceso y se deja evidencia en [evidence](../evidence/README.md).
- Convención: un `tests/<capa>/test_<modulo>.py` por módulo (regla `prueba-vecina`); las apps de Django (vistas y rutas) se prueban por HTTP en `tests/interfaces/web/test_api.py` con `tests/cliente_web.py`. Cada carpeta de pruebas es un paquete (`__init__.py`).
- Para código que llama a la base de datos, parchear el adaptador del puerto (`monkeypatch.setattr(infraestructura.bd, "leer_sql", falso)`) o registrar un doble con `aplicacion.puertos.registrar(...)`. El historial de validación de las pruebas va a una carpeta temporal (`conftest.py`).

```bash
python -m pytest -q
```
