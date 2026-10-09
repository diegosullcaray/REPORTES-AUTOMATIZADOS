# Convenciones

- Archivos y carpetas: `snake_case`, sin espacios ni tildes (regla `nombres-canonicos`).
- **Reportes: un módulo por reporte con el número del legado**: `src/reportes/mensuales/<piero|erick>/r<NN>[_<n>]_<nombre>.py` y `src/reportes/diarios/r<NN>…` (`r04_1_cmg_mora.py`). Salida: `data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>/`. El responsable y el número salen de la carpeta del legado.
- **No hay carpeta `sql/`**: el T-SQL va incrustado en el módulo del reporte (`SQL = r"""…"""` dentro de un `ReporteLote`). Las fechas siempre por tokens (`@@F@@`, `@@F_ISO@@`, `@@F_ANT@@`…); nunca fechas literales ni f-strings con datos de usuario (los nombres de tabla dinámicos, como `PROV_PROY_<fecha>_0`, se generan desde un `date`).
- Código: `from __future__ import annotations`, tipado, `logging` en lugar de `print` en reportes nuevos.
- Cada reporte: `main(argv) -> int` + `argparse` con `--fecha-corte`/`--mes`, `--salida`, `-v`.
- Acceso a datos solo vía `reportes.db`; salidas solo bajo `config.DIR_OUTPUTS`.
- Commits en español, imperativo, con alcance claro.
