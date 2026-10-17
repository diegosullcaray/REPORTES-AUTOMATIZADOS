# Guía: crear un reporte nuevo

1. Llena la [ficha de reporte](../templates/report-spec-template.md) (solicitante, base, fecha de corte, reglas, salida).
2. Toma el T-SQL del legado y reemplaza cada fecha fija por un token (`@@F@@`, `@@F_ISO@@`, `@@F_ANT@@`…).
3. Crea `src/modulos/reportes/catalogo/<diarios|mensuales/piero|mensuales/erick>/r<NN>_<nombre>.py` (número de su carpeta del legado) con un `ReporteLote` y `main(argv)` → `correr(REPORTE, argv)` ([skill](../../skills/reportes-ejecutor/SKILL.md)). El ejecutor ya conecta, valida tablas al corte, valida datos y exporta a Excel.
3b. **Registra el reporte** en `src/modulos/reportes/dominio/reportes.py` y **sus tablas** que consulta en `src/modulos/reportes/dominio/tablas.py` (`TABLAS` con servidor, tipo y columna de fecha; `USO[<reporte>]`). La regla `tabla-sin-registrar` lo exige y el cierre de mes depende de ello.
4. Declara los casos: `vacio_valido` si un resultado vacío es legítimo, `hojas` con `columna_fecha` para validar fechas, `escribe_en_bd` si crea/borra tablas.
5. Verifica que quedó en `modulos/reportes/dominio/reportes.py` (comando, grupo, número del legado, servidores, carpeta de salida).
6. Añade `tests/modulos/reportes/catalogo/test_<reporte>.py` (reglas de fecha y transformaciones, sin BD). El módulo importa `aplicacion.ejecucion` (`ReporteLote`, `correr`) y, si consulta, `infraestructura.bd`; nunca `interfaces`.
7. `python governance/scripts/generar_inventario.py` y `python governance/scripts/verificar.py`.
8. Escribe su runbook en `docs/development/runbooks/<reporte>.md` (tablas críticas, comando, validaciones, abortos).
9. Si la ficha cambió el catálogo, actualiza [catalog](../data/catalog.md) y [domain-catalog](../business/domain-catalog.md).
