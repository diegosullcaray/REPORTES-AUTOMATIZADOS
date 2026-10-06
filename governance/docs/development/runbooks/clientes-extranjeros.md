# Runbook: `clientes-extranjeros` (mensual)

**Conexiones**: `slc` (créditos, seguros y, por defecto, pasivos vía linked server `rcc_cd`); `rcc` solo con `--pasivos-directo`. **Salida**: `salidas/clientes_extranjeros/ClientesExtranjeros_<AAAAMMDD>.xlsx` (`consolidado`, `creditos`, `pasivos`, `seguros`).

## Antes
```bash
python main.py tablas clientes-extranjeros --fecha-corte 2026-07-31 --verificar
```
Críticas: `intcom.dbo.ccd` (Fecha_Cierre), `intcom.dbo.ccs_fund_f` (fecha_reporte) y `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}` (debe existir).

## Ejecutar
```bash
python main.py clientes-extranjeros --fecha-corte 2026-07-31
python main.py clientes-extranjeros --fecha-corte 2026-07-31 --fecha-seguros 2026-06-30   # seguros con otro corte
python main.py clientes-extranjeros --fecha-corte 2026-07-31 --pasivos-directo            # si el linked server falla
```
## Validar
Si un bloque devuelve vacío el script sugiere la última fecha disponible: eso indica tabla desactualizada ⇒ [solicitud](./solicitud-actualizacion-tablas.md).
