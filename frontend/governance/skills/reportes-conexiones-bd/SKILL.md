---
name: reportes-conexiones-bd
description: Los 3 servidores del proyecto (mish, slc, rcc), cómo se configuran en el .env y cómo cada reporte elige su base de datos. Usar siempre que un reporte lea o escriba en SQL Server.
---

# Conexiones: 3 servidores; la base la elige el reporte

| Conexión | Servidor | Auth | Bases que usan los reportes |
|---|---|---|---|
| `mish` | MISHWBDDES01 | Windows | `storage` (+ `appj`) |
| `slc` | 172.24.2.213 | Windows | `dwh`, `dma`, `csd`, `intcom`, `slc` |
| `rcc` | 172.20.0.70 | SQL (master) | `dbriesgos`, `DBRCC`, `DW_Raw_v2`, `DW_Metadata`, `DB<AAAAMM>` |

El `.env` solo trae servidor y credenciales por conexión; **no** una base. Contrato: [conexiones-bd](../../docs/data/contracts/conexiones-bd.md).

```python
from reportes.db import leer_sql, ejecutar_lote
df = leer_sql("rcc", "select top 5 * from DBRCC.dbo.RCCCAB20260630", base="DBRCC")
resultados = ejecutar_lote("mish", sql_tsql, base="storage")   # lote completo (#temp, USE, GO): lista de DataFrames
```

En un `ReporteLote`: `servidor="mish", base="storage"`. Si el T-SQL cambia de base con `USE`, o usa nombres de 3 partes, `base` es solo el punto de partida.

**Una consulta solo ve las bases de su servidor** (`storage` ⇒ `mish`, `dwh`/`dma`/`csd`/`intcom` ⇒ `slc`, `dbriesgos`/`DBRCC`/`DW_Raw_v2` ⇒ `rcc`). Mapa: [servidores y bases](../../docs/data/servidores-y-bases.md) y `config.BASES_DE`; la regla `servidor-coherente` lo verifica.

## Prohibido
- `pyodbc.connect` / `create_engine` fuera de `db.py` (regla `conexion-solo-en-db`).
- Servidores, usuarios o claves literales; todo sale de `.env`.
- Fijar una base en el `.env` para "todos los reportes": cada reporte declara la suya.
- Usar para reportes de solo lectura una cuenta con permisos de escritura cuando exista una de lectura.
