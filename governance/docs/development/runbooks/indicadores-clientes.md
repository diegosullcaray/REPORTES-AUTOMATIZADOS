# Runbook: `indicadores-clientes` (mensual, Directorio)

**Conexión**: `slc`. **Salida**: `data/outputs/indicadores_clientes/IndicadoresClientes_<AAAAMM>.xlsx` (`resumen`, `detalle`).

## Antes
```bash
python main.py tablas indicadores-clientes --verificar
```
Críticas: `intcom.dbo.ccd`, `csd.dbo.clientes_ds`, `dwh.dbo.hcarcap001`, `intcom.dbo.ccs_fund_f`. **Desfase**: Nuevos y Seguros usan un mes antes del `--mes` (por defecto); al verificar tablas, usa también el corte del mes anterior para esas dos.

## Ejecutar
```bash
python main.py indicadores-clientes               # mes de FECHA_CORTE_MENSUAL (.env)
python main.py indicadores-clientes --mes 2026-07
python main.py indicadores-clientes --mes 2026-07 --reportes pasivos seguros
python main.py indicadores-clientes --mes 2026-07 --desfase seguros=2 --hilos 4
```
El cierre se detecta solo (última fecha cargada dentro del mes). Calcula también el mismo mes del año anterior (variación anual).

## Validar
`resumen`: participaciones suman ~100 %; revisa que no haya categorías vacías por tabla sin cargar.
