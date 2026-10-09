# Visión del sistema

```text
main.py                         CLI único (listar | probar-conexiones | <reporte>)
src/reportes/
  config.py                     rutas + las 3 BD (lee .env)
  db.py                         ÚNICO acceso a BD
  registro.py                   catálogo de reportes
  tablas.py                     registro de TABLAS por reporte (servidor, tipo, columna de fecha)
  verificacion.py               ¿tablas al día? + mensaje de solicitud a Producción
  cli_tablas.py                 subcomandos `tablas` y `solicitud-actualizacion`
  comun/ejecutor.py             flujo común de todo reporte de lote
  comun/fechas.py               cortes y tokens @@F@@…
  diarios/r<NN>_<nombre>.py     reportes diarios (número de «01 TAREAS DIARIAS»)
  mensuales/piero/r<NN>_…       reportes heredados de Piero (01…09)
  mensuales/erick/r<NN>_…       reportes heredados de Erick (01…03)
  comun/excel.py imagen.py correo.py entrega_correo.py   formato Excel, imagen del resumen y correo (cuenta MIS)
data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>/   salidas con el orden del legado
data/inputs/                    archivos que entran (Excel/CSV, formatos base) — no versionado
data/outputs/                   resultados que generan los reportes — no versionado
tests/                          pytest
governance/                     este marco
docs/LEGADO/                    archivo histórico, solo lectura
```

## Reglas de capas
1. `reportes.<frecuencia>.*` pueden importar `config`, `db`, `comun`; **nunca** entre sí.
2. Solo `db.py` conoce pyodbc/SQLAlchemy.
3. Solo `config.py` lee variables de entorno.
4. El T-SQL va incrustado en el módulo (`ReporteLote.sql`) con tokens de fecha; el ejecutor los resuelve desde `--fecha-corte`.
5. Cada módulo expone `main(argv) -> int` y se registra en `registro.py`.

## Estado de la migración
16 reportes usan el ejecutor común (`ReporteLote`). Los 5 primeros migrados (CMG Mora, Bancarizados ×2, Extranjeros, Indicadores) tienen lógica Python propia y utilidades repetidas (`Periodo`, `cronometro`, `exportar_excel`): candidatos a converger al ejecutor. Ver [roadmap](../business/roadmap.md).
