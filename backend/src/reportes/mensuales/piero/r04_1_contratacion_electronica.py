"""Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto).

Comando: python main.py contratacion-electronica --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/contratacion_electronica/. Tablas: ver tablas.USO["contratacion-electronica"].
"""

from __future__ import annotations

from ...comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
declare @numope int,@mondes float,@fecha date
/* Desembolsos habilitados posibles desembolsos CE */
select count(distinct HCODOPE),sum(HMONDESMN) from storage.com_act.wcdce002
where hfecpro ='@@F@@'
group by hfecpro order by 1 asc




/* Desembolsos CE */
select count(distinct HCODOPE),sum(HMONDESMN) from storage.com_act.wcdce001
where hfecpro ='@@F@@'
group by hfecpro order by 1 asc
"""

REPORTE = ReporteLote(
    comando="contratacion-electronica",
    descripcion='Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto)',
    frecuencia="mensual",
    servidor="mish",
    base="storage",
    sql=SQL,
    hojas=(Hoja("CE habilitados"), Hoja("CE desembolsados"),),
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
