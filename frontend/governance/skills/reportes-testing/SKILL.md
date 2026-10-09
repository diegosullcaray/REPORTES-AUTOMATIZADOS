---
name: reportes-testing
description: Cómo probar los reportes con pytest sin tocar las bases reales. Usar al escribir o revisar tests.
---

# Testing

```bash
python -m pytest -q
python governance/scripts/verificar.py
```

- Un `tests/test_<modulo>.py` por módulo (regla `prueba-vecina`).
- Se prueba: reglas de fecha (lunes→sábado, fin de mes), `Periodo`/`Mes` inválidos, transformaciones puras (normalizar llaves, agrupar productos), cuatro casos (error / vacío / aborto / éxito).
- Las consultas se parchean: `monkeypatch.setattr("reportes.db.leer_sql", falso)` devolviendo `DataFrame` sintéticos (sin datos reales de clientes).
- Variables de entorno de conexión con `monkeypatch.setenv` (ver `tests/test_config.py`).
- La validación contra BD real es manual y queda en `docs/evidence/` con conteos, no con datos.
