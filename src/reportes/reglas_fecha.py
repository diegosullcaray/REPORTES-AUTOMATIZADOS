"""Cómo usa cada reporte la fecha de corte en cada tabla: qué columna se compara y con qué condición.

Es la fuente de la guía para Producción (`governance/docs/data/columnas-fecha-de-corte.md`), de `python main.py columnas-fecha`
y del mensaje de `solicitud-actualizacion`. Se obtuvo leyendo el SQL de cada reporte (no es una suposición por el nombre).

Notación: D = fecha de corte de un reporte diario · F = fecha de corte de un reporte mensual (fin de mes) ·
«cierre hábil» = día con RCIEBT=1 en el calendario `storage.ref.rcalen001`.
La columna de cada tabla está en `tablas.TABLAS[...].col_fecha`; aquí va la condición completa por reporte.
"""

from __future__ import annotations

SIN = "sin fecha de corte: catálogo; el reporte no lo filtra por fecha"
REL = "sin fecha de corte: se une por clave (SIDS) a la tabla H* del mismo reporte"
FN = "función: la fecha de corte entra como parámetro"

REGLAS: dict[str, dict[str, str]] = {
    "cartera-sin-asignar": {
        "storage.com_act.hcda001": "HFECPRO = D",
        "storage.com_act.sdas001": "SFECPRO = D",
        "storage.ref.fjercor02": f"{FN}: FJERCOR02(D)",
        "storage.ref.vjercor03": SIN, "storage.com_act.retp001": SIN, "storage.com_act.retp002": SIN, "storage.com_act.retp003": SIN,
    },
    "cmg-mora": {
        "dbriesgos.dbo.recaudo_diario_finanzas": "FECHA_CIERRE = D",
        "dbriesgos.dbo.gasto_prov_ope_diaria": "FC_DIA = D",
        "dbriesgos.dbo.prov_proy_{yyyymmdd}_0": "la tabla del día debe existir: PROV_PROY_<AAAAMMDD de D>_0",
        "dw_raw_v2.dbo.cmgmora_recaudo": "staging: el reporte la trunca y la llena; no la carga Producción",
        "dw_raw_v2.dbo.cmgmora_strjercor": SIN,
        "storage.com_act.sbtvrie001": "destino de los INSERT que genera el reporte; no se consulta",
    },
    "cmg-castigos": {
        "storage.com_act.sdas005": "SFECPRO IN (los 11 últimos cierres hábiles hasta D) con SCODAGR = 1",
        "storage.ref.rcalen001": "RFEC con RCIEBT = 1 hasta D (define los 11 últimos cierres hábiles)",
    },
    "desembolsos-por-canal": {
        "storage.com_act.hcda001": "HFECPRO = F",
        "storage.com_act.hmcm001": "HFECPRO = EOMONTH(F)",
        "storage.com_act.hcdr001": "HFECPRO = F", "storage.com_act.hcdr002": "HFECPRO = F",
        "storage.com_act.hdce001": "HFECPRO = F (se une con HCDA001 por HFECPRO y HCODOPE)",
        "storage.com_act.rfoc001": "sin fecha de corte: ROPEFEC es la fecha de la operación, no el corte",
        "storage.gpr.vpph001": SIN, "storage.ref.fjercor02": f"{FN}: FJERCOR02(F)",
        "storage.ref.rtcm001": "RFECCIE <= F (último tipo de cambio hasta F)",
    },
    "fondeo-estable": {
        "storage.com_pas.wjas008": "hfecpro = F (con HTIPCOD = 4)", "storage.ref.vjercor04": SIN,
    },
    "heredados-pdm": {
        "dma.dbo.fecciebt": "RFCIEBT = F (fecha de cierre)",
        "dma.dbo.hiscreditos": "HFECPRO IN (cierre F, de FecCieBt)",
        "dma.dbo.hisgrupospdm": "HFECPRO = fecha del crédito (cierre F)",
        "dma.dbo.mrvgrupopdm": SIN, "dwh.dbo.bregmod001": SIN, "dwh.dbo.bregubt001": SIN, "dwh.dbo.rregope001": SIN,
        "dwh.dbo.rtipcre001": SIN, "dwh.dbo.rtipcre002": SIN, "dwh.dbo.rtipcre003": SIN,
    },
    "contratacion-electronica": {
        "storage.com_act.wcdce001": "hfecpro = F", "storage.com_act.wcdce002": "hfecpro = F",
    },
    "clientes-rurales-migrantes": {
        "storage.ref.rcalen001": "RFEC entre F-3 meses y F con RCIEMES = 1 (cierres de mes) y RCIEBT = 1 (cierre hábil)",
        "storage.com_act.hbcn001": "HFECPRO = cierre de mes (RCIEMES) de los últimos 3 meses",
        "storage.com_act.hcda001": "HFECPRO = cierre hábil (RCIEBT) de cada uno de los últimos 3 meses",
        "storage.com_act.hcdr001": "HFECPRO = cierre hábil (RCIEBT) del mes", "storage.com_act.hcdr002": "HFECPRO = cierre hábil (RCIEBT) del mes",
        "storage.com_act.rfoc001": "sin fecha de corte: ROPEFEC es la fecha de la operación, no el corte", "storage.ref.vurbrur01": SIN,
    },
    "giovanni-captaciones": {
        "storage.com_pas.sdps013": "SFECPRO = F (con SCODAGR = 8)", "storage.com_pas.wjas004": "HFECPRO = F",
        "storage.com_pas.retp001": SIN, "storage.ref.vjercor04": SIN,
    },
    "giovanni-seguros": {
        "storage.com.vdmcom01": "HFECPRO = EOMONTH(F) (con HCODVAR de metas)",
        "storage.com_act.sdaf002": "SFECPRO = F (con SCODAGR = 6)",
        "storage.com_seg.sdsf001": "SFECPRO = F (con SCODAGR = 13)",
        "storage.ref.wjercor03": "RFECPRO = F con RINDFEC = 'ACTUAL'",
        "storage.com_act.retp001": SIN, "storage.com_act.retp002": SIN, "storage.com_act.retp003": SIN,
    },
    "giovanni-cartera-agro": {
        "storage.com_act.hcda001": "HFECPRO = F y HFECPRO = fin de mes anterior (dos cierres)",
        "storage.ref.wjercor03": "RFECPRO = F con RINDFEC = 'actual'",
        "storage.ref.fjercor02": f"{FN}: FJERCOR02(fin de mes anterior)",
        "storage.com_act.retp001": SIN, "storage.com_act.retp002": SIN, "storage.com_act.retp003": SIN,
    },
    "saca-tu-garra": {
        "storage.ref.rcalen001": "RFEC <= F con RCIEBT = 1: los 2 últimos cierres hábiles",
        "storage.com_act.hcda001": "HFECPRO IN (los 2 últimos cierres hábiles hasta F)",
        "storage.com_act.hcma001": "HFECPRO = último cierre hábil hasta F",
        "storage.com_act.hctc001": "HFECPRO = último cierre hábil hasta F",
        "storage.com_act.sdae002": "SFECPRO = último cierre hábil hasta F (SCODAGR = 3)",
        "storage.com_act.sdae003": "SFECPRO = último cierre hábil hasta F (SCODAGR = 3)",
    },
    "saldo-medio-vigente": {
        "storage.com_act.wjas001": "HFECPRO = F (con HTIPCOD = 7)",
        "storage.com_act.sdas001": "SFECPRO entre el primer día del mes y F (con SCODAGR = 1): todos los días del mes",
    },
    "tapp-saldo-medio-territorio": {
        "storage.ref.rcalen001": "RFEC entre fin de mes anterior y F con RCIEBT = 1",
        "storage.util.fvecfec01": f"{FN}: FVECFEC01(fecha, 'ini-hoy|cal')",
        "storage.ref.fjercor02": f"{FN}: FJERCOR02(lista de fechas del periodo)",
        "storage.com_act.sdas001": "SFECPRO = cada fecha del periodo (con SCODAGR = 6)",
        "storage.com_act.sdaf002": "SFECPRO = cada fecha del periodo",
        "storage.com_act.retp001": SIN,
        "appj.dbo.salmediovigente1": "staging: la crea y llena el reporte (HFECPRO); no la carga Producción",
    },
    "michael-captaciones": {
        "storage.com_pas.hcdp001": "HFECPRO = F", "storage.com_pas.retp001": SIN, "storage.ref.vjercor04": SIN,
    },
    "michael-castigos": {
        "storage.com_act.hcda001": "HFECPRO = fin de mes anterior",
        "storage.com_act.hcca001": "HFECPRO = F",
        "storage.ref.fjercor01": f"{FN}: FJERCOR01(F)",
        "storage.ref.rtcm001": "RFECCIE en el mes del fin de mes anterior (tipo de cambio)",
        "storage.com_act.retp001": SIN, "storage.com_act.retp002": SIN, "storage.com_act.retp003": SIN,
        "storage.com_act.rfoc001": "sin fecha de corte: ROPEFEC es la fecha de la operación, no el corte", "storage.gpr.vpph001": SIN,
    },
    "productos-verdes": {
        "dwh.dbo.gjerreg001": "procedimiento: la fecha entra como parámetro (@fecs = F)",
        "dwh.dbo.gdesemcre001": "procedimiento: la fecha entra como parámetro (@fecs = F)",
        "dwh.dbo.hcarcre001": "HFECPRO = F (solo si F es cierre hábil)",
        "dwh.dbo.rfecsis001": "RFEC = F con RCIEBT = 1 (F debe estar marcado como cierre hábil)",
        "dwh.dbo.scarcre002": REL, "dwh.dbo.bregmod001": SIN, "dwh.dbo.bregper001": SIN, "dwh.dbo.bregubt001": SIN,
        "dwh.dbo.rtipcre001": SIN, "dwh.dbo.rtipcre002": SIN, "dwh.dbo.rtipcre003": SIN, "dwh.dbo.vplaper001": SIN, "slc.dbo.retp006": SIN,
    },
    "clientes-jovenes": {
        "dwh.dbo.gdesemcre001": "procedimiento: la fecha entra como parámetro (@fecs = F)",
        "dwh.dbo.hcarcre001": "HFECPRO = F",
        "csd.dbo.clientes_ds": "HFECPRO = fecha de los desembolsos (se une por HCTACLI y HFECPRO)",
        "dwh.dbo.scarcre006": REL, "dwh.dbo.bregper001": SIN,
    },
    "bancarizados": {
        "dbrcc.dbo.rcccab{yyyymmdd}": "tabla del cierre: RCCCAB + AAAAMMDD de F",
        "dbrcc.dbo.rccdet{yyyymmdd}": "tabla del cierre: RCCDET + AAAAMMDD de F (columna FECHA)",
        "db{yyyymm}.dbo.ccd{yyyymmdd}": "tabla del cierre en la base DB<AAAAMM>: CCD + AAAAMMDD de F; FECHA_CIERRE dentro del mes de F",
        "dw_metadata.dbo.wjercor03": "RFECPRO dentro del mes de F",
        "dw_raw.dbo.clientes": "HFECPRO < primer día del mes de F (para marcar Stock vs Nuevo)",
        "intcom.dbo.ccd": "FECHA_CIERRE dentro del mes de F", "intcom.dbo.an_productos": SIN,
    },
    "bancarizados-producto": {
        "csd.dbo.clientes_ds": "HFECPRO = último cierre cargado del mes de F (se detecta solo)",
        "dwh.dbo.gdesemcre001": "procedimiento: la fecha entra como parámetro (el mismo cierre detectado)",
        "dwh.dbo.bregmod001": SIN, "dwh.dbo.rtipcre001": SIN, "dwh.dbo.rtipcre002": SIN, "dwh.dbo.rtipcre003": SIN,
    },
    "clientes-extranjeros": {
        "intcom.dbo.ccd": "Fecha_Cierre = F",
        "intcom.dbo.ccs_fund_f": "fecha_reporte dentro del mes de F (seguros; puede usar otro corte con --fecha-seguros)",
        "rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}": "tabla del cierre: CCP + AAAAMMDD de F en la base DB<AAAAMM> (vía linked server, ruta por defecto)",
        "db{yyyymm}.dbo.ccp{yyyymmdd}": "tabla del cierre: CCP + AAAAMMDD de F en DB<AAAAMM> (ruta directa, --pasivos-directo)",
    },
    "indicadores-clientes": {
        "intcom.dbo.ccd": "Fecha_Cierre = último cierre cargado del mes",
        "csd.dbo.clientes_ds": "HFECPRO = último cierre cargado del mes anterior (desfase 1)",
        "dwh.dbo.hcarcap001": "HFECPRO = último cierre cargado del mes",
        "intcom.dbo.ccs_fund_f": "fecha_reporte = último cierre cargado del mes anterior (desfase 1)",
        "dwh.dbo.scarcap001": REL, "dwh.dbo.scarcap003": REL, "dwh.dbo.bregper001": SIN,
        "intcom.bt.sngc13": SIN, "intcom.bt.fsd002": SIN, "intcom.dbo.distritos_rural_alv": SIN,
    },
}


def regla_de(reporte: str, tabla: str) -> str | None:
    return REGLAS.get(reporte, {}).get(tabla)
