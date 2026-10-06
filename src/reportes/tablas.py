"""Registro de TABLAS: qué tabla usa cada reporte, en qué base vive y cómo saber si está al día.

Es la fuente de verdad del inventario de tablas (`governance/docs/data/tables-inventory.md` se genera de aquí) y de
los comandos `python main.py tablas ...` y `python main.py solicitud-actualizacion ...`.

Campos de `Tabla`:
  (el servidor NO se escribe: se deriva de la base del nombre con config.servidor_de_tabla; ver config.BASES_DE)
  tipo      historica (una foto por fecha) | stock (saldo por fecha) | referencia (catálogo, sin fecha) |
            dinamica (el nombre lleva la fecha: {yyyymmdd}/{yyyymm}) | funcion / procedimiento (la fecha entra como parámetro) |
            relacionada (se une por clave a una tabla H*, sin columna de fecha) | staging | destino
  col_fecha columna con la fecha de carga; permite saber si la tabla llegó al corte (MAX(col_fecha) >= corte)
  confianza confirmada: la columna (o la ausencia de columna de fecha) se comprobó leyendo el SQL de cada reporte | convencion | por_confirmar
Mantenimiento: al usar una tabla nueva, añádela aquí y a USO; la regla `tabla-sin-registrar` lo exige.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import servidor_de_tabla


@dataclass(frozen=True)
class Tabla:
    nombre: str
    tipo: str
    col_fecha: str | None
    confianza: str

    @property
    def servidor(self) -> str:
        """Servidor donde vive la tabla (por su base de datos)."""
        return servidor_de_tabla(self.nombre)

    @property
    def verificable(self) -> bool:
        return self.tipo == "dinamica" or (self.col_fecha is not None and self.tipo in {"historica", "stock"})


# (nombre, tipo, col_fecha, confianza)
_FILAS = [
    ('appj.dbo.salmediovigente1', 'staging', 'hfecpro', 'confirmada'),
    ('csd.dbo.clientes_ds', 'stock', 'HFECPRO', 'confirmada'),
    ('dbrcc.dbo.rcccab{yyyymmdd}', 'dinamica', None, 'confirmada'),
    ('dbrcc.dbo.rccdet{yyyymmdd}', 'dinamica', None, 'confirmada'),
    ('dbriesgos.dbo.gasto_prov_ope_diaria', 'stock', 'FC_DIA', 'confirmada'),
    ('dbriesgos.dbo.prov_proy_{yyyymmdd}_0', 'dinamica', None, 'confirmada'),
    ('dbriesgos.dbo.recaudo_diario_finanzas', 'stock', 'FECHA_CIERRE', 'confirmada'),
    ('db{yyyymm}.dbo.ccd{yyyymmdd}', 'dinamica', None, 'confirmada'),
    ('db{yyyymm}.dbo.ccp{yyyymmdd}', 'dinamica', None, 'confirmada'),
    ('dma.dbo.fecciebt', 'referencia', 'RFCIEBT', 'confirmada'),
    ('dma.dbo.hiscreditos', 'historica', 'HFECPRO', 'confirmada'),
    ('dma.dbo.hisgrupospdm', 'historica', 'HFECPRO', 'confirmada'),
    ('dma.dbo.mrvgrupopdm', 'referencia', None, 'confirmada'),
    ('dw_metadata.dbo.wjercor03', 'referencia', 'RFECPRO', 'confirmada'),
    ('dw_raw.dbo.clientes', 'historica', 'HFECPRO', 'confirmada'),
    ('dw_raw_v2.dbo.cmgmora_recaudo', 'staging', None, 'confirmada'),
    ('dw_raw_v2.dbo.cmgmora_strjercor', 'referencia', None, 'confirmada'),
    ('dwh.dbo.bregmod001', 'referencia', None, 'confirmada'),
    ('dwh.dbo.bregper001', 'referencia', None, 'confirmada'),
    ('dwh.dbo.bregubt001', 'referencia', None, 'confirmada'),
    ('dwh.dbo.gdesemcre001', 'procedimiento', None, 'confirmada'),
    ('dwh.dbo.gjerreg001', 'procedimiento', None, 'confirmada'),
    ('dwh.dbo.hcarcap001', 'historica', 'HFECPRO', 'confirmada'),
    ('dwh.dbo.hcarcre001', 'historica', 'HFECPRO', 'confirmada'),
    ('dwh.dbo.rfecsis001', 'referencia', 'RFEC', 'confirmada'),
    ('dwh.dbo.rregope001', 'referencia', None, 'confirmada'),
    ('dwh.dbo.rtipcre001', 'referencia', None, 'confirmada'),
    ('dwh.dbo.rtipcre002', 'referencia', None, 'confirmada'),
    ('dwh.dbo.rtipcre003', 'referencia', None, 'confirmada'),
    ('dwh.dbo.scarcap001', 'relacionada', None, 'confirmada'),
    ('dwh.dbo.scarcap003', 'relacionada', None, 'confirmada'),
    ('dwh.dbo.scarcre002', 'relacionada', None, 'confirmada'),
    ('dwh.dbo.scarcre006', 'relacionada', None, 'confirmada'),
    ('dwh.dbo.vplaper001', 'referencia', None, 'confirmada'),
    ('intcom.bt.fsd002', 'referencia', None, 'confirmada'),
    ('intcom.bt.sngc13', 'referencia', None, 'confirmada'),
    ('intcom.dbo.an_productos', 'referencia', None, 'confirmada'),
    ('intcom.dbo.ccd', 'stock', 'Fecha_Cierre', 'confirmada'),
    ('intcom.dbo.ccs_fund_f', 'stock', 'fecha_reporte', 'confirmada'),
    ('intcom.dbo.distritos_rural_alv', 'referencia', None, 'confirmada'),
    ('rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}', 'dinamica', None, 'confirmada'),
    ('slc.dbo.retp006', 'referencia', None, 'confirmada'),
    ('storage.com.vdmcom01', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hbcn001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcca001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcda001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcdr001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcdr002', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hcma001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hctc001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hdce001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.hmcm001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_act.retp001', 'referencia', None, 'confirmada'),
    ('storage.com_act.retp002', 'referencia', None, 'confirmada'),
    ('storage.com_act.retp003', 'referencia', None, 'confirmada'),
    ('storage.com_act.rfoc001', 'referencia', None, 'confirmada'),
    ('storage.com_act.sbtvrie001', 'destino', None, 'confirmada'),
    ('storage.com_act.sdae002', 'stock', 'SFECPRO', 'confirmada'),
    ('storage.com_act.sdae003', 'stock', 'SFECPRO', 'confirmada'),
    ('storage.com_act.sdaf002', 'stock', 'SFECPRO', 'confirmada'),
    ('storage.com_act.sdas001', 'stock', 'sfecpro', 'confirmada'),
    ('storage.com_act.sdas005', 'stock', 'SFECPRO', 'confirmada'),
    ('storage.com_act.wcdce001', 'historica', 'hfecpro', 'confirmada'),
    ('storage.com_act.wcdce002', 'historica', 'hfecpro', 'confirmada'),
    ('storage.com_act.wjas001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_pas.hcdp001', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_pas.retp001', 'referencia', None, 'confirmada'),
    ('storage.com_pas.sdps013', 'stock', 'SFECPRO', 'confirmada'),
    ('storage.com_pas.wjas004', 'historica', 'HFECPRO', 'confirmada'),
    ('storage.com_pas.wjas008', 'historica', 'hfecpro', 'confirmada'),
    ('storage.com_seg.sdsf001', 'stock', 'SFECPRO', 'confirmada'),
    ('storage.gpr.vpph001', 'referencia', None, 'confirmada'),
    ('storage.ref.fjercor01', 'funcion', None, 'confirmada'),
    ('storage.ref.fjercor02', 'funcion', None, 'confirmada'),
    ('storage.ref.rcalen001', 'referencia', 'RFEC', 'confirmada'),
    ('storage.ref.rtcm001', 'referencia', 'RFECCIE', 'confirmada'),
    ('storage.ref.vjercor03', 'referencia', None, 'confirmada'),
    ('storage.ref.vjercor04', 'referencia', None, 'confirmada'),
    ('storage.ref.vurbrur01', 'referencia', None, 'confirmada'),
    ('storage.ref.wjercor03', 'referencia', 'RFECPRO', 'confirmada'),
    ('storage.util.fvecfec01', 'funcion', None, 'confirmada'),
]

TABLAS: dict[str, Tabla] = {f[0]: Tabla(*f) for f in _FILAS}

# comando del reporte (main.py) -> tablas que consume
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
    'cartera-sin-asignar': (
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
        'rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}',
        'db{yyyymm}.dbo.ccp{yyyymmdd}',
    ),
    'clientes-jovenes': (
        'csd.dbo.clientes_ds',
        'dwh.dbo.bregper001',
        'dwh.dbo.gdesemcre001',
        'dwh.dbo.hcarcre001',
        'dwh.dbo.scarcre006',
    ),
    'clientes-rurales-migrantes': (
        'storage.com_act.hbcn001',
        'storage.com_act.hcda001',
        'storage.com_act.hcdr001',
        'storage.com_act.hcdr002',
        'storage.com_act.rfoc001',
        'storage.ref.rcalen001',
        'storage.ref.vurbrur01',
    ),
    'cmg-castigos': (
        'storage.com_act.sdas005',
        'storage.ref.rcalen001',
    ),
    'cmg-mora': (
        'dbriesgos.dbo.gasto_prov_ope_diaria',
        'dbriesgos.dbo.prov_proy_{yyyymmdd}_0',
        'dbriesgos.dbo.recaudo_diario_finanzas',
        'dw_raw_v2.dbo.cmgmora_recaudo',
        'dw_raw_v2.dbo.cmgmora_strjercor',
        'storage.com_act.sbtvrie001',
    ),
    'contratacion-electronica': (
        'storage.com_act.wcdce001',
        'storage.com_act.wcdce002',
    ),
    'desembolsos-por-canal': (
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
    'fondeo-estable': (
        'storage.com_pas.wjas008',
        'storage.ref.vjercor04',
    ),
    'giovanni-captaciones': (
        'storage.com_pas.retp001',
        'storage.com_pas.sdps013',
        'storage.com_pas.wjas004',
        'storage.ref.vjercor04',
    ),
    'giovanni-cartera-agro': (
        'storage.com_act.hcda001',
        'storage.com_act.retp001',
        'storage.com_act.retp002',
        'storage.com_act.retp003',
        'storage.ref.fjercor02',
        'storage.ref.wjercor03',
    ),
    'giovanni-seguros': (
        'storage.com.vdmcom01',
        'storage.com_act.retp001',
        'storage.com_act.retp002',
        'storage.com_act.retp003',
        'storage.com_act.sdaf002',
        'storage.com_seg.sdsf001',
        'storage.ref.wjercor03',
    ),
    'heredados-pdm': (
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
    'michael-captaciones': (
        'storage.com_pas.hcdp001',
        'storage.com_pas.retp001',
        'storage.ref.vjercor04',
    ),
    'michael-castigos': (
        'storage.com_act.hcca001',
        'storage.com_act.hcda001',
        'storage.com_act.retp001',
        'storage.com_act.retp002',
        'storage.com_act.retp003',
        'storage.com_act.rfoc001',
        'storage.gpr.vpph001',
        'storage.ref.fjercor01',
        'storage.ref.rtcm001',
    ),
    'productos-verdes': (
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
    'saca-tu-garra': (
        'storage.com_act.hcda001',
        'storage.com_act.hcma001',
        'storage.com_act.hctc001',
        'storage.com_act.sdae002',
        'storage.com_act.sdae003',
        'storage.ref.rcalen001',
    ),
    'saldo-medio-vigente': (
        'storage.com_act.sdas001',
        'storage.com_act.wjas001',
    ),
    'tapp-saldo-medio-territorio': (
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
