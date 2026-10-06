# Catálogo de datos

Qué origen consume cada reporte. **El detalle tabla por tabla (con columna de fecha y reportes que la usan) está en el [inventario de tablas](./tables-inventory.md)**, generado desde `src/reportes/tablas.py`. La lista de reportes y SQL se **genera** en el [inventario](../architecture/module-inventory.md); aquí vive el significado.

| Reporte | Base (alias) | Tablas / orígenes principales | Corte |
|---|---|---|---|
| CMG Mora | `dw_raw` | `dbriesgos.dbo.RECAUDO_DIARIO_FINANZAS`, `dbriesgos.dbo.PROV_PROY_<YYYYMMDD>_0`, `dbriesgos.dbo.GASTO_PROV_OPE_DIARIA`, `DW_Raw_v2.dbo.CMGMora_Recaudo`, `CMGMora_STRJERCOR` → `[storage].[com_act].[SBTVRIE001]` | día anterior (lunes: sábado) |
| Bancarizados | `rcc` + `slc` | RCC (deuda sistema) cruzado con cartera `ccd` | fin de mes |
| Bancarizados por producto | `slc` | `csd.dbo.Clientes_DS`, SP de desembolsos en `dwh` | mes |
| Clientes extranjeros | `slc` (+ `rcc` con `--pasivos-directo`) | créditos, pasivos, seguros por nacionalidad | fin de mes |
| Indicadores de clientes | `slc` | `INTCOM.dbo.ccd`, `csd.dbo.Clientes_DS`, `DWH.dbo.HCARCAP001`, `INTCOM.dbo.CCS_FUND_F` | mes (seguros con desfase configurable) |
| Resto de reportes (17 comandos de lote) | `slc` | ver [inventario de tablas](./tables-inventory.md) | fin de mes (diarios: día anterior) |

> Los reportes de lote consultan sobre todo `DWH`, `INTCOM`, `DMA`, `storage` y `csd` desde `slc`. Verificar con el responsable antes de automatizar.
