# Catálogo de comandos

> **Generado** por `governance/scripts/generar_inventario.py` desde `registro.py`, `tablas.py` y los módulos. No editar a mano.

Todos los reportes se ejecutan igual: `python main.py <comando> --fecha-corte AAAA-MM-DD`. El ejecutor común valida las tablas al corte (si falta alguna, **no ejecuta** y deja el mensaje para Producción), consulta, valida los datos y exporta el Excel a `data/outputs/<comando>/`. Proceso completo: [ejecutar un reporte](./ejecutar-un-reporte.md).

Opciones comunes de los reportes de lote: `--solo-verificar` · `--forzar` · `--sin-verificar` · `--confirmar-escritura` (solo si escribe en BD) · `--salida DIR` · `-v`.

## `cmg-mora` — diaria

Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0)

```bash
python main.py tablas cmg-mora --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py cmg-mora [--fecha-corte AAAA-MM-DD]
```

- **Conexión**: `dw_raw` · **Tablas**: 6 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dbriesgos.dbo.gasto_prov_ope_diaria`, `dbriesgos.dbo.prov_proy_{yyyymmdd}_0`, `dbriesgos.dbo.recaudo_diario_finanzas`
- Guía propia: [runbook](./cmg-mora.md)

## `bancarizados` — mensual

Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio

```bash
python main.py tablas bancarizados --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py bancarizados --fecha-corte AAAA-MM-DD
```

- **Conexión**: `rcc`, `slc` · **Tablas**: 7 (4 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dbrcc.dbo.rcccab{yyyymmdd}`, `dbrcc.dbo.rccdet{yyyymmdd}`, `db{yyyymm}.dbo.ccd{yyyymmdd}`, `intcom.dbo.ccd`
- Guía propia: [runbook](./bancarizados.md)

## `bancarizados-producto` — mensual

Bancarizados por producto (clientes nuevos con desembolso)

```bash
python main.py tablas bancarizados-producto --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py bancarizados-producto --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 6 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `csd.dbo.clientes_ds`
- Guía propia: [runbook](./bancarizados-producto.md)

## `clientes-extranjeros` — mensual

Clientes por nacionalidad: créditos, pasivos y seguros

```bash
python main.py tablas clientes-extranjeros --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py clientes-extranjeros --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc`, `rcc` · **Tablas**: 2 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `intcom.dbo.ccd`, `intcom.dbo.ccs_fund_f`
- Guía propia: [runbook](./clientes-extranjeros.md)

## `indicadores-clientes` — mensual

Indicadores de clientes para el Directorio

```bash
python main.py tablas indicadores-clientes --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py indicadores-clientes --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 10 (7 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `csd.dbo.clientes_ds`, `dwh.dbo.hcarcap001`, `dwh.dbo.scarcap001`, `dwh.dbo.scarcap003`, `intcom.bt.sngc13`, `intcom.dbo.ccd`, `intcom.dbo.ccs_fund_f`
- Guía propia: [runbook](./indicadores-clientes.md)

## `cartera-sin-asignar` — diaria

Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación

```bash
python main.py tablas cartera-sin-asignar --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py cartera-sin-asignar [--fecha-corte AAAA-MM-DD]
```

- **Conexión**: `slc` · **Tablas**: 7 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`, `storage.com_act.sdas001`
- **Salida**: `data/outputs/cartera_sin_asignar/CarteraSinAsignar_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `cmg-castigos` — diaria

CMG Mora · recuperación de castigos 12M (SRECCAST12M): suma de SDAS005 en los últimos 11 cierres

```bash
python main.py tablas cmg-castigos --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py cmg-castigos [--fecha-corte AAAA-MM-DD]
```

- **Conexión**: `slc` · **Tablas**: 2 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.sdas005`
- **Salida**: `data/outputs/cmg_castigos/CmgCastigos_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `clientes-jovenes` — mensual

Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años

```bash
python main.py tablas clientes-jovenes --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py clientes-jovenes --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 5 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `csd.dbo.clientes_ds`, `dwh.dbo.hcarcre001`, `dwh.dbo.scarcre006`
- **Salida**: `data/outputs/clientes_jovenes/ClientesJovenes_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `desembolsos-por-canal` — mensual

Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT)

```bash
python main.py tablas desembolsos-por-canal --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py desembolsos-por-canal --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 9 (5 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`, `storage.com_act.hcdr001`, `storage.com_act.hcdr002`, `storage.com_act.hdce001`, `storage.com_act.hmcm001`
- **Salida**: `data/outputs/desembolsos_por_canal/DesembolsosPorCanal_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `fondeo-estable` — mensual

Estadística de tramo / Fondeo estable (Eddy Martínez)

```bash
python main.py tablas fondeo-estable --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py fondeo-estable --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 2 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_pas.wjas008`
- **Salida**: `data/outputs/fondeo_estable/FondeoEstable_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `heredados-pdm` — mensual

Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar

```bash
python main.py tablas heredados-pdm --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py heredados-pdm --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 10 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dma.dbo.hiscreditos`, `dma.dbo.hisgrupospdm`
- **Salida**: `data/outputs/heredados_pdm/HeredadosPdm_<AAAAMMDD>.xlsx` (+ hoja `Control`)
- ⚠ Antes de entregar valida que el Cubo y las tablas PDM estén completos a la fecha (si faltan datos el reporte sale mal).

## `productos-verdes` — mensual

Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas

```bash
python main.py tablas productos-verdes --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py productos-verdes --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 13 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dwh.dbo.hcarcre001`, `dwh.dbo.scarcre002`
- **Salida**: `data/outputs/productos_verdes/ProductosVerdes_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `contratacion-electronica` — mensual

Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto)

```bash
python main.py tablas contratacion-electronica --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py contratacion-electronica --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 2 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.wcdce001`, `storage.com_act.wcdce002`
- **Salida**: `data/outputs/contratacion_electronica/ContratacionElectronica_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `clientes-rurales-migrantes` — mensual

Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres

```bash
python main.py tablas clientes-rurales-migrantes --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py clientes-rurales-migrantes --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 7 (4 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hbcn001`, `storage.com_act.hcda001`, `storage.com_act.hcdr001`, `storage.com_act.hcdr002`
- **Salida**: `data/outputs/clientes_rurales_migrantes/ClientesRuralesMigrantes_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `michael-captaciones` — mensual

Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos)

```bash
python main.py tablas michael-captaciones --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py michael-captaciones --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 5 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_pas.hcdp001`, `storage.com_pas.wcap001`
- **Salida**: `data/outputs/michael_captaciones/MichaelCaptaciones_<AAAAMMDD>.xlsx` (+ hoja `Control`)
- ⚠ Si WCAP001 no tiene la fecha, hay que correr antes el SP storage.com_pas.PSLWCAP001 (ver comentario del SQL original en docs/LEGADO).

## `michael-castigos` — mensual

Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos)

```bash
python main.py tablas michael-castigos --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py michael-castigos --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 9 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcca001`, `storage.com_act.hcda001`
- **Salida**: `data/outputs/michael_castigos/MichaelCastigos_<AAAAMMDD>.xlsx` (+ hoja `Control`)
- **Vacío válido**: sí (puede no haber datos en el mes)

## `giovanni-captaciones` — mensual

Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones

```bash
python main.py tablas giovanni-captaciones --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py giovanni-captaciones --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 5 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_pas.sdps010`, `storage.com_pas.sdps013`, `storage.com_pas.wjas004`
- **Salida**: `data/outputs/giovanni_captaciones/GiovanniCaptaciones_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `giovanni-seguros` — mensual

Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar»

```bash
python main.py tablas giovanni-seguros --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py giovanni-seguros --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 7 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.sdaf002`, `storage.com_seg.sdsf001`
- **Salida**: `data/outputs/giovanni_seguros/GiovanniSeguros_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `giovanni-cartera-agro` — mensual

Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior)

```bash
python main.py tablas giovanni-cartera-agro --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py giovanni-cartera-agro --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 6 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`
- **Salida**: `data/outputs/giovanni_cartera_agro/GiovanniCarteraAgro_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `saca-tu-garra` — mensual

Saca tu garra (Giancarlos): entregar 8:00–8:30 AM

```bash
python main.py tablas saca-tu-garra --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py saca-tu-garra --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 6 (5 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`, `storage.com_act.hcma001`, `storage.com_act.hctc001`, `storage.com_act.sdae002`, `storage.com_act.sdae003`
- **Salida**: `data/outputs/saca_tu_garra/SacaTuGarra_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `saldo-medio-vigente` — mensual

Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios

```bash
python main.py tablas saldo-medio-vigente --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py saldo-medio-vigente --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 2 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.sdas001`, `storage.com_act.wjas001`
- **Salida**: `data/outputs/saldo_medio_vigente/SaldoMedioVigente_<AAAAMMDD>.xlsx` (+ hoja `Control`)

## `tapp-saldo-medio-territorio` — mensual

TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy)

```bash
python main.py tablas tapp-saldo-medio-territorio --fecha-corte AAAA-MM-DD --verificar   # ¿tablas al día?
python main.py tapp-saldo-medio-territorio --fecha-corte AAAA-MM-DD
```

- **Conexión**: `slc` · **Tablas**: 7 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `appj.dbo.salmediovigente1`, `storage.com_act.sdaf002`, `storage.com_act.sdas001`
- **Salida**: `data/outputs/tapp_saldo_medio_territorio/TappSaldoMedioTerritorio_<AAAAMMDD>.xlsx` (+ hoja `Control`)
- ⚠ **Escribe en BD** (crea/borra tablas permanentes): exige `--confirmar-escritura`
- ⚠ Este reporte crea/borra la tabla permanente appj.dbo.salmediovigente1 (como el proceso manual original).

