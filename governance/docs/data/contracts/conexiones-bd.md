# Contrato: conexiones a bases de datos

Las **3 conexiones** del proyecto se definen en `src/reportes/config.py` y se configuran por `.env`. El único código autorizado a abrirlas es `src/reportes/db.py` (regla `conexion-solo-en-db`).

| Alias | Servidor | Base | Autenticación | Alcance adicional (3 partes) | Permisos requeridos |
|---|---|---|---|---|---|
| `dw_raw` | 172.20.0.70 | `DW_Raw_v2` | SQL: `DW_RAW_USER` / `DW_RAW_PASSWORD` | `dbriesgos` | **lectura + escritura** (TRUNCATE/INSERT/UPDATE en `CMGMora_Recaudo`) |
| `rcc` | 172.20.0.70 | `DBRCC` | SQL: `RCC_USER` / `RCC_PASSWORD` | — | solo lectura |
| `slc` | 172.24.2.213 | `slc` | Windows (o `SLC_USER`/`SLC_PASSWORD`) | `INTCOM`, `DWH`, `csd`, `DMA`, `storage`; linked server `rcc_cd` | solo lectura |

## Uso desde código

```python
from reportes.db import leer_sql, ejecutar_lote, leer_ultimo_resultado, conexion_pyodbc

df = leer_sql("slc", "select top 5 * from csd.dbo.Clientes_DS where HFECPRO = :f", {"f": "2026-06-30"})
resultados = ejecutar_lote("slc", sql_tsql)   # script completo con #temp/USE/GO -> lista de DataFrames
```

- `leer_sql(alias, sql, params)`: SELECT parametrizado → DataFrame.
- `ejecutar_lote(alias, tsql)`: script T-SQL completo (GO, `USE`, `#temp`, `EXEC`) en una sesión → todos los resultados.
- `leer_ultimo_resultado(alias, sql, params)`: lotes con tabla temporal / SP en una sola sesión.
- `conexion_pyodbc(alias)`: escrituras y control transaccional (CMG Mora).

## Reglas

1. Un alias desconocido lanza `ConfiguracionError`; no hay valores por defecto de credenciales.
2. Usuario sin contraseña (o al revés) es error de configuración.
3. Verificación: `python main.py probar-conexiones`.
4. Supuesto pendiente de validar con el responsable: que estos tres alias sean las tres bases previstas.
