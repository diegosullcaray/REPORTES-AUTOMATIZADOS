# ADR-0006: La conexión es un servidor; la base de datos la elige cada reporte

- Estado: Vigente · Fecha: 2026-10-06 · Ajusta: [ADR-0001](./ADR-0001-conexiones-centralizadas.md)

## Contexto
La primera versión modeló «3 bases de datos» (`dw_raw`, `rcc`, `slc`) con una base fija por conexión. Pero el `.env` real tiene **3 servidores** (`MISHWBDDES01`, `172.24.2.213`, `172.20.0.70`) y en cada uno viven varias bases (en `172.20.0.70`: `DBRCC`, `DW_Raw_v2`, `dbriesgos`, `DW_Metadata`; en `172.24.2.213`: `slc`, `storage`, `dwh`, `intcom`, `csd`, `dma`, `appj`). Cada reporte usa las suyas, así que una base fija por conexión es una restricción artificial.

## Decisión
- El `.env` declara solo servidor y credenciales por conexión: `MISH_*`, `SLC_*`, `RCC_*`.
- La base de datos la declara **cada reporte**: `ReporteLote(servidor=…, base=…)`, o `base=` en `leer_sql`/`conexion_pyodbc`/`ejecutar_lote`, o el propio `USE`/nombres de 3 partes del T-SQL.
- `<PREFIJO>_DATABASE` en el `.env` queda como catálogo por defecto **opcional**; la base del reporte siempre manda.
- El alias `dw_raw` desaparece: era `rcc` (mismo servidor `172.20.0.70`) con base `DW_Raw_v2`.

## Consecuencias
- Un reporte que cambia de base no toca el `.env`; agregar una base nueva no requiere configuración.
- El servidor `mish` queda configurado pero sin reportes asignados.
- El servidor `rcc` se usa con `master` para lectura y escritura: sigue abierto [SEC-002](../../security/findings.md) (usuario dedicado de mínimo privilegio).
