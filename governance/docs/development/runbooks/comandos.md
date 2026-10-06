# Catálogo de comandos

> **Generado** por `governance/scripts/generar_inventario.py` desde `registro.py`, `tablas.py` y los módulos. No editar a mano.

Los reportes **los ejecutas tú, cuando quieras** (no hay tareas programadas): `python main.py <comando>`. La fecha de corte sale de `FECHA_CORTE_MENSUAL` / `FECHA_CORTE_DIARIA` del `.env`, o de `--fecha-corte AAAA-MM-DD` (que manda sobre el `.env`). El ejecutor común valida las tablas al corte (si falta alguna, **no ejecuta** y deja el mensaje para Producción), consulta, valida los datos y exporta el Excel a `data/outputs/mensuales/<piero|erick>/<NN_nombre>/` (diarios: `data/outputs/diarias/<NN_nombre>/`). La numeración es la de las carpetas del legado. Proceso completo: [ejecutar un reporte](./ejecutar-un-reporte.md).

Opciones comunes de los reportes de lote: `--solo-verificar` · `--forzar` · `--sin-verificar` · `--confirmar-escritura` (solo si escribe en BD) · `--salida DIR` · `-v`.

# Diarias (01 TAREAS DIARIAS)

## Diarias 02 · `cartera-sin-asignar` — diaria

Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación

```bash
python main.py tablas cartera-sin-asignar --verificar   # ¿tablas al día? (fecha del .env)
python main.py cartera-sin-asignar [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_DIARIA del .env
```

- **Servidor**: `mish` · **Tablas**: 7 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`, `storage.com_act.sdas001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/diarias/02_cartera_sin_asignar/Cartera-Sin asignar-{AAAA-MM-DD}.xlsx` · hojas: `DATA_MIS_v2`, `RESUMEN_v2` (resumen jerárquico)

## Diarias 04.1 · `cmg-mora` — diaria

Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0)

```bash
python main.py tablas cmg-mora --verificar   # ¿tablas al día? (fecha del .env)
python main.py cmg-mora [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_DIARIA del .env
```

- **Servidor**: `rcc` · **Tablas**: 6 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dbriesgos.dbo.gasto_prov_ope_diaria`, `dbriesgos.dbo.prov_proy_{yyyymmdd}_0`, `dbriesgos.dbo.recaudo_diario_finanzas`
- Guía propia: [runbook](./cmg-mora.md)

## Diarias 04.2 · `cmg-castigos` — diaria

CMG Mora · recuperación de castigos 12M (SRECCAST12M): suma de SDAS005 en los últimos 11 cierres

```bash
python main.py tablas cmg-castigos --verificar   # ¿tablas al día? (fecha del .env)
python main.py cmg-castigos [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_DIARIA del .env
```

- **Servidor**: `mish` · **Tablas**: 2 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.sdas005`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/diarias/04_cmg_mora/CmgCastigos_{AAAAMMDD}.xlsx` · hojas: `Castigos 12M`

# Mensuales · heredados de Piero

## Piero 01 · `desembolsos-por-canal` — mensual

Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT)

```bash
python main.py tablas desembolsos-por-canal --verificar   # ¿tablas al día? (fecha del .env)
python main.py desembolsos-por-canal [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 9 (5 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`, `storage.com_act.hcdr001`, `storage.com_act.hcdr002`, `storage.com_act.hdce001`, `storage.com_act.hmcm001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/01_desembolsos_por_canal/Desembolsos_canal_{AAAAMMDD}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)

## Piero 02 · `fondeo-estable` — mensual

Estadística de tramo / Fondeo estable (Eddy Martínez)

```bash
python main.py tablas fondeo-estable --verificar   # ¿tablas al día? (fecha del .env)
python main.py fondeo-estable [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 2 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_pas.wjas008`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/02_estadistica_de_tramo_fondeo_estable/Saldo_FondeoEstable_{AAAAMMDD}.xlsx` · hojas: `Datos`

## Piero 03 · `heredados-pdm` — mensual

Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar

```bash
python main.py tablas heredados-pdm --verificar   # ¿tablas al día? (fecha del .env)
python main.py heredados-pdm [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `slc` · **Tablas**: 10 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dma.dbo.hiscreditos`, `dma.dbo.hisgrupospdm`
- **Base de datos**: `slc` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/03_heredados_pdm/PDM Heredado {MES} {AA}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)
- ⚠ Antes de entregar valida que el Cubo y las tablas PDM estén completos a la fecha (si faltan datos el reporte sale mal).

## Piero 04.1 · `contratacion-electronica` — mensual

Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto)

```bash
python main.py tablas contratacion-electronica --verificar   # ¿tablas al día? (fecha del .env)
python main.py contratacion-electronica [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 2 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.wcdce001`, `storage.com_act.wcdce002`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/04_ratio_ce_clientes_nuevos_y_migrantes/ContratacionElectronica_{AAAAMMDD}.xlsx` · hojas: `CE habilitados`, `CE desembolsados`

## Piero 04.2 · `clientes-rurales-migrantes` — mensual

Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres

```bash
python main.py tablas clientes-rurales-migrantes --verificar   # ¿tablas al día? (fecha del .env)
python main.py clientes-rurales-migrantes [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 7 (4 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hbcn001`, `storage.com_act.hcda001`, `storage.com_act.hcdr001`, `storage.com_act.hcdr002`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/04_ratio_ce_clientes_nuevos_y_migrantes/ClientesRuralesMigrantes_{AAAAMMDD}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)

## Piero 05.1 · `giovanni-captaciones` — mensual

Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones

```bash
python main.py tablas giovanni-captaciones --verificar   # ¿tablas al día? (fecha del .env)
python main.py giovanni-captaciones [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 5 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_pas.sdps010`, `storage.com_pas.sdps013`, `storage.com_pas.wjas004`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/05_reportes_para_giovanni/Saldo Medio y Puntual Captaciones_{AAAAMMDD}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)

## Piero 05.2 · `giovanni-seguros` — mensual

Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar»

```bash
python main.py tablas giovanni-seguros --verificar   # ¿tablas al día? (fecha del .env)
python main.py giovanni-seguros [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 7 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.sdaf002`, `storage.com_seg.sdsf001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/05_reportes_para_giovanni/Reporte Seguros_{AAAAMMDD}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)

## Piero 05.3 · `giovanni-cartera-agro` — mensual

Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior)

```bash
python main.py tablas giovanni-cartera-agro --verificar   # ¿tablas al día? (fecha del .env)
python main.py giovanni-cartera-agro [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 6 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/05_reportes_para_giovanni/Cartera Vigente Agro_{AAAAMMDD}.xlsx` · hojas: `Saldo vigente`, `Saldo vigente (cierre anterior)`, `Clientes`

## Piero 06 · `saca-tu-garra` — mensual

Saca tu garra (Giancarlos): entregar 8:00–8:30 AM

```bash
python main.py tablas saca-tu-garra --verificar   # ¿tablas al día? (fecha del .env)
python main.py saca-tu-garra [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 6 (5 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcda001`, `storage.com_act.hcma001`, `storage.com_act.hctc001`, `storage.com_act.sdae002`, `storage.com_act.sdae003`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/06_saca_tu_garra/Base Saca tu Garra_{AAAAMMDD}.xlsx` · hojas: `Datos`

## Piero 07 · `saldo-medio-vigente` — mensual

Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios

```bash
python main.py tablas saldo-medio-vigente --verificar   # ¿tablas al día? (fecha del .env)
python main.py saldo-medio-vigente [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 2 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.sdas001`, `storage.com_act.wjas001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/07_saldo_medio_vigente/Saldo Medio Vigente_{AAAAMMDD}.xlsx` · hojas: `Saldo medio mes`, `Saldo diario`

## Piero 08 · `tapp-saldo-medio-territorio` — mensual

TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy)

```bash
python main.py tablas tapp-saldo-medio-territorio --verificar   # ¿tablas al día? (fecha del .env)
python main.py tapp-saldo-medio-territorio [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 7 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `appj.dbo.salmediovigente1`, `storage.com_act.sdaf002`, `storage.com_act.sdas001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/08_tapp_stock_tpp_mes_saldo_medio_vigente_territorio/SaldoMedio_TPPSTOCK_TPPMES_{AAAAMM}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)
- ⚠ **Escribe en BD** (crea/borra tablas permanentes): exige `--confirmar-escritura`
- ⚠ Este reporte crea/borra la tabla permanente appj.dbo.salmediovigente1 (como el proceso manual original).

## Piero 09.1 · `michael-captaciones` — mensual

Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos)

```bash
python main.py tablas michael-captaciones --verificar   # ¿tablas al día? (fecha del .env)
python main.py michael-captaciones [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 5 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_pas.hcdp001`, `storage.com_pas.wcap001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/09_reporte_mensual_michael_palacios/Datos Cierre {MES} {AA}.xlsx` · hojas: `Captaciones` · libro compartido con otro comando
- ⚠ Si WCAP001 no tiene la fecha, hay que correr antes el SP storage.com_pas.PSLWCAP001 (ver comentario del SQL original en docs/LEGADO).

## Piero 09.2 · `michael-castigos` — mensual

Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos)

```bash
python main.py tablas michael-castigos --verificar   # ¿tablas al día? (fecha del .env)
python main.py michael-castigos [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `mish` · **Tablas**: 9 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `storage.com_act.hcca001`, `storage.com_act.hcda001`
- **Base de datos**: `storage` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/piero/09_reporte_mensual_michael_palacios/Datos Cierre {MES} {AA}.xlsx` · hojas: `Castigos` · libro compartido con otro comando
- **Vacío válido**: sí (puede no haber datos en el mes)

# Mensuales · heredados de Erick

## Erick 01 · `productos-verdes` — mensual

Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas

```bash
python main.py tablas productos-verdes --verificar   # ¿tablas al día? (fecha del .env)
python main.py productos-verdes [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `slc` · **Tablas**: 13 (2 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dwh.dbo.hcarcre001`, `dwh.dbo.scarcre002`
- **Base de datos**: `slc` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/erick/01_productos_verdes/7. Productos_verdes_{mes3}{AA}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)

## Erick 02 · `clientes-jovenes` — mensual

Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años

```bash
python main.py tablas clientes-jovenes --verificar   # ¿tablas al día? (fecha del .env)
python main.py clientes-jovenes [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `slc` · **Tablas**: 5 (3 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `csd.dbo.clientes_ds`, `dwh.dbo.hcarcre001`, `dwh.dbo.scarcre006`
- **Base de datos**: `slc` (editable en el módulo; el servidor lo define el `.env`)
- **Salida**: `data/outputs/mensuales/erick/02_clientes_jovenes/Clientes_jóvenes_{mes3}{AA}.xlsx` · hojas: una hoja por resultado (`Datos`, `Datos_2`…)

## Erick 03.1 · `bancarizados` — mensual

Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio

```bash
python main.py tablas bancarizados --verificar   # ¿tablas al día? (fecha del .env)
python main.py bancarizados [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `rcc`, `slc` · **Tablas**: 7 (4 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `dbrcc.dbo.rcccab{yyyymmdd}`, `dbrcc.dbo.rccdet{yyyymmdd}`, `db{yyyymm}.dbo.ccd{yyyymmdd}`, `intcom.dbo.ccd`
- Guía propia: [runbook](./bancarizados.md)

## Erick 03.2 · `bancarizados-producto` — mensual

Bancarizados por producto (clientes nuevos con desembolso)

```bash
python main.py tablas bancarizados-producto --verificar   # ¿tablas al día? (fecha del .env)
python main.py bancarizados-producto [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `slc` · **Tablas**: 6 (1 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `csd.dbo.clientes_ds`
- Guía propia: [runbook](./bancarizados-producto.md)

## Erick 03.3 · `clientes-extranjeros` — mensual

Clientes por nacionalidad: créditos, pasivos y seguros

```bash
python main.py tablas clientes-extranjeros --verificar   # ¿tablas al día? (fecha del .env)
python main.py clientes-extranjeros [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `slc`, `rcc` · **Tablas**: 4 (4 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `intcom.dbo.ccd`, `intcom.dbo.ccs_fund_f`, `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}`, `db{yyyymm}.dbo.ccp{yyyymmdd}`
- Guía propia: [runbook](./clientes-extranjeros.md)

## Erick 03.4 · `indicadores-clientes` — mensual

Indicadores de clientes para el Directorio

```bash
python main.py tablas indicadores-clientes --verificar   # ¿tablas al día? (fecha del .env)
python main.py indicadores-clientes [--fecha-corte AAAA-MM-DD]   # sin la opción usa FECHA_CORTE_MENSUAL del .env
```

- **Servidor**: `slc` · **Tablas**: 10 (7 verificables por fecha) → [inventario](../../data/tables-inventory.md)
- **Críticas** (se validan al corte): `csd.dbo.clientes_ds`, `dwh.dbo.hcarcap001`, `dwh.dbo.scarcap001`, `dwh.dbo.scarcap003`, `intcom.bt.sngc13`, `intcom.dbo.ccd`, `intcom.dbo.ccs_fund_f`
- Guía propia: [runbook](./indicadores-clientes.md)

