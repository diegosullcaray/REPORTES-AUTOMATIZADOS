---
name: reportes-testing
description: Cómo probar los reportes con pytest sin tocar las bases reales. Usar al escribir o revisar tests.
---

# Testing

```bash
python -m pytest -q
python governance/scripts/verificar.py
```

- Un `tests/<capa>/test_<modulo>.py` por módulo (regla `prueba-vecina`); las carpetas de pruebas reflejan las capas del backend.
- Se prueba: reglas de fecha (lunes→sábado, fin de mes), `Periodo`/`Mes` inválidos, transformaciones puras (normalizar llaves, agrupar productos), cuatro casos (error / vacío / aborto / éxito).
- Las consultas se parchean: `monkeypatch.setattr("infraestructura.bd.leer_sql", falso)` (o un doble con `aplicacion.puertos.registrar`) devolviendo `DataFrame` sintéticos (sin datos reales de clientes).
- Variables de entorno de conexión con `monkeypatch.setenv` (ver `tests/infraestructura/test_configuracion.py`).
- La validación contra BD real es manual y queda en `docs/evidence/` con conteos, no con datos.
