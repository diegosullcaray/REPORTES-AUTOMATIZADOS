# Convenciones

- Archivos y carpetas: `snake_case`, sin espacios ni tildes (regla `nombres-canonicos`).
- **Reportes: un módulo por reporte con el número del legado**: `src/reportes/mensuales/<piero|erick>/r<NN>[_<n>]_<nombre>.py` y `src/reportes/diarios/r<NN>…` (`r04_1_cmg_mora.py`). Salida: `data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>/`. El responsable y el número salen de la carpeta del legado.
- **No hay carpeta `sql/`**: el T-SQL va incrustado en el módulo del reporte (`SQL = r"""…"""` dentro de un `ReporteLote`). Las fechas siempre por tokens (`@@F@@`, `@@F_ISO@@`, `@@F_ANT@@`…); nunca fechas literales ni f-strings con datos de usuario (los nombres de tabla dinámicos, como `PROV_PROY_<fecha>_0`, se generan desde un `date`).
- Código: `from __future__ import annotations`, tipado, `logging` en lugar de `print` en reportes nuevos.
- Cada reporte: `main(argv) -> int` + `argparse` con `--fecha-corte`/`--mes`, `--salida`, `-v`.
- Acceso a datos solo vía el puerto `bd` (`infraestructura/bd.py`); salidas solo bajo `DIR_OUTPUTS` (`infraestructura/configuracion.py`).
- **Capas** ([ADR-0014](../architecture/adr/ADR-0014-clean-architecture-backend.md)): `dominio ← aplicacion ← infraestructura / interfaces`. Las reglas de negocio van en `dominio`; lo que orquesta, en un caso de uso de `aplicacion/casos_uso`; lo que toca el mundo exterior (BD, archivos, red), en `infraestructura` detrás de un puerto; las rutas HTTP y la consola solo traducen. La compuerta `arquitectura-capas` lo exige.
- Commits en español, imperativo, con alcance claro.
