---
name: reportes-conexiones-bd
description: Las 3 bases de datos del proyecto (dw_raw, rcc, slc), cómo se configuran y cómo se consultan. Usar siempre que un reporte lea o escriba en SQL Server.
---

# Conexiones a BD

| Alias | Servidor | Base | Auth |
|---|---|---|---|
| `dw_raw` | 172.20.0.70 | DW_Raw_v2 (+ `dbriesgos`) | SQL |
| `rcc` | 172.20.0.70 | DBRCC | SQL |
| `slc` | 172.24.2.213 | slc (+ INTCOM, DWH, csd) | Windows |

Contrato completo: [conexiones-bd](../../docs/data/contracts/conexiones-bd.md).

```python
from reportes.db import leer_sql, cargar_sql
df = leer_sql("slc", cargar_sql("mensuales/saca_tu_garra/saca_tu_garra.sql"), {"fec": "2026-06-30"})
```

## Prohibido
- `pyodbc.connect` / `create_engine` fuera de `db.py` (regla `conexion-solo-en-db`).
- Servidores, usuarios o claves literales; todo sale de `.env`.
- Usar `dw_raw` (escritura) para reportes que solo leen.

Bases adicionales (`dbriesgos`, `INTCOM`, `DWH`…) se alcanzan con nombres de 3 partes desde su alias; no son conexiones nuevas. Una cuarta base requiere ADR y entrada en `config.BASES`.
