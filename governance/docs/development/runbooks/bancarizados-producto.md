# Runbook: `bancarizados-producto` (mensual)

**Conexión**: `slc`. **Salida**: `data/outputs/bancarizados_producto/BancarizadosProducto_<sufijo>.xlsx` (`resumen`, `comparativo`, `clientes`, `multiproducto`).

## Antes
```bash
python main.py tablas bancarizados-producto --verificar
```
Crítica: `csd.dbo.clientes_ds` (HFECPRO). El cierre se **detecta solo**: última fecha cargada dentro del mes; esa fecha va al SP `dwh.dbo.GDESEMCRE001`.

## Ejecutar
```bash
python main.py bancarizados-producto              # mes de FECHA_CORTE_MENSUAL (.env)
python main.py bancarizados-producto --mes 2026-06
python main.py bancarizados-producto --mes 2026-06 2025-06     # comparativo entre meses
```
## Validar
`resumen`: % bancarizados razonable; `multiproducto` explica diferencias entre clientes y operaciones.
