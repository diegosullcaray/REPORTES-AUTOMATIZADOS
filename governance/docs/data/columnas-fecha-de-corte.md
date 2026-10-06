# Columnas que controlan la fecha de corte

> **Generado** desde `src/reportes/tablas.py` y `src/reportes/reglas_fecha.py` (leyendo el SQL de cada reporte). No editar a mano; CSV para Producción: `python main.py columnas-fecha --csv columnas.csv`.

Para **Producción**: al cargar el cierre, la columna de la tabla indicada debe quedar con la **fecha de corte**; los reportes validan y filtran por ella. Notación: D = corte diario · F = corte mensual (fin de mes) · «cierre hábil» = `RCIEBT = 1` en `storage.ref.rcalen001`.

## 1. Por tabla (qué columna debe llevar la fecha del cierre)

| Tabla | Conexión | Columna de fecha | Reportes que la usan |
|---|---|---|---|
| `appj.dbo.salmediovigente1` | `mish` | `hfecpro` | `tapp-saldo-medio-territorio` |
| `csd.dbo.clientes_ds` | `slc` | `HFECPRO` | `bancarizados-producto`, `clientes-jovenes`, `indicadores-clientes` |
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `rcc` | `FC_DIA` | `cmg-mora` |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `rcc` | `FECHA_CIERRE` | `cmg-mora` |
| `dma.dbo.fecciebt` | `slc` | `RFCIEBT` | `heredados-pdm` |
| `dma.dbo.hiscreditos` | `slc` | `HFECPRO` | `heredados-pdm` |
| `dma.dbo.hisgrupospdm` | `slc` | `HFECPRO` | `heredados-pdm` |
| `dw_metadata.dbo.wjercor03` | `rcc` | `RFECPRO` | `bancarizados` |
| `dw_raw.dbo.clientes` | `rcc` | `HFECPRO` | `bancarizados` |
| `dwh.dbo.hcarcap001` | `slc` | `HFECPRO` | `indicadores-clientes` |
| `dwh.dbo.hcarcre001` | `slc` | `HFECPRO` | `clientes-jovenes`, `productos-verdes` |
| `dwh.dbo.rfecsis001` | `slc` | `RFEC` | `productos-verdes` |
| `intcom.dbo.ccd` | `slc` | `Fecha_Cierre` | `bancarizados`, `clientes-extranjeros`, `indicadores-clientes` |
| `intcom.dbo.ccs_fund_f` | `slc` | `fecha_reporte` | `clientes-extranjeros`, `indicadores-clientes` |
| `storage.com.vdmcom01` | `mish` | `HFECPRO` | `giovanni-seguros` |
| `storage.com_act.hbcn001` | `mish` | `HFECPRO` | `clientes-rurales-migrantes` |
| `storage.com_act.hcca001` | `mish` | `HFECPRO` | `michael-castigos` |
| `storage.com_act.hcda001` | `mish` | `HFECPRO` | `cartera-sin-asignar`, `clientes-rurales-migrantes`, `desembolsos-por-canal`, `giovanni-cartera-agro`, `michael-castigos`, `saca-tu-garra` |
| `storage.com_act.hcdr001` | `mish` | `HFECPRO` | `clientes-rurales-migrantes`, `desembolsos-por-canal` |
| `storage.com_act.hcdr002` | `mish` | `HFECPRO` | `clientes-rurales-migrantes`, `desembolsos-por-canal` |
| `storage.com_act.hcma001` | `mish` | `HFECPRO` | `saca-tu-garra` |
| `storage.com_act.hctc001` | `mish` | `HFECPRO` | `saca-tu-garra` |
| `storage.com_act.hdce001` | `mish` | `HFECPRO` | `desembolsos-por-canal` |
| `storage.com_act.hmcm001` | `mish` | `HFECPRO` | `desembolsos-por-canal` |
| `storage.com_act.sdae002` | `mish` | `SFECPRO` | `saca-tu-garra` |
| `storage.com_act.sdae003` | `mish` | `SFECPRO` | `saca-tu-garra` |
| `storage.com_act.sdaf002` | `mish` | `SFECPRO` | `giovanni-seguros`, `tapp-saldo-medio-territorio` |
| `storage.com_act.sdas001` | `mish` | `sfecpro` | `cartera-sin-asignar`, `saldo-medio-vigente`, `tapp-saldo-medio-territorio` |
| `storage.com_act.sdas005` | `mish` | `SFECPRO` | `cmg-castigos` |
| `storage.com_act.wcdce001` | `mish` | `hfecpro` | `contratacion-electronica` |
| `storage.com_act.wcdce002` | `mish` | `hfecpro` | `contratacion-electronica` |
| `storage.com_act.wjas001` | `mish` | `HFECPRO` | `saldo-medio-vigente` |
| `storage.com_pas.hcdp001` | `mish` | `HFECPRO` | `michael-captaciones` |
| `storage.com_pas.sdps013` | `mish` | `SFECPRO` | `giovanni-captaciones` |
| `storage.com_pas.wjas004` | `mish` | `HFECPRO` | `giovanni-captaciones` |
| `storage.com_pas.wjas008` | `mish` | `hfecpro` | `fondeo-estable` |
| `storage.com_seg.sdsf001` | `mish` | `SFECPRO` | `giovanni-seguros` |
| `storage.ref.rcalen001` | `mish` | `RFEC` | `clientes-rurales-migrantes`, `cmg-castigos`, `saca-tu-garra`, `tapp-saldo-medio-territorio` |
| `storage.ref.rtcm001` | `mish` | `RFECCIE` | `desembolsos-por-canal`, `michael-castigos` |
| `storage.ref.wjercor03` | `mish` | `RFECPRO` | `giovanni-cartera-agro`, `giovanni-seguros` |

Sin columna de fecha de corte (41: catálogos, funciones o tablas que genera el reporte): `dbrcc.dbo.rcccab{yyyymmdd}`, `dbrcc.dbo.rccdet{yyyymmdd}`, `dbriesgos.dbo.prov_proy_{yyyymmdd}_0`, `db{yyyymm}.dbo.ccd{yyyymmdd}`, `db{yyyymm}.dbo.ccp{yyyymmdd}`, `dma.dbo.mrvgrupopdm`, `dw_raw_v2.dbo.cmgmora_recaudo`, `dw_raw_v2.dbo.cmgmora_strjercor`, `dwh.dbo.bregmod001`, `dwh.dbo.bregper001`, `dwh.dbo.bregubt001`, `dwh.dbo.gdesemcre001`, `dwh.dbo.gjerreg001`, `dwh.dbo.rregope001`, `dwh.dbo.rtipcre001`, `dwh.dbo.rtipcre002`, `dwh.dbo.rtipcre003`, `dwh.dbo.scarcap001`, `dwh.dbo.scarcap003`, `dwh.dbo.scarcre002`, `dwh.dbo.scarcre006`, `dwh.dbo.vplaper001`, `intcom.bt.fsd002`, `intcom.bt.sngc13`, `intcom.dbo.an_productos`, `intcom.dbo.distritos_rural_alv`, `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}`, `slc.dbo.retp006`, `storage.com_act.retp001`, `storage.com_act.retp002`, `storage.com_act.retp003`, `storage.com_act.rfoc001`, `storage.com_act.sbtvrie001`, `storage.com_pas.retp001`, `storage.gpr.vpph001`, `storage.ref.fjercor01`, `storage.ref.fjercor02`, `storage.ref.vjercor03`, `storage.ref.vjercor04`, `storage.ref.vurbrur01`, `storage.util.fvecfec01`

## 2. Por reporte (condición exacta)

### Diarias 02 · `cartera-sin-asignar`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.hcda001` | `HFECPRO` | HFECPRO = D |
| `storage.com_act.retp001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp003` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.sdas001` | `sfecpro` | SFECPRO = D |
| `storage.ref.fjercor02` | — | función: la fecha de corte entra como parámetro: FJERCOR02(D) |
| `storage.ref.vjercor03` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Diarias 04.1 · `cmg-mora`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `dbriesgos.dbo.gasto_prov_ope_diaria` | `FC_DIA` | FC_DIA = D |
| `dbriesgos.dbo.prov_proy_{yyyymmdd}_0` | — | la tabla del día debe existir: PROV_PROY_<AAAAMMDD de D>_0 |
| `dbriesgos.dbo.recaudo_diario_finanzas` | `FECHA_CIERRE` | FECHA_CIERRE = D |
| `dw_raw_v2.dbo.cmgmora_recaudo` | — | staging: el reporte la trunca y la llena; no la carga Producción |
| `dw_raw_v2.dbo.cmgmora_strjercor` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.sbtvrie001` | — | destino de los INSERT que genera el reporte; no se consulta |

### Diarias 04.2 · `cmg-castigos`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.sdas005` | `SFECPRO` | SFECPRO IN (los 11 últimos cierres hábiles hasta D) con SCODAGR = 1 |
| `storage.ref.rcalen001` | `RFEC` | RFEC con RCIEBT = 1 hasta D (define los 11 últimos cierres hábiles) |

### Piero 01 · `desembolsos-por-canal`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.hcda001` | `HFECPRO` | HFECPRO = F |
| `storage.com_act.hcdr001` | `HFECPRO` | HFECPRO = F |
| `storage.com_act.hcdr002` | `HFECPRO` | HFECPRO = F |
| `storage.com_act.hdce001` | `HFECPRO` | HFECPRO = F (se une con HCDA001 por HFECPRO y HCODOPE) |
| `storage.com_act.hmcm001` | `HFECPRO` | HFECPRO = EOMONTH(F) |
| `storage.com_act.rfoc001` | — | sin fecha de corte: ROPEFEC es la fecha de la operación, no el corte |
| `storage.gpr.vpph001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.ref.fjercor02` | — | función: la fecha de corte entra como parámetro: FJERCOR02(F) |
| `storage.ref.rtcm001` | `RFECCIE` | RFECCIE <= F (último tipo de cambio hasta F) |

### Piero 02 · `fondeo-estable`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_pas.wjas008` | `hfecpro` | hfecpro = F (con HTIPCOD = 4) |
| `storage.ref.vjercor04` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Piero 03 · `heredados-pdm`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `dma.dbo.fecciebt` | `RFCIEBT` | RFCIEBT = F (fecha de cierre) |
| `dma.dbo.hiscreditos` | `HFECPRO` | HFECPRO IN (cierre F, de FecCieBt) |
| `dma.dbo.hisgrupospdm` | `HFECPRO` | HFECPRO = fecha del crédito (cierre F) |
| `dma.dbo.mrvgrupopdm` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.bregmod001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.bregubt001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rregope001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rtipcre001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rtipcre002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rtipcre003` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Piero 04.1 · `contratacion-electronica`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.wcdce001` | `hfecpro` | hfecpro = F |
| `storage.com_act.wcdce002` | `hfecpro` | hfecpro = F |

### Piero 04.2 · `clientes-rurales-migrantes`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.hbcn001` | `HFECPRO` | HFECPRO = cierre de mes (RCIEMES) de los últimos 3 meses |
| `storage.com_act.hcda001` | `HFECPRO` | HFECPRO = cierre hábil (RCIEBT) de cada uno de los últimos 3 meses |
| `storage.com_act.hcdr001` | `HFECPRO` | HFECPRO = cierre hábil (RCIEBT) del mes |
| `storage.com_act.hcdr002` | `HFECPRO` | HFECPRO = cierre hábil (RCIEBT) del mes |
| `storage.com_act.rfoc001` | — | sin fecha de corte: ROPEFEC es la fecha de la operación, no el corte |
| `storage.ref.rcalen001` | `RFEC` | RFEC entre F-3 meses y F con RCIEMES = 1 (cierres de mes) y RCIEBT = 1 (cierre hábil) |
| `storage.ref.vurbrur01` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Piero 05.1 · `giovanni-captaciones`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_pas.retp001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_pas.sdps013` | `SFECPRO` | SFECPRO = F (con SCODAGR = 8) |
| `storage.com_pas.wjas004` | `HFECPRO` | HFECPRO = F |
| `storage.ref.vjercor04` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Piero 05.2 · `giovanni-seguros`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com.vdmcom01` | `HFECPRO` | HFECPRO = EOMONTH(F) (con HCODVAR de metas) |
| `storage.com_act.retp001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp003` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.sdaf002` | `SFECPRO` | SFECPRO = F (con SCODAGR = 6) |
| `storage.com_seg.sdsf001` | `SFECPRO` | SFECPRO = F (con SCODAGR = 13) |
| `storage.ref.wjercor03` | `RFECPRO` | RFECPRO = F con RINDFEC = 'ACTUAL' |

### Piero 05.3 · `giovanni-cartera-agro`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.hcda001` | `HFECPRO` | HFECPRO = F y HFECPRO = fin de mes anterior (dos cierres) |
| `storage.com_act.retp001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp003` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.ref.fjercor02` | — | función: la fecha de corte entra como parámetro: FJERCOR02(fin de mes anterior) |
| `storage.ref.wjercor03` | `RFECPRO` | RFECPRO = F con RINDFEC = 'actual' |

### Piero 06 · `saca-tu-garra`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.hcda001` | `HFECPRO` | HFECPRO IN (los 2 últimos cierres hábiles hasta F) |
| `storage.com_act.hcma001` | `HFECPRO` | HFECPRO = último cierre hábil hasta F |
| `storage.com_act.hctc001` | `HFECPRO` | HFECPRO = último cierre hábil hasta F |
| `storage.com_act.sdae002` | `SFECPRO` | SFECPRO = último cierre hábil hasta F (SCODAGR = 3) |
| `storage.com_act.sdae003` | `SFECPRO` | SFECPRO = último cierre hábil hasta F (SCODAGR = 3) |
| `storage.ref.rcalen001` | `RFEC` | RFEC <= F con RCIEBT = 1: los 2 últimos cierres hábiles |

### Piero 07 · `saldo-medio-vigente`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.sdas001` | `sfecpro` | SFECPRO entre el primer día del mes y F (con SCODAGR = 1): todos los días del mes |
| `storage.com_act.wjas001` | `HFECPRO` | HFECPRO = F (con HTIPCOD = 7) |

### Piero 08 · `tapp-saldo-medio-territorio`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `appj.dbo.salmediovigente1` | `hfecpro` | staging: la crea y llena el reporte (HFECPRO); no la carga Producción |
| `storage.com_act.retp001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.sdaf002` | `SFECPRO` | SFECPRO = cada fecha del periodo |
| `storage.com_act.sdas001` | `sfecpro` | SFECPRO = cada fecha del periodo (con SCODAGR = 6) |
| `storage.ref.fjercor02` | — | función: la fecha de corte entra como parámetro: FJERCOR02(lista de fechas del periodo) |
| `storage.ref.rcalen001` | `RFEC` | RFEC entre fin de mes anterior y F con RCIEBT = 1 |
| `storage.util.fvecfec01` | — | función: la fecha de corte entra como parámetro: FVECFEC01(fecha, 'ini-hoy|cal') |

### Piero 09.1 · `michael-captaciones`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_pas.hcdp001` | `HFECPRO` | HFECPRO = F |
| `storage.com_pas.retp001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.ref.vjercor04` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Piero 09.2 · `michael-castigos`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `storage.com_act.hcca001` | `HFECPRO` | HFECPRO = F |
| `storage.com_act.hcda001` | `HFECPRO` | HFECPRO = fin de mes anterior |
| `storage.com_act.retp001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.retp003` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.com_act.rfoc001` | — | sin fecha de corte: ROPEFEC es la fecha de la operación, no el corte |
| `storage.gpr.vpph001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `storage.ref.fjercor01` | — | función: la fecha de corte entra como parámetro: FJERCOR01(F) |
| `storage.ref.rtcm001` | `RFECCIE` | RFECCIE en el mes del fin de mes anterior (tipo de cambio) |

### Erick 01 · `productos-verdes`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `dwh.dbo.bregmod001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.bregper001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.bregubt001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.gdesemcre001` | — | procedimiento: la fecha entra como parámetro (@fecs = F) |
| `dwh.dbo.gjerreg001` | — | procedimiento: la fecha entra como parámetro (@fecs = F) |
| `dwh.dbo.hcarcre001` | `HFECPRO` | HFECPRO = F (solo si F es cierre hábil) |
| `dwh.dbo.rfecsis001` | `RFEC` | RFEC = F con RCIEBT = 1 (F debe estar marcado como cierre hábil) |
| `dwh.dbo.rtipcre001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rtipcre002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rtipcre003` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.scarcre002` | — | sin fecha de corte: se une por clave (SIDS) a la tabla H* del mismo reporte |
| `dwh.dbo.vplaper001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `slc.dbo.retp006` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Erick 02 · `clientes-jovenes`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `csd.dbo.clientes_ds` | `HFECPRO` | HFECPRO = fecha de los desembolsos (se une por HCTACLI y HFECPRO) |
| `dwh.dbo.bregper001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.gdesemcre001` | — | procedimiento: la fecha entra como parámetro (@fecs = F) |
| `dwh.dbo.hcarcre001` | `HFECPRO` | HFECPRO = F |
| `dwh.dbo.scarcre006` | — | sin fecha de corte: se une por clave (SIDS) a la tabla H* del mismo reporte |

### Erick 03.1 · `bancarizados`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `dbrcc.dbo.rcccab{yyyymmdd}` | — | tabla del cierre: RCCCAB + AAAAMMDD de F |
| `dbrcc.dbo.rccdet{yyyymmdd}` | — | tabla del cierre: RCCDET + AAAAMMDD de F (columna FECHA) |
| `db{yyyymm}.dbo.ccd{yyyymmdd}` | — | tabla del cierre en la base DB<AAAAMM>: CCD + AAAAMMDD de F; FECHA_CIERRE dentro del mes de F |
| `dw_metadata.dbo.wjercor03` | `RFECPRO` | RFECPRO dentro del mes de F |
| `dw_raw.dbo.clientes` | `HFECPRO` | HFECPRO < primer día del mes de F (para marcar Stock vs Nuevo) |
| `intcom.dbo.an_productos` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `intcom.dbo.ccd` | `Fecha_Cierre` | FECHA_CIERRE dentro del mes de F |

### Erick 03.2 · `bancarizados-producto`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `csd.dbo.clientes_ds` | `HFECPRO` | HFECPRO = último cierre cargado del mes de F (se detecta solo) |
| `dwh.dbo.bregmod001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.gdesemcre001` | — | procedimiento: la fecha entra como parámetro (el mismo cierre detectado) |
| `dwh.dbo.rtipcre001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rtipcre002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.rtipcre003` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

### Erick 03.3 · `clientes-extranjeros`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `intcom.dbo.ccd` | `Fecha_Cierre` | Fecha_Cierre = F |
| `intcom.dbo.ccs_fund_f` | `fecha_reporte` | fecha_reporte dentro del mes de F (seguros; puede usar otro corte con --fecha-seguros) |
| `rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}` | — | tabla del cierre: CCP + AAAAMMDD de F en la base DB<AAAAMM> (vía linked server, ruta por defecto) |
| `db{yyyymm}.dbo.ccp{yyyymmdd}` | — | tabla del cierre: CCP + AAAAMMDD de F en DB<AAAAMM> (ruta directa, --pasivos-directo) |

### Erick 03.4 · `indicadores-clientes`

| Tabla | Columna | Condición que aplica el reporte |
|---|---|---|
| `csd.dbo.clientes_ds` | `HFECPRO` | HFECPRO = último cierre cargado del mes anterior (desfase 1) |
| `dwh.dbo.bregper001` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `dwh.dbo.hcarcap001` | `HFECPRO` | HFECPRO = último cierre cargado del mes |
| `dwh.dbo.scarcap001` | — | sin fecha de corte: se une por clave (SIDS) a la tabla H* del mismo reporte |
| `dwh.dbo.scarcap003` | — | sin fecha de corte: se une por clave (SIDS) a la tabla H* del mismo reporte |
| `intcom.bt.fsd002` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `intcom.bt.sngc13` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |
| `intcom.dbo.ccd` | `Fecha_Cierre` | Fecha_Cierre = último cierre cargado del mes |
| `intcom.dbo.ccs_fund_f` | `fecha_reporte` | fecha_reporte = último cierre cargado del mes anterior (desfase 1) |
| `intcom.dbo.distritos_rural_alv` | — | sin fecha de corte: catálogo; el reporte no lo filtra por fecha |

