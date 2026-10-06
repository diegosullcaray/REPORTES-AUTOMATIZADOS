# ADR-0007: Ejecución manual bajo demanda; la fecha de corte vive en el `.env`

- Estado: Vigente · Fecha: 2026-10-06

## Contexto
«Automatizar» se entendió al inicio como reportes que corren solos. El uso real es otro: una persona decide cuándo ejecutar cada reporte (cuando las tablas están listas) y necesita fijar la fecha de corte sin editar código ni repetirla en cada comando.

## Decisión
- No hay tareas programadas ni procesos residentes: cada reporte corre cuando alguien lo lanza (`python main.py <reporte>`).
- La fecha de corte se escribe en el `.env`: `FECHA_CORTE_MENSUAL` (reportes mensuales) y `FECHA_CORTE_DIARIA` (diarios), formato `AAAA-MM-DD`.
- Prioridad: `--fecha-corte` / `--mes` en el comando **>** `.env` **>** solo diarios: día anterior (lunes ⇒ sábado). Un reporte mensual sin ninguna fecha falla con un mensaje que indica el `.env`.
- Cada reporte imprime la fecha y su origen (`--fecha-corte`, `.env (…)` o por defecto) antes de consultar.
- Aplica a los 22 comandos (los 17 de lote y los 5 con CLI propia).

## Consecuencias
- Cambiar de mes = editar una línea del `.env`. Una fecha olvidada de un mes anterior es el riesgo principal: por eso se imprime siempre y, con `tablas --verificar`, se valida contra las tablas.
- El inicio de mes no depende de memoria ni de parámetros repetidos; el roadmap descarta programar ejecuciones.
