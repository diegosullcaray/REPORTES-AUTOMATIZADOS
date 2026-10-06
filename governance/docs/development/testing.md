# Pruebas

- `pytest` en `tests/`; `tests/conftest.py` añade `src/` al path.
- **Nunca** se prueba contra las bases reales: se prueban reglas de fecha, transformaciones puras y configuración. Las consultas se validan manualmente en un entorno con acceso y se deja evidencia en [evidence](../evidence/README.md).
- Convención: un `tests/test_<modulo>.py` por módulo (regla `prueba-vecina`).
- Para código que llama a `db`, parchear `reportes.db.leer_sql` con `monkeypatch`.

```bash
python -m pytest -q
```
