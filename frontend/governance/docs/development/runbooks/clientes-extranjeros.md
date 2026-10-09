# Runbook: `clientes-extranjeros` (mensual)

**Conexiones**: `slc` (créditos, seguros y, por defecto, pasivos vía linked server `rcc_cd`); `rcc` solo con `--pasivos-directo`. **Salida**: `data/outputs/clientes_extranjeros/ClientesExtranjeros_<AAAAMMDD>.xlsx` (`consolidado`, `creditos`, `pasivos`, `seguros`).

## Antes
```bash
python main.py tablas clientes-extranjeros --verificar
```
Críticas: `intcom.dbo.ccd` (Fecha_Cierre), `intcom.dbo.ccs_fund_f` (fecha_reporte) y la tabla de pasivos del cierre: `rcc_cd.db<AAAAMM>.dbo.ccp<AAAAMMDD>` desde `slc` (por defecto, vía linked server) o `db<AAAAMM>.dbo.ccp<AAAAMMDD>` en `rcc` (con `--pasivos-directo`; necesita `RCC_USER`/`RCC_PASSWORD`). Si no tienes credenciales de `rcc`, la verificación de la ruta directa sale `ERROR` y las demás se validan igual.

## Ejecutar
```bash
python main.py clientes-extranjeros              # corte = FECHA_CORTE_MENSUAL (.env)
python main.py clientes-extranjeros --fecha-corte 2026-07-31   # fecha puntual
python main.py clientes-extranjeros --fecha-seguros 2026-06-30   # seguros con otro corte
python main.py clientes-extranjeros --pasivos-directo            # si el linked server falla
```
## Validar
Si un bloque devuelve vacío el script sugiere la última fecha disponible: eso indica tabla desactualizada ⇒ [solicitud](./solicitud-actualizacion-tablas.md).
