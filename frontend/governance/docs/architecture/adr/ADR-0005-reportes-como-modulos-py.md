# ADR-0005: Reportes como módulos `.py` con ejecutor común (sin carpeta `sql/`)

- Estado: Vigente · Fecha: 2026-10-06

## Contexto
El flujo heredado era: abrir un `.sql`, cambiar a mano las fechas, ejecutar en SSMS, copiar a Excel. Las fechas fijas, la falta de validación de tablas y el copy-paste producían cifras plausibles y equivocadas. Una carpeta `sql/` con archivos sueltos reproducía ese flujo (alguien tenía que ejecutarlos).

## Decisión
Cada reporte es un módulo Python ejecutable con su T-SQL incrustado y fechas por tokens (`@@F@@`…). Un ejecutor común (lo lanza una persona, [ADR-0007](./ADR-0007-ejecucion-manual-fecha-en-env.md)) (`comun/ejecutor.py`) automatiza conexión, validación de tablas al corte, ejecución, validación de datos y exportación a Excel. Se elimina `sql/`.

Si una tabla no está al día: el reporte **no se ejecuta**, se imprime qué tablas faltan y se guarda el mensaje para Producción (`data/outputs/solicitudes/`).

## Consecuencias
- Un solo comando por reporte: `python main.py <reporte> --fecha-corte AAAA-MM-DD`.
- La lógica heredada se conserva tal cual (con fechas parametrizadas): **no se ha ejecutado contra las bases reales** desde este entorno; la primera ejecución de cada reporte debe compararse con la salida manual del mes anterior ([evidencia](../../evidence/evidence-policy.md)).
- Los nombres de hoja son `Resultado_N` hasta fijarlos tras esa primera ejecución.
- La regla `fechas-fijas-en-sql` impide volver a incrustar fechas.
