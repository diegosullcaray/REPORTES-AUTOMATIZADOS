# Inventario de tablas

> **Generado** desde `src/reportes/tablas.py` por `governance/scripts/generar_inventario.py`. No editar a mano; para cambiar algo edita `tablas.py` y regenera.

Sirve para el cierre de mes: saber **qué tablas necesita cada reporte** y **a qué reportes afecta una tabla** antes de pedir a Producción que la actualice. Proceso: [cierre de mes](../development/runbooks/proceso-cierre-de-mes.md).

- Tablas registradas: **89** · Reportes con tablas: **17**
- **Confianza** de la columna de fecha: `confirmada` (aparece en el SQL/código) · `convencion` (inferida por el prefijo H*/S* del core; **validar con el DBA**) · `por_confirmar`.

## 1. Por reporte (¿qué debo tener actualizado?)

### `bancarizados` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `dbrcc.dbo.rcccab{yyyymmdd}` | `rcc` | dinamica | — | por_confirmar |
| `dbrcc.dbo.rccdet{yyyymmdd}` | `rcc` | dinamica | — | por_confirmar |
| `db{yyyymm}.dbo.ccd{yyyymmdd}` | `rcc` | dinamica | — | por_confirmar |
| `dw_metadata.dbo.wjercor03` | `rcc` | otro | — | por_confirmar |
| `dw_raw.dbo.clientes` | `rcc` | otro | — | por_confirmar |
| `intcom.dbo.an_productos` | `slc` | otro | — | por_confirmar |
| `intcom.dbo.ccd` | `slc` | stock | `Fecha_Cierre` | confirmada |

### `bancarizados-producto` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `csd.dbo.clientes_ds` | `slc` | stock | `HFECPRO` | confirmada |
| `dwh.dbo.bregmod001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.gdesemcre001` | `slc` | procedimiento | — | por_confirmar |
| `dwh.dbo.rtipcre001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre002` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre003` | `slc` | referencia | — | por_confirmar |

### `cartera_sin_asignar` (diaria)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.sdas001` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.fjercor02` | `slc` | otro | — | por_confirmar |
| `storage.ref.vjercor03` | `slc` | otro | — | por_confirmar |

### `clientes-extranjeros` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `intcom.dbo.ccd` | `slc` | stock | `Fecha_Cierre` | confirmada |
| `intcom.dbo.ccs_fund_f` | `slc` | stock | `fecha_reporte` | confirmada |

### `clientes_jovenes` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `csd.dbo.clientes_ds` | `slc` | stock | `HFECPRO` | confirmada |
| `dwh.dbo.bregper001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.gdesemcre001` | `slc` | procedimiento | — | por_confirmar |
| `dwh.dbo.hcarcre001` | `slc` | historica | `HFECPRO` | convencion |
| `dwh.dbo.scarcre006` | `slc` | stock | `SFECPRO` | convencion |

### `cmg-mora` (diaria)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `dw_raw` | stock | `FC_DIA` | confirmada |
| `dbriesgos.dbo.prov_proy_{yyyymmdd}_0` | `dw_raw` | dinamica | — | por_confirmar |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `dw_raw` | stock | `FECHA_CIERRE` | confirmada |
| `dw_raw_v2.dbo.cmgmora_recaudo` | `dw_raw` | staging | — | por_confirmar |
| `dw_raw_v2.dbo.cmgmora_strjercor` | `dw_raw` | otro | — | por_confirmar |
| `storage.com_act.sbtvrie001` | `slc` | destino | — | por_confirmar |
| `storage.com_act.sdas005` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |

### `desembolsos_por_canal` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr002` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hdce001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hmcm001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_act.rfoc001` | `slc` | referencia | — | por_confirmar |
| `storage.gpr.vpph001` | `slc` | otro | — | por_confirmar |
| `storage.ref.fjercor02` | `slc` | otro | — | por_confirmar |
| `storage.ref.rtcm001` | `slc` | referencia | — | por_confirmar |

### `fondeo_estable` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_pas.wjas008` | `slc` | otro | — | por_confirmar |
| `storage.ref.vjercor04` | `slc` | otro | — | por_confirmar |

### `heredados_pdm` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `dma.dbo.fecciebt` | `slc` | otro | — | por_confirmar |
| `dma.dbo.hiscreditos` | `slc` | historica | `HFECPRO` | convencion |
| `dma.dbo.hisgrupospdm` | `slc` | historica | `HFECPRO` | confirmada |
| `dma.dbo.mrvgrupopdm` | `slc` | otro | — | por_confirmar |
| `dwh.dbo.bregmod001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.bregubt001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rregope001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre002` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre003` | `slc` | referencia | — | por_confirmar |

### `indicadores-clientes` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `csd.dbo.clientes_ds` | `slc` | stock | `HFECPRO` | confirmada |
| `dwh.dbo.bregper001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.hcarcap001` | `slc` | historica | `HFECPRO` | confirmada |
| `dwh.dbo.scarcap001` | `slc` | stock | `SFECPRO` | convencion |
| `dwh.dbo.scarcap003` | `slc` | stock | `SFECPRO` | convencion |
| `intcom.bt.fsd002` | `slc` | otro | — | por_confirmar |
| `intcom.bt.sngc13` | `slc` | stock | `FECHA_REPORTE` | confirmada |
| `intcom.dbo.ccd` | `slc` | stock | `Fecha_Cierre` | confirmada |
| `intcom.dbo.ccs_fund_f` | `slc` | stock | `fecha_reporte` | confirmada |
| `intcom.dbo.distritos_rural_alv` | `slc` | otro | — | por_confirmar |

### `productos_verdes` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `dwh.dbo.bregmod001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.bregper001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.bregubt001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.gdesemcre001` | `slc` | procedimiento | — | por_confirmar |
| `dwh.dbo.gjerreg001` | `slc` | otro | — | por_confirmar |
| `dwh.dbo.hcarcre001` | `slc` | historica | `HFECPRO` | convencion |
| `dwh.dbo.rfecsis001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre002` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.rtipcre003` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.scarcre002` | `slc` | stock | `SFECPRO` | convencion |
| `dwh.dbo.vplaper001` | `slc` | otro | — | por_confirmar |
| `slc.dbo.retp006` | `slc` | referencia | — | por_confirmar |

### `ratio_ce_nuevos_migrantes` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hbcn001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr002` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.rfoc001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.wcdce001` | `slc` | otro | — | por_confirmar |
| `storage.com_act.wcdce002` | `slc` | otro | — | por_confirmar |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |
| `storage.ref.vurbrur01` | `slc` | otro | — | por_confirmar |

### `reporte_michael_palacios` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcca001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.rfoc001` | `slc` | referencia | — | por_confirmar |
| `storage.com_pas.hcdp001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_pas.pslwcap001` | `slc` | otro | — | por_confirmar |
| `storage.com_pas.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_pas.wcap001` | `slc` | otro | — | por_confirmar |
| `storage.gpr.vpph001` | `slc` | otro | — | por_confirmar |
| `storage.ref.fjercor01` | `slc` | otro | — | por_confirmar |
| `storage.ref.rtcm001` | `slc` | referencia | — | por_confirmar |
| `storage.ref.vjercor04` | `slc` | otro | — | por_confirmar |

### `reportes_giovanni` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com.vdmcom01` | `slc` | otro | — | por_confirmar |
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.sdaf002` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_pas.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_pas.sdps010` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_pas.sdps013` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_pas.wjas004` | `slc` | otro | — | por_confirmar |
| `storage.com_seg.sdsf001` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.fjercor02` | `slc` | otro | — | por_confirmar |
| `storage.ref.vjercor04` | `slc` | otro | — | por_confirmar |
| `storage.ref.wjercor03` | `slc` | otro | — | por_confirmar |

### `saca_tu_garra` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcma001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_act.hctc001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_act.sdae002` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_act.sdae003` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |

### `saldo_medio_vigente` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.sdas001` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_act.wjas001` | `slc` | otro | — | por_confirmar |

### `tapp_saldo_medio_territorio` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `appj.dbo.salmediovigente1` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.sdaf002` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_act.sdas001` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.fjercor02` | `slc` | otro | — | por_confirmar |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |
| `storage.util.fvecfec01` | `slc` | otro | — | por_confirmar |

## 2. Por tabla (si se actualiza esta, ¿a qué reportes afecta?)

| Tabla | Conexión | Tipo | Reportes |
|---|---|---|---|
| `appj.dbo.salmediovigente1` | `slc` | historica | `tapp_saldo_medio_territorio` |
| `csd.dbo.clientes_ds` | `slc` | stock | `bancarizados-producto`, `clientes_jovenes`, `indicadores-clientes` |
| `dbrcc.dbo.rcccab{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `dbrcc.dbo.rccdet{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `dw_raw` | stock | `cmg-mora` |
| `dbriesgos.dbo.prov_proy_{yyyymmdd}_0` | `dw_raw` | dinamica | `cmg-mora` |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `dw_raw` | stock | `cmg-mora` |
| `db{yyyymm}.dbo.ccd{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `db{yyyymm}.dbo.ccp{yyyymmdd}` | `rcc` | dinamica | — (solo SQL legado) |
| `dma.dbo.fecciebt` | `slc` | otro | `heredados_pdm` |
| `dma.dbo.hiscreditos` | `slc` | historica | `heredados_pdm` |
| `dma.dbo.hisgrupospdm` | `slc` | historica | `heredados_pdm` |
| `dma.dbo.mrvgrupopdm` | `slc` | otro | `heredados_pdm` |
| `dw_metadata.dbo.wjercor03` | `rcc` | otro | `bancarizados` |
| `dw_raw.dbo.clientes` | `rcc` | otro | `bancarizados` |
| `dw_raw_v2.dbo.cmgmora_recaudo` | `dw_raw` | staging | `cmg-mora` |
| `dw_raw_v2.dbo.cmgmora_strjercor` | `dw_raw` | otro | `cmg-mora` |
| `dwh.dbo.bregcap001` | `slc` | referencia | — (solo SQL legado) |
| `dwh.dbo.bregmod001` | `slc` | referencia | `bancarizados-producto`, `heredados_pdm`, `productos_verdes` |
| `dwh.dbo.bregmod002` | `slc` | referencia | — (solo SQL legado) |
| `dwh.dbo.bregper001` | `slc` | referencia | `clientes_jovenes`, `indicadores-clientes`, `productos_verdes` |
| `dwh.dbo.bregubt001` | `slc` | referencia | `heredados_pdm`, `productos_verdes` |
| `dwh.dbo.gdesemcre001` | `slc` | procedimiento | `bancarizados-producto`, `clientes_jovenes`, `productos_verdes` |
| `dwh.dbo.gjerreg001` | `slc` | otro | `productos_verdes` |
| `dwh.dbo.hcarcap001` | `slc` | historica | `indicadores-clientes` |
| `dwh.dbo.hcarcre001` | `slc` | historica | `clientes_jovenes`, `productos_verdes` |
| `dwh.dbo.rfecsis001` | `slc` | referencia | `productos_verdes` |
| `dwh.dbo.rregope001` | `slc` | referencia | `heredados_pdm` |
| `dwh.dbo.rtipcre001` | `slc` | referencia | `bancarizados-producto`, `heredados_pdm`, `productos_verdes` |
| `dwh.dbo.rtipcre002` | `slc` | referencia | `bancarizados-producto`, `heredados_pdm`, `productos_verdes` |
| `dwh.dbo.rtipcre003` | `slc` | referencia | `bancarizados-producto`, `heredados_pdm`, `productos_verdes` |
| `dwh.dbo.scarcap001` | `slc` | stock | `indicadores-clientes` |
| `dwh.dbo.scarcap002` | `slc` | stock | — (solo SQL legado) |
| `dwh.dbo.scarcap003` | `slc` | stock | `indicadores-clientes` |
| `dwh.dbo.scarcap004` | `slc` | stock | — (solo SQL legado) |
| `dwh.dbo.scarcre002` | `slc` | stock | `productos_verdes` |
| `dwh.dbo.scarcre006` | `slc` | stock | `clientes_jovenes` |
| `dwh.dbo.vplaper001` | `slc` | otro | `productos_verdes` |
| `intcom.bt.fsd002` | `slc` | otro | `indicadores-clientes` |
| `intcom.bt.sngc13` | `slc` | stock | `indicadores-clientes` |
| `intcom.dbo.an_productos` | `slc` | otro | `bancarizados` |
| `intcom.dbo.ccd` | `slc` | stock | `bancarizados`, `clientes-extranjeros`, `indicadores-clientes` |
| `intcom.dbo.ccs_fund_f` | `slc` | stock | `clientes-extranjeros`, `indicadores-clientes` |
| `intcom.dbo.clientes_netos_ds` | `slc` | otro | — (solo SQL legado) |
| `intcom.dbo.distritos_rural_alv` | `slc` | otro | `indicadores-clientes` |
| `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}` | `slc` | dinamica | — (solo SQL legado) |
| `slc.dbo.retp006` | `slc` | referencia | `productos_verdes` |
| `storage.com.vdmcom01` | `slc` | otro | `reportes_giovanni` |
| `storage.com_act.hbcn001` | `slc` | historica | `ratio_ce_nuevos_migrantes` |
| `storage.com_act.hcca001` | `slc` | historica | `reporte_michael_palacios` |
| `storage.com_act.hcda001` | `slc` | historica | `cartera_sin_asignar`, `desembolsos_por_canal`, `ratio_ce_nuevos_migrantes`, `reporte_michael_palacios`, `reportes_giovanni`, `saca_tu_garra` |
| `storage.com_act.hcdr001` | `slc` | historica | `desembolsos_por_canal`, `ratio_ce_nuevos_migrantes` |
| `storage.com_act.hcdr002` | `slc` | historica | `desembolsos_por_canal`, `ratio_ce_nuevos_migrantes` |
| `storage.com_act.hcma001` | `slc` | historica | `saca_tu_garra` |
| `storage.com_act.hctc001` | `slc` | historica | `saca_tu_garra` |
| `storage.com_act.hdce001` | `slc` | historica | `desembolsos_por_canal` |
| `storage.com_act.hmcm001` | `slc` | historica | `desembolsos_por_canal` |
| `storage.com_act.retp001` | `slc` | referencia | `cartera_sin_asignar`, `reporte_michael_palacios`, `reportes_giovanni`, `tapp_saldo_medio_territorio` |
| `storage.com_act.retp002` | `slc` | referencia | `cartera_sin_asignar`, `reporte_michael_palacios`, `reportes_giovanni` |
| `storage.com_act.retp003` | `slc` | referencia | `cartera_sin_asignar`, `reporte_michael_palacios`, `reportes_giovanni` |
| `storage.com_act.rfoc001` | `slc` | referencia | `desembolsos_por_canal`, `ratio_ce_nuevos_migrantes`, `reporte_michael_palacios` |
| `storage.com_act.sbtvrie001` | `slc` | destino | `cmg-mora` |
| `storage.com_act.sdae002` | `slc` | stock | `saca_tu_garra` |
| `storage.com_act.sdae003` | `slc` | stock | `saca_tu_garra` |
| `storage.com_act.sdaf002` | `slc` | stock | `reportes_giovanni`, `tapp_saldo_medio_territorio` |
| `storage.com_act.sdas001` | `slc` | stock | `cartera_sin_asignar`, `saldo_medio_vigente`, `tapp_saldo_medio_territorio` |
| `storage.com_act.sdas005` | `slc` | stock | `cmg-mora` |
| `storage.com_act.wcdce001` | `slc` | otro | `ratio_ce_nuevos_migrantes` |
| `storage.com_act.wcdce002` | `slc` | otro | `ratio_ce_nuevos_migrantes` |
| `storage.com_act.wjas001` | `slc` | otro | `saldo_medio_vigente` |
| `storage.com_pas.hcdp001` | `slc` | historica | `reporte_michael_palacios` |
| `storage.com_pas.pslwcap001` | `slc` | otro | `reporte_michael_palacios` |
| `storage.com_pas.retp001` | `slc` | referencia | `reporte_michael_palacios`, `reportes_giovanni` |
| `storage.com_pas.sdps010` | `slc` | stock | `reportes_giovanni` |
| `storage.com_pas.sdps013` | `slc` | stock | `reportes_giovanni` |
| `storage.com_pas.wcap001` | `slc` | otro | `reporte_michael_palacios` |
| `storage.com_pas.wjas004` | `slc` | otro | `reportes_giovanni` |
| `storage.com_pas.wjas008` | `slc` | otro | `fondeo_estable` |
| `storage.com_seg.sdsf001` | `slc` | stock | `reportes_giovanni` |
| `storage.gpr.vpph001` | `slc` | otro | `desembolsos_por_canal`, `reporte_michael_palacios` |
| `storage.ref.fjercor01` | `slc` | otro | `reporte_michael_palacios` |
| `storage.ref.fjercor02` | `slc` | otro | `cartera_sin_asignar`, `desembolsos_por_canal`, `reportes_giovanni`, `tapp_saldo_medio_territorio` |
| `storage.ref.rcalen001` | `slc` | referencia | `cmg-mora`, `ratio_ce_nuevos_migrantes`, `saca_tu_garra`, `tapp_saldo_medio_territorio` |
| `storage.ref.rtcm001` | `slc` | referencia | `desembolsos_por_canal`, `reporte_michael_palacios` |
| `storage.ref.vjercor03` | `slc` | otro | `cartera_sin_asignar` |
| `storage.ref.vjercor04` | `slc` | otro | `fondeo_estable`, `reporte_michael_palacios`, `reportes_giovanni` |
| `storage.ref.vurbrur01` | `slc` | otro | `ratio_ce_nuevos_migrantes` |
| `storage.ref.wjercor03` | `slc` | otro | `reportes_giovanni` |
| `storage.util.fvecfec01` | `slc` | otro | `tapp_saldo_medio_territorio` |
