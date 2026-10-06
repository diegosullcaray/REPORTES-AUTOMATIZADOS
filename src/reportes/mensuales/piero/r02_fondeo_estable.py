"""Estadística de tramo / Fondeo estable (Eddy Martínez).

Comando: python main.py fondeo-estable --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/fondeo_estable/. Tablas: ver tablas.USO["fondeo-estable"].
"""

from __future__ import annotations

from ...comun.ejecutor import Hoja, ReporteLote, correr
from ...comun.excel import Columna

SQL = r"""
--Reportes Mensual Fondeo Estable
--Eddy
;with cte_a as (
select * from STORAGE.[com_pas].[WJAS008]
where hfecpro='@@F@@' and HTIPCOD=4 and  RDESCPROD='TODOS'
)
select A.HFECPRO FECHA,b.RDESMAT,A.HSALFESI  from cte_a a
left join (select distinct RCODMAT,RDESMAT from storage.ref.vjercor04)  b
on a.HCODREL=b.RCODMAT
"""

REPORTE = ReporteLote(
    comando="fondeo-estable",
    descripcion='Estadística de tramo / Fondeo estable (Eddy Martínez)',
    frecuencia="mensual",
    servidor="mish",
    base="storage",
    sql=SQL,
    archivo="Saldo_FondeoEstable_{AAAAMMDD}",
    # Formato del Excel entregado: FECHA como 30/09/2026, RDESMAT = Matriz, HSALFESI = Saldo Fondeo Estable
    hojas=(Hoja("Datos", columnas=(
        Columna("FECHA", "FECHA", formato="dd/mm/yyyy"),
        Columna("RDESMAT", "Matriz"),
        Columna("HSALFESI", "Saldo Fondeo Estable"),
    )),),
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
