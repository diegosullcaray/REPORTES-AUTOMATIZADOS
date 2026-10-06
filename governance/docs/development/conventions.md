# Convenciones

- Archivos y carpetas: `snake_case`, sin espacios ni tildes (regla `nombres-canonicos`).
- SQL: `sql/<diarias|mensuales>/<reporte>/<nombre>.sql`; parámetros enlazados (`:fec` / `?`), nunca f-strings con datos de usuario (los nombres de tabla dinámicos, como `PROV_PROY_<fecha>_0`, se validan antes).
- Código: `from __future__ import annotations`, tipado, `logging` en lugar de `print` en reportes nuevos.
- Cada reporte: `main(argv) -> int` + `argparse` con `--fecha-corte`/`--mes`, `--salida`, `-v`.
- Acceso a datos solo vía `reportes.db`; salidas solo bajo `config.DIR_SALIDAS`.
- Commits en español, imperativo, con alcance claro.
