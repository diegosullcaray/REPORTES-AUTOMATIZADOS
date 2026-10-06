# Guía: crear un reporte nuevo

1. Llena la [ficha de reporte](../templates/report-spec-template.md) (solicitante, base, fecha de corte, reglas, salida).
2. Toma el T-SQL del legado y reemplaza cada fecha fija por un token (`@@F@@`, `@@F_ISO@@`, `@@F_ANT@@`…).
3. Crea `src/reportes/<diarios|mensuales>/<reporte>.py` con un `ReporteLote` y `main(argv)` → `correr(REPORTE, argv)` ([skill](../../skills/reportes-ejecutor/SKILL.md)). El ejecutor ya conecta, valida tablas al corte, valida datos y exporta a Excel.
3b. **Registra el reporte** en `registro.py` y **sus tablas** que consulta en `src/reportes/tablas.py` (`TABLAS` con alias, tipo y columna de fecha; `USO[<reporte>]`). La regla `tabla-sin-registrar` lo exige y el cierre de mes depende de ello.
4. Declara los casos: `vacio_valido` si un resultado vacío es legítimo, `hojas` con `columna_fecha` para validar fechas, `escribe_en_bd` si crea/borra tablas.
5. Registra en `registro.py`.
6. Añade `tests/test_<reporte>.py` (reglas de fecha y transformaciones, sin BD).
7. `python governance/scripts/generar_inventario.py` y `python governance/scripts/verificar.py`.
8. Escribe su runbook en `docs/development/runbooks/<reporte>.md` (tablas críticas, comando, validaciones, abortos).
9. Si la ficha cambió el catálogo, actualiza [catalog](../data/catalog.md) y [domain-catalog](../business/domain-catalog.md).
