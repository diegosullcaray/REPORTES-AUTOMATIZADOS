# Inventario de tablas

> **Generado** desde `src/reportes/tablas.py` por `governance/scripts/generar_inventario.py`. No editar a mano; para cambiar algo edita `tablas.py` y regenera.

Sirve para el cierre de mes: saber **qué tablas necesita cada reporte** y **a qué reportes afecta una tabla** antes de pedir a Producción que la actualice. Proceso: [cierre de mes](../development/runbooks/proceso-cierre-de-mes.md).

- Tablas registradas: **89** · Reportes con tablas: **22**
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

### `cartera-sin-asignar` (diaria)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.sdas001` | `slc` | stock | `sfecpro` | confirmada |
| `storage.ref.fjercor02` | `slc` | otro | — | por_confirmar |
| `storage.ref.vjercor03` | `slc` | otro | — | por_confirmar |

### `clientes-extranjeros` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `intcom.dbo.ccd` | `slc` | stock | `Fecha_Cierre` | confirmada |
| `intcom.dbo.ccs_fund_f` | `slc` | stock | `fecha_reporte` | confirmada |

### `clientes-jovenes` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `csd.dbo.clientes_ds` | `slc` | stock | `HFECPRO` | confirmada |
| `dwh.dbo.bregper001` | `slc` | referencia | — | por_confirmar |
| `dwh.dbo.gdesemcre001` | `slc` | procedimiento | — | por_confirmar |
| `dwh.dbo.hcarcre001` | `slc` | historica | `HFECPRO` | convencion |
| `dwh.dbo.scarcre006` | `slc` | stock | `SFECPRO` | convencion |

### `clientes-rurales-migrantes` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hbcn001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr002` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.rfoc001` | `slc` | referencia | — | por_confirmar |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |
| `storage.ref.vurbrur01` | `slc` | otro | — | por_confirmar |

### `cmg-castigos` (diaria)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.sdas005` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |

### `cmg-mora` (diaria)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `rcc` | stock | `FC_DIA` | confirmada |
| `dbriesgos.dbo.prov_proy_{yyyymmdd}_0` | `rcc` | dinamica | — | por_confirmar |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `rcc` | stock | `FECHA_CIERRE` | confirmada |
| `dw_raw_v2.dbo.cmgmora_recaudo` | `rcc` | staging | — | por_confirmar |
| `dw_raw_v2.dbo.cmgmora_strjercor` | `rcc` | otro | — | por_confirmar |
| `storage.com_act.sbtvrie001` | `slc` | destino | — | por_confirmar |

### `contratacion-electronica` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.wcdce001` | `slc` | historica | `hfecpro` | confirmada |
| `storage.com_act.wcdce002` | `slc` | historica | `hfecpro` | confirmada |

### `desembolsos-por-canal` (mensual)

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

### `fondeo-estable` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_pas.wjas008` | `slc` | historica | `hfecpro` | confirmada |
| `storage.ref.vjercor04` | `slc` | otro | — | por_confirmar |

### `giovanni-captaciones` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_pas.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_pas.sdps010` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_pas.sdps013` | `slc` | stock | `SFECPRO` | confirmada |
| `storage.com_pas.wjas004` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.ref.vjercor04` | `slc` | otro | — | por_confirmar |

### `giovanni-cartera-agro` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `slc` | referencia | — | por_confirmar |
| `storage.ref.fjercor02` | `slc` | otro | — | por_confirmar |
| `storage.ref.wjercor03` | `slc` | otro | — | por_confirmar |

### `giovanni-seguros` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com.vdmcom01` | `slc` | otro | — | por_confirmar |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.sdaf002` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_seg.sdsf001` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.wjercor03` | `slc` | otro | — | por_confirmar |

### `heredados-pdm` (mensual)

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

### `michael-captaciones` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_pas.hcdp001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_pas.pslwcap001` | `slc` | otro | — | por_confirmar |
| `storage.com_pas.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_pas.wcap001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.ref.vjercor04` | `slc` | otro | — | por_confirmar |

### `michael-castigos` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcca001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.rfoc001` | `slc` | referencia | — | por_confirmar |
| `storage.gpr.vpph001` | `slc` | otro | — | por_confirmar |
| `storage.ref.fjercor01` | `slc` | otro | — | por_confirmar |
| `storage.ref.rtcm001` | `slc` | referencia | — | por_confirmar |

### `productos-verdes` (mensual)

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

### `saca-tu-garra` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcma001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_act.hctc001` | `slc` | historica | `HFECPRO` | convencion |
| `storage.com_act.sdae002` | `slc` | stock | `sfecpro` | confirmada |
| `storage.com_act.sdae003` | `slc` | stock | `SFECPRO` | convencion |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |

### `saldo-medio-vigente` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.sdas001` | `slc` | stock | `sfecpro` | confirmada |
| `storage.com_act.wjas001` | `slc` | historica | `HFECPRO` | confirmada |

### `tapp-saldo-medio-territorio` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `appj.dbo.salmediovigente1` | `slc` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `slc` | referencia | — | por_confirmar |
| `storage.com_act.sdaf002` | `slc` | stock | `SFECPRO` | convencion |
| `storage.com_act.sdas001` | `slc` | stock | `sfecpro` | confirmada |
| `storage.ref.fjercor02` | `slc` | otro | — | por_confirmar |
| `storage.ref.rcalen001` | `slc` | referencia | — | por_confirmar |
| `storage.util.fvecfec01` | `slc` | otro | — | por_confirmar |

## 2. Por tabla (si se actualiza esta, ¿a qué reportes afecta?)

| Tabla | Conexión | Tipo | Reportes |
|---|---|---|---|
| `appj.dbo.salmediovigente1` | `slc` | historica | `tapp-saldo-medio-territorio` |
| `csd.dbo.clientes_ds` | `slc` | stock | `bancarizados-producto`, `clientes-jovenes`, `indicadores-clientes` |
| `dbrcc.dbo.rcccab{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `dbrcc.dbo.rccdet{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `rcc` | stock | `cmg-mora` |
| `dbriesgos.dbo.prov_proy_{yyyymmdd}_0` | `rcc` | dinamica | `cmg-mora` |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `rcc` | stock | `cmg-mora` |
| `db{yyyymm}.dbo.ccd{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `db{yyyymm}.dbo.ccp{yyyymmdd}` | `rcc` | dinamica | — (solo SQL legado) |
| `dma.dbo.fecciebt` | `slc` | otro | `heredados-pdm` |
| `dma.dbo.hiscreditos` | `slc` | historica | `heredados-pdm` |
| `dma.dbo.hisgrupospdm` | `slc` | historica | `heredados-pdm` |
| `dma.dbo.mrvgrupopdm` | `slc` | otro | `heredados-pdm` |
| `dw_metadata.dbo.wjercor03` | `rcc` | otro | `bancarizados` |
| `dw_raw.dbo.clientes` | `rcc` | otro | `bancarizados` |
| `dw_raw_v2.dbo.cmgmora_recaudo` | `rcc` | staging | `cmg-mora` |
| `dw_raw_v2.dbo.cmgmora_strjercor` | `rcc` | otro | `cmg-mora` |
| `dwh.dbo.bregcap001` | `slc` | referencia | — (solo SQL legado) |
| `dwh.dbo.bregmod001` | `slc` | referencia | `bancarizados-producto`, `heredados-pdm`, `productos-verdes` |
| `dwh.dbo.bregmod002` | `slc` | referencia | — (solo SQL legado) |
| `dwh.dbo.bregper001` | `slc` | referencia | `clientes-jovenes`, `indicadores-clientes`, `productos-verdes` |
| `dwh.dbo.bregubt001` | `slc` | referencia | `heredados-pdm`, `productos-verdes` |
| `dwh.dbo.gdesemcre001` | `slc` | procedimiento | `bancarizados-producto`, `clientes-jovenes`, `productos-verdes` |
| `dwh.dbo.gjerreg001` | `slc` | otro | `productos-verdes` |
| `dwh.dbo.hcarcap001` | `slc` | historica | `indicadores-clientes` |
| `dwh.dbo.hcarcre001` | `slc` | historica | `clientes-jovenes`, `productos-verdes` |
| `dwh.dbo.rfecsis001` | `slc` | referencia | `productos-verdes` |
| `dwh.dbo.rregope001` | `slc` | referencia | `heredados-pdm` |
| `dwh.dbo.rtipcre001` | `slc` | referencia | `bancarizados-producto`, `heredados-pdm`, `productos-verdes` |
| `dwh.dbo.rtipcre002` | `slc` | referencia | `bancarizados-producto`, `heredados-pdm`, `productos-verdes` |
| `dwh.dbo.rtipcre003` | `slc` | referencia | `bancarizados-producto`, `heredados-pdm`, `productos-verdes` |
| `dwh.dbo.scarcap001` | `slc` | stock | `indicadores-clientes` |
| `dwh.dbo.scarcap002` | `slc` | stock | — (solo SQL legado) |
| `dwh.dbo.scarcap003` | `slc` | stock | `indicadores-clientes` |
| `dwh.dbo.scarcap004` | `slc` | stock | — (solo SQL legado) |
| `dwh.dbo.scarcre002` | `slc` | stock | `productos-verdes` |
| `dwh.dbo.scarcre006` | `slc` | stock | `clientes-jovenes` |
| `dwh.dbo.vplaper001` | `slc` | otro | `productos-verdes` |
| `intcom.bt.fsd002` | `slc` | otro | `indicadores-clientes` |
| `intcom.bt.sngc13` | `slc` | stock | `indicadores-clientes` |
| `intcom.dbo.an_productos` | `slc` | otro | `bancarizados` |
| `intcom.dbo.ccd` | `slc` | stock | `bancarizados`, `clientes-extranjeros`, `indicadores-clientes` |
| `intcom.dbo.ccs_fund_f` | `slc` | stock | `clientes-extranjeros`, `indicadores-clientes` |
| `intcom.dbo.clientes_netos_ds` | `slc` | otro | — (solo SQL legado) |
| `intcom.dbo.distritos_rural_alv` | `slc` | otro | `indicadores-clientes` |
| `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}` | `slc` | dinamica | — (solo SQL legado) |
| `slc.dbo.retp006` | `slc` | referencia | `productos-verdes` |
| `storage.com.vdmcom01` | `slc` | otro | `giovanni-seguros` |
| `storage.com_act.hbcn001` | `slc` | historica | `clientes-rurales-migrantes` |
| `storage.com_act.hcca001` | `slc` | historica | `michael-castigos` |
| `storage.com_act.hcda001` | `slc` | historica | `cartera-sin-asignar`, `clientes-rurales-migrantes`, `desembolsos-por-canal`, `giovanni-cartera-agro`, `michael-castigos`, `saca-tu-garra` |
| `storage.com_act.hcdr001` | `slc` | historica | `clientes-rurales-migrantes`, `desembolsos-por-canal` |
| `storage.com_act.hcdr002` | `slc` | historica | `clientes-rurales-migrantes`, `desembolsos-por-canal` |
| `storage.com_act.hcma001` | `slc` | historica | `saca-tu-garra` |
| `storage.com_act.hctc001` | `slc` | historica | `saca-tu-garra` |
| `storage.com_act.hdce001` | `slc` | historica | `desembolsos-por-canal` |
| `storage.com_act.hmcm001` | `slc` | historica | `desembolsos-por-canal` |
| `storage.com_act.retp001` | `slc` | referencia | `cartera-sin-asignar`, `giovanni-cartera-agro`, `giovanni-seguros`, `michael-castigos`, `tapp-saldo-medio-territorio` |
| `storage.com_act.retp002` | `slc` | referencia | `cartera-sin-asignar`, `giovanni-cartera-agro`, `giovanni-seguros`, `michael-castigos` |
| `storage.com_act.retp003` | `slc` | referencia | `cartera-sin-asignar`, `giovanni-cartera-agro`, `giovanni-seguros`, `michael-castigos` |
| `storage.com_act.rfoc001` | `slc` | referencia | `clientes-rurales-migrantes`, `desembolsos-por-canal`, `michael-castigos` |
| `storage.com_act.sbtvrie001` | `slc` | destino | `cmg-mora` |
| `storage.com_act.sdae002` | `slc` | stock | `saca-tu-garra` |
| `storage.com_act.sdae003` | `slc` | stock | `saca-tu-garra` |
| `storage.com_act.sdaf002` | `slc` | stock | `giovanni-seguros`, `tapp-saldo-medio-territorio` |
| `storage.com_act.sdas001` | `slc` | stock | `cartera-sin-asignar`, `saldo-medio-vigente`, `tapp-saldo-medio-territorio` |
| `storage.com_act.sdas005` | `slc` | stock | `cmg-castigos` |
| `storage.com_act.wcdce001` | `slc` | historica | `contratacion-electronica` |
| `storage.com_act.wcdce002` | `slc` | historica | `contratacion-electronica` |
| `storage.com_act.wjas001` | `slc` | historica | `saldo-medio-vigente` |
| `storage.com_pas.hcdp001` | `slc` | historica | `michael-captaciones` |
| `storage.com_pas.pslwcap001` | `slc` | otro | `michael-captaciones` |
| `storage.com_pas.retp001` | `slc` | referencia | `giovanni-captaciones`, `michael-captaciones` |
| `storage.com_pas.sdps010` | `slc` | stock | `giovanni-captaciones` |
| `storage.com_pas.sdps013` | `slc` | stock | `giovanni-captaciones` |
| `storage.com_pas.wcap001` | `slc` | historica | `michael-captaciones` |
| `storage.com_pas.wjas004` | `slc` | historica | `giovanni-captaciones` |
| `storage.com_pas.wjas008` | `slc` | historica | `fondeo-estable` |
| `storage.com_seg.sdsf001` | `slc` | stock | `giovanni-seguros` |
| `storage.gpr.vpph001` | `slc` | otro | `desembolsos-por-canal`, `michael-castigos` |
| `storage.ref.fjercor01` | `slc` | otro | `michael-castigos` |
| `storage.ref.fjercor02` | `slc` | otro | `cartera-sin-asignar`, `desembolsos-por-canal`, `giovanni-cartera-agro`, `tapp-saldo-medio-territorio` |
| `storage.ref.rcalen001` | `slc` | referencia | `clientes-rurales-migrantes`, `cmg-castigos`, `saca-tu-garra`, `tapp-saldo-medio-territorio` |
| `storage.ref.rtcm001` | `slc` | referencia | `desembolsos-por-canal`, `michael-castigos` |
| `storage.ref.vjercor03` | `slc` | otro | `cartera-sin-asignar` |
| `storage.ref.vjercor04` | `slc` | otro | `fondeo-estable`, `giovanni-captaciones`, `michael-captaciones` |
| `storage.ref.vurbrur01` | `slc` | otro | `clientes-rurales-migrantes` |
| `storage.ref.wjercor03` | `slc` | otro | `giovanni-cartera-agro`, `giovanni-seguros` |
| `storage.util.fvecfec01` | `slc` | otro | `tapp-saldo-medio-territorio` |
