# Proceso de cierre de mes

Objetivo: tener los reportes mensuales del corte sin sorpresas por tablas desactualizadas. Los ejecutas tú, uno por uno, cuando las tablas estén listas.

**Primero**: en el `.env` escribe `FECHA_CORTE_MENSUAL=AAAA-MM-DD` (último día del mes). Con eso no hace falta repetir `--fecha-corte` en cada comando.

## Día 1–2 · Antes de ejecutar (pre-vuelo)
1. `python main.py probar-conexiones`.
2. Para **cada** reporte mensual, verifica tablas:
   ```bash
   python main.py tablas bancarizados --verificar
   python main.py tablas bancarizados-producto --verificar
   python main.py tablas clientes-extranjeros --verificar
   python main.py tablas indicadores-clientes --verificar
   ```
   y el resto de reportes mensuales (`saldo-medio-vigente`, `fondeo-estable`, `heredados-pdm`, `giovanni-*`, `michael-*`, `desembolsos-por-canal`, …; lista en [comandos](./comandos.md)). Atajo por reporte: `python main.py <reporte> --solo-verificar`.
3. Junta todas las tablas `DESACTUALIZADA`/`NO EXISTE` y haz **una sola solicitud** a Producción ([guía](./solicitud-actualizacion-tablas.md)). Usa la sección «por tabla» del [inventario](../../data/tables-inventory.md) para ver qué reportes se destraban con cada tabla.

## Orden sugerido de ejecución
| Orden | Reporte | Por qué |
|---|---|---|
| 1 | `heredados-pdm` | exige validar Cubo y tablas PDM completas antes |
| 2 | `fondeo-estable`, `desembolsos-por-canal` | solo necesitan el cierre; plazo corto (día ~3) |
| 3 | `michael-captaciones`, `michael-castigos`, `giovanni-captaciones`, `giovanni-seguros`, `giovanni-cartera-agro`, `saldo-medio-vigente`, `tapp-saldo-medio-territorio` | cierre mes anterior y actual |
| 4 | `bancarizados`, `bancarizados-producto`, `clientes-extranjeros`, `indicadores-clientes`, `clientes-jovenes`, `productos-verdes`, `contratacion-electronica`, `clientes-rurales-migrantes` | las tablas RCC (`rccdet`, `ccp`) suelen llegar más tarde; verifícalas primero |
| Aparte | `saca-tu-garra` | 8:00–8:30 AM; no depende de los reportes de cierre pesados |

Es una sugerencia basada en las notas heredadas; el orden real lo manda la disponibilidad de tablas.

## Tablas que suelen retrasar el cierre (revisar primero)
- Dinámicas por fecha: `rccdet{yyyymmdd}`, `rcccab{yyyymmdd}`, `ccd{yyyymmdd}`, `ccp{yyyymmdd}` (existen solo cuando se carga el cierre).
- `csd.dbo.clientes_ds`, `intcom.dbo.ccd`, `intcom.dbo.ccs_fund_f`, `dwh.dbo.hcarcap001` (fecha de cierre).
- Cubo y tablas PDM (`dma.dbo.*`).

## Cuando todo está al día
Ejecuta cada reporte con su guía: [`bancarizados`](./bancarizados.md), [`bancarizados-producto`](./bancarizados-producto.md), [`clientes-extranjeros`](./clientes-extranjeros.md), [`indicadores-clientes`](./indicadores-clientes.md); los demás con su comando ([catálogo de comandos](./comandos.md)). El [procedimiento manual heredado](../../business/procedimientos_manuales_legado.md) queda como referencia (destinatarios y formato del correo).

## Cierre
Entregas hechas, bitácora al día, incidentes registrados. Si las tablas fallaron, anota a quién se pidió y cuánto tardó: alimenta el [roadmap](../../business/roadmap.md).
