# Guía: crear un reporte nuevo

1. Llena la [ficha de reporte](../templates/report-spec-template.md) (solicitante, base, fecha de corte, reglas, salida).
2. Localiza el SQL en `sql/…` (o muévelo desde el módulo) y parametriza la fecha.
3. Crea `src/reportes/<frecuencia>/<reporte>.py` con `main(argv) -> int`; carga SQL con `cargar_sql` y consulta con `leer_sql("<alias>", …)`.
4. Implementa los cuatro casos: **error** (excepción SQL), **vacío** válido, **abortar** por variable crítica, **éxito**.
5. Registra en `registro.py`.
6. Añade `tests/test_<reporte>.py` (reglas de fecha y transformaciones, sin BD).
7. `python governance/scripts/generar_inventario.py` y `python governance/scripts/verificar.py`.
8. Si la ficha cambió el catálogo, actualiza [catalog](../data/catalog.md) y [domain-catalog](../business/domain-catalog.md).
