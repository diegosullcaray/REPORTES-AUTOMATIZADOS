"""Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios.

Comando: python main.py saldo-medio-vigente --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/saldo_medio_vigente/. Tablas: ver tablas.USO["saldo-medio-vigente"].
"""

from __future__ import annotations

from ..comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
select HFECPRO,HSALMEDMNVIGE  from storage.com_Act.wjas001 where hfecpro='@@F@@' and htipcod=7

select sfecpro,ssalvigmn  from storage.com_act.sdas001 where sfecpro between '@@F_INI@@' and '@@F@@' and scodagr=1 order by 1 asc
"""

REPORTE = ReporteLote(
    comando="saldo-medio-vigente",
    descripcion='Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios',
    frecuencia="mensual",
    servidor="mish",
    base="storage",
    sql=SQL,
    hojas=(Hoja("Saldo medio mes", columna_fecha="HFECPRO"), Hoja("Saldo diario", columna_fecha="sfecpro"),),
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
