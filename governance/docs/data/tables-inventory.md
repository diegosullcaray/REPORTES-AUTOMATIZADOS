# Inventario de tablas

> **Generado** desde `src/reportes/tablas.py` por `governance/scripts/generar_inventario.py`. No editar a mano; para cambiar algo edita `tablas.py` y regenera.

Sirve para el cierre de mes: saber **qué tablas necesita cada reporte** y **a qué reportes afecta una tabla** antes de pedir a Producción que la actualice. Proceso: [cierre de mes](../development/runbooks/proceso-cierre-de-mes.md).

- Tablas registradas: **84** · Reportes con tablas: **22**
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
| `storage.com_act.hcda001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.sdas001` | `mish` | stock | `sfecpro` | confirmada |
| `storage.ref.fjercor02` | `mish` | otro | — | por_confirmar |
| `storage.ref.vjercor03` | `mish` | otro | — | por_confirmar |

### `clientes-extranjeros` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `intcom.dbo.ccd` | `slc` | stock | `Fecha_Cierre` | confirmada |
| `intcom.dbo.ccs_fund_f` | `slc` | stock | `fecha_reporte` | confirmada |
| `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}` | `slc` | dinamica | — | por_confirmar |
| `db{yyyymm}.dbo.ccp{yyyymmdd}` | `rcc` | dinamica | — | por_confirmar |

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
| `storage.com_act.hbcn001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcda001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr002` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.rfoc001` | `mish` | referencia | — | por_confirmar |
| `storage.ref.rcalen001` | `mish` | referencia | — | por_confirmar |
| `storage.ref.vurbrur01` | `mish` | otro | — | por_confirmar |

### `cmg-castigos` (diaria)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.sdas005` | `mish` | stock | `SFECPRO` | convencion |
| `storage.ref.rcalen001` | `mish` | referencia | — | por_confirmar |

### `cmg-mora` (diaria)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `rcc` | stock | `FC_DIA` | confirmada |
| `dbriesgos.dbo.prov_proy_{yyyymmdd}_0` | `rcc` | dinamica | — | por_confirmar |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `rcc` | stock | `FECHA_CIERRE` | confirmada |
| `dw_raw_v2.dbo.cmgmora_recaudo` | `rcc` | staging | — | por_confirmar |
| `dw_raw_v2.dbo.cmgmora_strjercor` | `rcc` | otro | — | por_confirmar |
| `storage.com_act.sbtvrie001` | `mish` | destino | — | por_confirmar |

### `contratacion-electronica` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.wcdce001` | `mish` | historica | `hfecpro` | confirmada |
| `storage.com_act.wcdce002` | `mish` | historica | `hfecpro` | confirmada |

### `desembolsos-por-canal` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcdr002` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hdce001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hmcm001` | `mish` | historica | `HFECPRO` | convencion |
| `storage.com_act.rfoc001` | `mish` | referencia | — | por_confirmar |
| `storage.gpr.vpph001` | `mish` | otro | — | por_confirmar |
| `storage.ref.fjercor02` | `mish` | otro | — | por_confirmar |
| `storage.ref.rtcm001` | `mish` | referencia | — | por_confirmar |

### `fondeo-estable` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_pas.wjas008` | `mish` | historica | `hfecpro` | confirmada |
| `storage.ref.vjercor04` | `mish` | otro | — | por_confirmar |

### `giovanni-captaciones` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_pas.retp001` | `mish` | referencia | — | por_confirmar |
| `storage.com_pas.sdps010` | `mish` | stock | `SFECPRO` | convencion |
| `storage.com_pas.sdps013` | `mish` | stock | `SFECPRO` | confirmada |
| `storage.com_pas.wjas004` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.ref.vjercor04` | `mish` | otro | — | por_confirmar |

### `giovanni-cartera-agro` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcda001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `mish` | referencia | — | por_confirmar |
| `storage.ref.fjercor02` | `mish` | otro | — | por_confirmar |
| `storage.ref.wjercor03` | `mish` | otro | — | por_confirmar |

### `giovanni-seguros` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com.vdmcom01` | `mish` | otro | — | por_confirmar |
| `storage.com_act.retp001` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.sdaf002` | `mish` | stock | `SFECPRO` | convencion |
| `storage.com_seg.sdsf001` | `mish` | stock | `SFECPRO` | convencion |
| `storage.ref.wjercor03` | `mish` | otro | — | por_confirmar |

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
| `storage.com_pas.hcdp001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_pas.pslwcap001` | `mish` | otro | — | por_confirmar |
| `storage.com_pas.retp001` | `mish` | referencia | — | por_confirmar |
| `storage.com_pas.wcap001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.ref.vjercor04` | `mish` | otro | — | por_confirmar |

### `michael-castigos` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.hcca001` | `mish` | historica | `HFECPRO` | convencion |
| `storage.com_act.hcda001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp002` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.retp003` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.rfoc001` | `mish` | referencia | — | por_confirmar |
| `storage.gpr.vpph001` | `mish` | otro | — | por_confirmar |
| `storage.ref.fjercor01` | `mish` | otro | — | por_confirmar |
| `storage.ref.rtcm001` | `mish` | referencia | — | por_confirmar |

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
| `storage.com_act.hcda001` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.hcma001` | `mish` | historica | `HFECPRO` | convencion |
| `storage.com_act.hctc001` | `mish` | historica | `HFECPRO` | convencion |
| `storage.com_act.sdae002` | `mish` | stock | `sfecpro` | confirmada |
| `storage.com_act.sdae003` | `mish` | stock | `SFECPRO` | convencion |
| `storage.ref.rcalen001` | `mish` | referencia | — | por_confirmar |

### `saldo-medio-vigente` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `storage.com_act.sdas001` | `mish` | stock | `sfecpro` | confirmada |
| `storage.com_act.wjas001` | `mish` | historica | `HFECPRO` | confirmada |

### `tapp-saldo-medio-territorio` (mensual)

| Tabla | Conexión | Tipo | Columna de fecha | Confianza |
|---|---|---|---|---|
| `appj.dbo.salmediovigente1` | `mish` | historica | `HFECPRO` | confirmada |
| `storage.com_act.retp001` | `mish` | referencia | — | por_confirmar |
| `storage.com_act.sdaf002` | `mish` | stock | `SFECPRO` | convencion |
| `storage.com_act.sdas001` | `mish` | stock | `sfecpro` | confirmada |
| `storage.ref.fjercor02` | `mish` | otro | — | por_confirmar |
| `storage.ref.rcalen001` | `mish` | referencia | — | por_confirmar |
| `storage.util.fvecfec01` | `mish` | otro | — | por_confirmar |

## 2. Por tabla (si se actualiza esta, ¿a qué reportes afecta?)

| Tabla | Conexión | Tipo | Reportes |
|---|---|---|---|
| `appj.dbo.salmediovigente1` | `mish` | historica | `tapp-saldo-medio-territorio` |
| `csd.dbo.clientes_ds` | `slc` | stock | `bancarizados-producto`, `clientes-jovenes`, `indicadores-clientes` |
| `dbrcc.dbo.rcccab{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `dbrcc.dbo.rccdet{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `rcc` | stock | `cmg-mora` |
| `dbriesgos.dbo.prov_proy_{yyyymmdd}_0` | `rcc` | dinamica | `cmg-mora` |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `rcc` | stock | `cmg-mora` |
| `db{yyyymm}.dbo.ccd{yyyymmdd}` | `rcc` | dinamica | `bancarizados` |
| `db{yyyymm}.dbo.ccp{yyyymmdd}` | `rcc` | dinamica | `clientes-extranjeros` |
| `dma.dbo.fecciebt` | `slc` | otro | `heredados-pdm` |
| `dma.dbo.hiscreditos` | `slc` | historica | `heredados-pdm` |
| `dma.dbo.hisgrupospdm` | `slc` | historica | `heredados-pdm` |
| `dma.dbo.mrvgrupopdm` | `slc` | otro | `heredados-pdm` |
| `dw_metadata.dbo.wjercor03` | `rcc` | otro | `bancarizados` |
| `dw_raw.dbo.clientes` | `rcc` | otro | `bancarizados` |
| `dw_raw_v2.dbo.cmgmora_recaudo` | `rcc` | staging | `cmg-mora` |
| `dw_raw_v2.dbo.cmgmora_strjercor` | `rcc` | otro | `cmg-mora` |
| `dwh.dbo.bregmod001` | `slc` | referencia | `bancarizados-producto`, `heredados-pdm`, `productos-verdes` |
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
| `dwh.dbo.scarcap003` | `slc` | stock | `indicadores-clientes` |
| `dwh.dbo.scarcre002` | `slc` | stock | `productos-verdes` |
| `dwh.dbo.scarcre006` | `slc` | stock | `clientes-jovenes` |
| `dwh.dbo.vplaper001` | `slc` | otro | `productos-verdes` |
| `intcom.bt.fsd002` | `slc` | otro | `indicadores-clientes` |
| `intcom.bt.sngc13` | `slc` | stock | `indicadores-clientes` |
| `intcom.dbo.an_productos` | `slc` | otro | `bancarizados` |
| `intcom.dbo.ccd` | `slc` | stock | `bancarizados`, `clientes-extranjeros`, `indicadores-clientes` |
| `intcom.dbo.ccs_fund_f` | `slc` | stock | `clientes-extranjeros`, `indicadores-clientes` |
| `intcom.dbo.distritos_rural_alv` | `slc` | otro | `indicadores-clientes` |
| `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}` | `slc` | dinamica | `clientes-extranjeros` |
| `slc.dbo.retp006` | `slc` | referencia | `productos-verdes` |
| `storage.com.vdmcom01` | `mish` | otro | `giovanni-seguros` |
| `storage.com_act.hbcn001` | `mish` | historica | `clientes-rurales-migrantes` |
| `storage.com_act.hcca001` | `mish` | historica | `michael-castigos` |
| `storage.com_act.hcda001` | `mish` | historica | `cartera-sin-asignar`, `clientes-rurales-migrantes`, `desembolsos-por-canal`, `giovanni-cartera-agro`, `michael-castigos`, `saca-tu-garra` |
| `storage.com_act.hcdr001` | `mish` | historica | `clientes-rurales-migrantes`, `desembolsos-por-canal` |
| `storage.com_act.hcdr002` | `mish` | historica | `clientes-rurales-migrantes`, `desembolsos-por-canal` |
| `storage.com_act.hcma001` | `mish` | historica | `saca-tu-garra` |
| `storage.com_act.hctc001` | `mish` | historica | `saca-tu-garra` |
| `storage.com_act.hdce001` | `mish` | historica | `desembolsos-por-canal` |
| `storage.com_act.hmcm001` | `mish` | historica | `desembolsos-por-canal` |
| `storage.com_act.retp001` | `mish` | referencia | `cartera-sin-asignar`, `giovanni-cartera-agro`, `giovanni-seguros`, `michael-castigos`, `tapp-saldo-medio-territorio` |
| `storage.com_act.retp002` | `mish` | referencia | `cartera-sin-asignar`, `giovanni-cartera-agro`, `giovanni-seguros`, `michael-castigos` |
| `storage.com_act.retp003` | `mish` | referencia | `cartera-sin-asignar`, `giovanni-cartera-agro`, `giovanni-seguros`, `michael-castigos` |
| `storage.com_act.rfoc001` | `mish` | referencia | `clientes-rurales-migrantes`, `desembolsos-por-canal`, `michael-castigos` |
| `storage.com_act.sbtvrie001` | `mish` | destino | `cmg-mora` |
| `storage.com_act.sdae002` | `mish` | stock | `saca-tu-garra` |
| `storage.com_act.sdae003` | `mish` | stock | `saca-tu-garra` |
| `storage.com_act.sdaf002` | `mish` | stock | `giovanni-seguros`, `tapp-saldo-medio-territorio` |
| `storage.com_act.sdas001` | `mish` | stock | `cartera-sin-asignar`, `saldo-medio-vigente`, `tapp-saldo-medio-territorio` |
| `storage.com_act.sdas005` | `mish` | stock | `cmg-castigos` |
| `storage.com_act.wcdce001` | `mish` | historica | `contratacion-electronica` |
| `storage.com_act.wcdce002` | `mish` | historica | `contratacion-electronica` |
| `storage.com_act.wjas001` | `mish` | historica | `saldo-medio-vigente` |
| `storage.com_pas.hcdp001` | `mish` | historica | `michael-captaciones` |
| `storage.com_pas.pslwcap001` | `mish` | otro | `michael-captaciones` |
| `storage.com_pas.retp001` | `mish` | referencia | `giovanni-captaciones`, `michael-captaciones` |
| `storage.com_pas.sdps010` | `mish` | stock | `giovanni-captaciones` |
| `storage.com_pas.sdps013` | `mish` | stock | `giovanni-captaciones` |
| `storage.com_pas.wcap001` | `mish` | historica | `michael-captaciones` |
| `storage.com_pas.wjas004` | `mish` | historica | `giovanni-captaciones` |
| `storage.com_pas.wjas008` | `mish` | historica | `fondeo-estable` |
| `storage.com_seg.sdsf001` | `mish` | stock | `giovanni-seguros` |
| `storage.gpr.vpph001` | `mish` | otro | `desembolsos-por-canal`, `michael-castigos` |
| `storage.ref.fjercor01` | `mish` | otro | `michael-castigos` |
| `storage.ref.fjercor02` | `mish` | otro | `cartera-sin-asignar`, `desembolsos-por-canal`, `giovanni-cartera-agro`, `tapp-saldo-medio-territorio` |
| `storage.ref.rcalen001` | `mish` | referencia | `clientes-rurales-migrantes`, `cmg-castigos`, `saca-tu-garra`, `tapp-saldo-medio-territorio` |
| `storage.ref.rtcm001` | `mish` | referencia | `desembolsos-por-canal`, `michael-castigos` |
| `storage.ref.vjercor03` | `mish` | otro | `cartera-sin-asignar` |
| `storage.ref.vjercor04` | `mish` | otro | `fondeo-estable`, `giovanni-captaciones`, `michael-captaciones` |
| `storage.ref.vurbrur01` | `mish` | otro | `clientes-rurales-migrantes` |
| `storage.ref.wjercor03` | `mish` | otro | `giovanni-cartera-agro`, `giovanni-seguros` |
| `storage.util.fvecfec01` | `mish` | otro | `tapp-saldo-medio-territorio` |
