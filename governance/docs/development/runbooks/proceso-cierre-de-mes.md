# Proceso de cierre de mes

Objetivo: tener todos los reportes mensuales del corte `<corte>` sin sorpresas por tablas desactualizadas.

## Día 1–2 · Antes de ejecutar (pre-vuelo)
1. `python main.py probar-conexiones`.
2. Para **cada** reporte mensual, verifica tablas:
   ```bash
   python main.py tablas bancarizados            --fecha-corte <corte> --verificar
   python main.py tablas bancarizados-producto   --fecha-corte <corte> --verificar
   python main.py tablas clientes-extranjeros    --fecha-corte <corte> --verificar
   python main.py tablas indicadores-clientes    --fecha-corte <corte> --verificar
   ```
   y, para los aún manuales, el nombre de su carpeta en `sql/mensuales/` (p. ej. `saldo_medio_vigente`, `fondeo_estable`, `heredados_pdm`, `reportes_giovanni`, `reporte_michael_palacios`, `desembolsos_por_canal`).
3. Junta todas las tablas `DESACTUALIZADA`/`NO EXISTE` y haz **una sola solicitud** a Producción ([guía](./solicitud-actualizacion-tablas.md)). Usa la sección «por tabla» del [inventario](../../data/tables-inventory.md) para ver qué reportes se destraban con cada tabla.

## Orden sugerido de ejecución
| Orden | Reporte | Por qué |
|---|---|---|
| 1 | `heredados_pdm` | exige validar Cubo y tablas PDM completas antes |
| 2 | `fondeo_estable`, `desembolsos_por_canal` | solo necesitan el cierre; plazo corto (día ~3) |
| 3 | `reporte_michael_palacios`, `reportes_giovanni`, `saldo_medio_vigente`, `tapp_saldo_medio_territorio` | cierre mes anterior y actual |
| 4 | `bancarizados`, `bancarizados-producto`, `clientes-extranjeros`, `indicadores-clientes` | las tablas RCC (`rccdet`, `ccp`) suelen llegar más tarde; verifícalas primero |
| Aparte | `saca_tu_garra` | 8:00–8:30 AM; no depende de los reportes de cierre pesados |

Es una sugerencia basada en las notas heredadas; el orden real lo manda la disponibilidad de tablas.

## Tablas que suelen retrasar el cierre (revisar primero)
- Dinámicas por fecha: `rccdet{yyyymmdd}`, `rcccab{yyyymmdd}`, `ccd{yyyymmdd}`, `ccp{yyyymmdd}` (existen solo cuando se carga el cierre).
- `csd.dbo.clientes_ds`, `intcom.dbo.ccd`, `intcom.dbo.ccs_fund_f`, `dwh.dbo.hcarcap001` (fecha de cierre).
- Cubo y tablas PDM (`dma.dbo.*`).

## Cuando todo está al día
Ejecuta cada reporte con su guía: [`bancarizados`](./bancarizados.md), [`bancarizados-producto`](./bancarizados-producto.md), [`clientes-extranjeros`](./clientes-extranjeros.md), [`indicadores-clientes`](./indicadores-clientes.md); el resto con el [procedimiento heredado](../../business/procedimientos_manuales_legado.md).

## Cierre
Entregas hechas, bitácora al día, incidentes registrados. Si las tablas fallaron, anota a quién se pidió y cuánto tardó: alimenta el [roadmap](../../business/roadmap.md).
