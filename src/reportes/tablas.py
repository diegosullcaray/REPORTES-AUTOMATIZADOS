"""Registro de TABLAS: qué tabla usa cada reporte, en qué base vive y cómo saber si está al día.

Es la fuente de verdad del inventario de tablas (`governance/docs/data/tables-inventory.md` se genera de aquí) y de
los comandos `python main.py tablas ...` y `python main.py solicitud-actualizacion ...`.

Campos de `Tabla`:
  alias     conexión desde la que se consulta (dw_raw | rcc | slc); ver config.BASES
  tipo      historica (una foto por fecha) | stock (saldo por fecha) | referencia (catálogo, sin fecha) | otro (vistas W*/V*, sin fecha conocida) |
            dinamica (el nombre lleva la fecha: {yyyymmdd}/{yyyymm}) | staging | destino | procedimiento
  col_fecha columna con la fecha de carga; permite saber si la tabla llegó al corte (MAX(col_fecha) >= corte)
  confianza confirmada (la columna aparece en SQL/código) | convencion (por el prefijo H*/S* del core, VALIDAR) | por_confirmar
Mantenimiento: al usar una tabla nueva, añádela aquí y a USO; la regla `tabla-sin-registrar` lo exige.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tabla:
    nombre: str
    alias: str
    tipo: str
    col_fecha: str | None
    confianza: str

    @property
    def verificable(self) -> bool:
        return self.tipo == "dinamica" or (self.col_fecha is not None and self.tipo in {"historica", "stock"})


# (nombre, alias, tipo, col_fecha, confianza)
_FILAS = [
    ('appj.dbo.salmediovigente1', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('csd.dbo.clientes_ds', 'slc', 'stock', 'HFECPRO', 'confirmada'),
    ('dbrcc.dbo.rcccab{yyyymmdd}', 'rcc', 'dinamica', None, 'por_confirmar'),
    ('dbrcc.dbo.rccdet{yyyymmdd}', 'rcc', 'dinamica', None, 'por_confirmar'),
    ('dbriesgos.dbo.gasto_prov_ope_diaria', 'dw_raw', 'stock', 'FC_DIA', 'confirmada'),
    ('dbriesgos.dbo.prov_proy_{yyyymmdd}_0', 'dw_raw', 'dinamica', None, 'por_confirmar'),
    ('dbriesgos.dbo.recaudo_diario_finanzas', 'dw_raw', 'stock', 'FECHA_CIERRE', 'confirmada'),
    ('db{yyyymm}.dbo.ccd{yyyymmdd}', 'rcc', 'dinamica', None, 'por_confirmar'),
    ('db{yyyymm}.dbo.ccp{yyyymmdd}', 'rcc', 'dinamica', None, 'por_confirmar'),
    ('dma.dbo.fecciebt', 'slc', 'otro', None, 'por_confirmar'),
    ('dma.dbo.hiscreditos', 'slc', 'historica', 'HFECPRO', 'convencion'),
    ('dma.dbo.hisgrupospdm', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('dma.dbo.mrvgrupopdm', 'slc', 'otro', None, 'por_confirmar'),
    ('dw_metadata.dbo.wjercor03', 'rcc', 'otro', None, 'por_confirmar'),
    ('dw_raw.dbo.clientes', 'rcc', 'otro', None, 'por_confirmar'),
    ('dw_raw_v2.dbo.cmgmora_recaudo', 'dw_raw', 'staging', None, 'por_confirmar'),
    ('dw_raw_v2.dbo.cmgmora_strjercor', 'dw_raw', 'otro', None, 'por_confirmar'),
    ('dwh.dbo.bregcap001', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.bregmod001', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.bregmod002', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.bregper001', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.bregubt001', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.gdesemcre001', 'slc', 'procedimiento', None, 'por_confirmar'),
    ('dwh.dbo.gjerreg001', 'slc', 'otro', None, 'por_confirmar'),
    ('dwh.dbo.hcarcap001', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('dwh.dbo.hcarcre001', 'slc', 'historica', 'HFECPRO', 'convencion'),
    ('dwh.dbo.rfecsis001', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.rregope001', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.rtipcre001', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.rtipcre002', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.rtipcre003', 'slc', 'referencia', None, 'por_confirmar'),
    ('dwh.dbo.scarcap001', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('dwh.dbo.scarcap002', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('dwh.dbo.scarcap003', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('dwh.dbo.scarcap004', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('dwh.dbo.scarcre002', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('dwh.dbo.scarcre006', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('dwh.dbo.vplaper001', 'slc', 'otro', None, 'por_confirmar'),
    ('intcom.bt.fsd002', 'slc', 'otro', None, 'por_confirmar'),
    ('intcom.bt.sngc13', 'slc', 'stock', 'FECHA_REPORTE', 'confirmada'),
    ('intcom.dbo.an_productos', 'slc', 'otro', None, 'por_confirmar'),
    ('intcom.dbo.ccd', 'slc', 'stock', 'Fecha_Cierre', 'confirmada'),
    ('intcom.dbo.ccs_fund_f', 'slc', 'stock', 'fecha_reporte', 'confirmada'),
    ('intcom.dbo.clientes_netos_ds', 'slc', 'otro', None, 'por_confirmar'),
    ('intcom.dbo.distritos_rural_alv', 'slc', 'otro', None, 'por_confirmar'),
    ('rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}', 'slc', 'dinamica', None, 'por_confirmar'),
    ('slc.dbo.retp006', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.com.vdmcom01', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_act.hbcn001', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcca001', 'slc', 'historica', 'HFECPRO', 'convencion'),
    ('storage.com_act.hcda001', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcdr001', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcdr002', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcma001', 'slc', 'historica', 'HFECPRO', 'convencion'),
    ('storage.com_act.hctc001', 'slc', 'historica', 'HFECPRO', 'convencion'),
    ('storage.com_act.hdce001', 'slc', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hmcm001', 'slc', 'historica', 'HFECPRO', 'convencion'),
    ('storage.com_act.retp001', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.com_act.retp002', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.com_act.retp003', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.com_act.rfoc001', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.com_act.sbtvrie001', 'slc', 'destino', None, 'por_confirmar'),
    ('storage.com_act.sdae002', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.com_act.sdae003', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.com_act.sdaf002', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.com_act.sdas001', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.com_act.sdas005', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.com_act.wcdce001', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_act.wcdce002', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_act.wjas001', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_pas.hcdp001', 'slc', 'historica', 'HFECPRO', 'convencion'),
    ('storage.com_pas.pslwcap001', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_pas.retp001', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.com_pas.sdps010', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.com_pas.sdps013', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.com_pas.wcap001', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_pas.wjas004', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_pas.wjas008', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.com_seg.sdsf001', 'slc', 'stock', 'SFECPRO', 'convencion'),
    ('storage.gpr.vpph001', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.ref.fjercor01', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.ref.fjercor02', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.ref.rcalen001', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.ref.rtcm001', 'slc', 'referencia', None, 'por_confirmar'),
    ('storage.ref.vjercor03', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.ref.vjercor04', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.ref.vurbrur01', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.ref.wjercor03', 'slc', 'otro', None, 'por_confirmar'),
    ('storage.util.fvecfec01', 'slc', 'otro', None, 'por_confirmar'),
]

TABLAS: dict[str, Tabla] = {f[0]: Tabla(*f) for f in _FILAS}

# reporte -> tablas que consume. Reportes automatizados = nombre del comando; pendientes = carpeta en sql/mensuales|diarias.
USO: dict[str, tuple[str, ...]] = {
    'bancarizados': (
        'dbrcc.dbo.rcccab{yyyymmdd}',
        'dbrcc.dbo.rccdet{yyyymmdd}',
        'db{yyyymm}.dbo.ccd{yyyymmdd}',
        'dw_metadata.dbo.wjercor03',
        'dw_raw.dbo.clientes',
        'intcom.dbo.an_productos',
        'intcom.dbo.ccd',
    ),
    'bancarizados-producto': (
        'csd.dbo.clientes_ds',
        'dwh.dbo.bregmod001',
        'dwh.dbo.gdesemcre001',
        'dwh.dbo.rtipcre001',
        'dwh.dbo.rtipcre002',
        'dwh.dbo.rtipcre003',
    ),
    'cartera_sin_asignar': (
        'storage.com_act.hcda001',
        'storage.com_act.retp001',
        'storage.com_act.retp002',
        'storage.com_act.retp003',
        'storage.com_act.sdas001',
        'storage.ref.fjercor02',
        'storage.ref.vjercor03',
    ),
    'clientes-extranjeros': (
        'intcom.dbo.ccd',
        'intcom.dbo.ccs_fund_f',
    ),
    'clientes_jovenes': (
        'csd.dbo.clientes_ds',
        'dwh.dbo.bregper001',
        'dwh.dbo.gdesemcre001',
        'dwh.dbo.hcarcre001',
        'dwh.dbo.scarcre006',
    ),
    'cmg-mora': (
        'dbriesgos.dbo.gasto_prov_ope_diaria',
        'dbriesgos.dbo.prov_proy_{yyyymmdd}_0',
        'dbriesgos.dbo.recaudo_diario_finanzas',
        'dw_raw_v2.dbo.cmgmora_recaudo',
        'dw_raw_v2.dbo.cmgmora_strjercor',
        'storage.com_act.sbtvrie001',
        'storage.com_act.sdas005',
        'storage.ref.rcalen001',
    ),
    'desembolsos_por_canal': (
        'storage.com_act.hcda001',
        'storage.com_act.hcdr001',
        'storage.com_act.hcdr002',
        'storage.com_act.hdce001',
        'storage.com_act.hmcm001',
        'storage.com_act.rfoc001',
        'storage.gpr.vpph001',
        'storage.ref.fjercor02',
        'storage.ref.rtcm001',
    ),
    'fondeo_estable': (
        'storage.com_pas.wjas008',
        'storage.ref.vjercor04',
    ),
    'heredados_pdm': (
        'dma.dbo.fecciebt',
        'dma.dbo.hiscreditos',
        'dma.dbo.hisgrupospdm',
        'dma.dbo.mrvgrupopdm',
        'dwh.dbo.bregmod001',
        'dwh.dbo.bregubt001',
        'dwh.dbo.rregope001',
        'dwh.dbo.rtipcre001',
        'dwh.dbo.rtipcre002',
        'dwh.dbo.rtipcre003',
    ),
    'indicadores-clientes': (
        'csd.dbo.clientes_ds',
        'dwh.dbo.bregper001',
        'dwh.dbo.hcarcap001',
        'dwh.dbo.scarcap001',
        'dwh.dbo.scarcap003',
        'intcom.bt.fsd002',
        'intcom.bt.sngc13',
        'intcom.dbo.ccd',
        'intcom.dbo.ccs_fund_f',
        'intcom.dbo.distritos_rural_alv',
    ),
    'productos_verdes': (
        'dwh.dbo.bregmod001',
        'dwh.dbo.bregper001',
        'dwh.dbo.bregubt001',
        'dwh.dbo.gdesemcre001',
        'dwh.dbo.gjerreg001',
        'dwh.dbo.hcarcre001',
        'dwh.dbo.rfecsis001',
        'dwh.dbo.rtipcre001',
        'dwh.dbo.rtipcre002',
        'dwh.dbo.rtipcre003',
        'dwh.dbo.scarcre002',
        'dwh.dbo.vplaper001',
        'slc.dbo.retp006',
    ),
    'ratio_ce_nuevos_migrantes': (
        'storage.com_act.hbcn001',
        'storage.com_act.hcda001',
        'storage.com_act.hcdr001',
        'storage.com_act.hcdr002',
        'storage.com_act.rfoc001',
        'storage.com_act.wcdce001',
        'storage.com_act.wcdce002',
        'storage.ref.rcalen001',
        'storage.ref.vurbrur01',
    ),
    'reporte_michael_palacios': (
        'storage.com_act.hcca001',
        'storage.com_act.hcda001',
        'storage.com_act.retp001',
        'storage.com_act.retp002',
        'storage.com_act.retp003',
        'storage.com_act.rfoc001',
        'storage.com_pas.hcdp001',
        'storage.com_pas.pslwcap001',
        'storage.com_pas.retp001',
        'storage.com_pas.wcap001',
        'storage.gpr.vpph001',
        'storage.ref.fjercor01',
        'storage.ref.rtcm001',
        'storage.ref.vjercor04',
    ),
    'reportes_giovanni': (
        'storage.com.vdmcom01',
        'storage.com_act.hcda001',
        'storage.com_act.retp001',
        'storage.com_act.retp002',
        'storage.com_act.retp003',
        'storage.com_act.sdaf002',
        'storage.com_pas.retp001',
        'storage.com_pas.sdps010',
        'storage.com_pas.sdps013',
        'storage.com_pas.wjas004',
        'storage.com_seg.sdsf001',
        'storage.ref.fjercor02',
        'storage.ref.vjercor04',
        'storage.ref.wjercor03',
    ),
    'saca_tu_garra': (
        'storage.com_act.hcda001',
        'storage.com_act.hcma001',
        'storage.com_act.hctc001',
        'storage.com_act.sdae002',
        'storage.com_act.sdae003',
        'storage.ref.rcalen001',
    ),
    'saldo_medio_vigente': (
        'storage.com_act.sdas001',
        'storage.com_act.wjas001',
    ),
    'tapp_saldo_medio_territorio': (
        'appj.dbo.salmediovigente1',
        'storage.com_act.retp001',
        'storage.com_act.sdaf002',
        'storage.com_act.sdas001',
        'storage.ref.fjercor02',
        'storage.ref.rcalen001',
        'storage.util.fvecfec01',
    ),
}


def tablas_de(reporte: str) -> list[Tabla]:
    try:
        return [TABLAS[n] for n in USO[reporte]]
    except KeyError:
        raise KeyError(f"Reporte '{reporte}' sin tablas registradas. Opciones: {', '.join(sorted(USO))}") from None


def reportes_que_usan(tabla: str) -> list[str]:
    return sorted(r for r, ts in USO.items() if tabla in ts)
