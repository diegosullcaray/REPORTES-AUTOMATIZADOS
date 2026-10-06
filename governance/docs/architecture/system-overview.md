# Visión del sistema

```text
main.py                         CLI único (listar | probar-conexiones | <reporte>)
src/reportes/
  config.py                     rutas + las 3 BD (lee .env)
  db.py                         ÚNICO acceso a BD
  registro.py                   catálogo de reportes
  comun/                        utilidades compartidas (fechas, excel) — por poblar
  diarios/<reporte>.py          reportes diarios
  mensuales/<reporte>.py        reportes mensuales
sql/<frecuencia>/<reporte>/     SQL versionado
plantillas/                     formatos Excel base
salidas/                        resultados (no versionado)
tests/                          pytest
governance/                     este marco
docs/LEGADO/                    archivo histórico, solo lectura
```

## Reglas de capas
1. `reportes.<frecuencia>.*` pueden importar `config`, `db`, `comun`; **nunca** entre sí.
2. Solo `db.py` conoce pyodbc/SQLAlchemy.
3. Solo `config.py` lee variables de entorno.
4. El SQL vive en `sql/`; el módulo lo carga (`cargar_sql`) y le pasa parámetros enlazados.
5. Cada módulo expone `main(argv) -> int` y se registra en `registro.py`.

## Estado de la migración
Los 5 módulos migrados aún contienen SQL embebido y utilidades repetidas (`Periodo`, `cronometro`, `exportar_excel`). Ver [roadmap](../business/roadmap.md).
