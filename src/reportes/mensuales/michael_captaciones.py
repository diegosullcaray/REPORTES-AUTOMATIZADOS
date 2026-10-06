"""Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos).

Comando: python main.py michael-captaciones --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/michael_captaciones/. Tablas: ver tablas.USO["michael-captaciones"].
"""

from __future__ import annotations

from ..comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
/*****

-- EJECUTAR PRIMERO ESTO


exec storage.[com_pas].[PSLWCAP001] '20231230',1
select distinct HFECPRO from storage.com_pas.WCAP001
******/

select *
into #A
from storage.[com_pas].HCDP001
where HFECPRO='@@F@@'

--select *
--into #J--drop table #B
--from storage.ref.FJERCOR02('20241130')


select
A.HFECPRO fecha_cierre,
A.HSBOPER operacion,
A.HSBSBOP sub_operacion,
A.HSBFECH fecha_apertura,
case when eomonth(A.HSBFECH)=eomonth(A.HFECPRO) then 'APERTURA' else 'STOCK' end ind_apertura,
A.HSBMOD modulo,
A.HMDNOM des_modulo,
A.HSBTOPE tipo_operacion,
A.HTONOM des_tipo_operacion,
B.RDESCPROD01 tip_producto,
case A.HCODSEC when 0 then 'RED' when 1 then 'BANCA PREFERENTE' else 'TESORERIA' end canal,
A.HUSERBP usuario_bp,
A.HSBCTA cuenta_cliente,
A.HPENOM nombre_cliente,
A.HPENDOC num_doc_cliente,
A.HPETDOC tip_doc_cliente,
A.HPEPAIS pais_cliente,
case when A.HPETIPO='' then 'J' else A.HPETIPO end tipo_persona,
--D.RDESAGEH agencia_homologada,
D.RDESMAT matriz_ope,
D.RDESMAC macro_corredor_ope,
D.RDESTER territorio_ope,
A.HSBSDO1 saldo_mn,
A.HSBSDO1*A.HSBTPRO gasto_mn,
CONCAT_WS('-',A.HSBOPER,A.HSBSBOP,A.HSBCTA) cuenta_unica
into #B--drop table #B
from #A A
left join storage.[com_pas].RETP001 B
on A.HSBMOD=B.RCODMOD and A.HSBTOPE=B.RTIPOPE
left join storage.ref.VJERCOR04 D
on D.RCODAGE=A.HSBSUC

select
fecha_cierre,
modulo,
des_modulo,
tipo_operacion,
des_tipo_operacion,
tip_producto,
canal,
tipo_persona,
usuario_bp,
matriz_ope,
macro_corredor_ope,
territorio_ope,
ind_apertura,
sum(saldo_mn) saldo_mn,
sum(gasto_mn) gasto_mn,
count(distinct cuenta_unica) cuentas
from #B
group by
fecha_cierre,
modulo,
des_modulo,
tipo_operacion,
des_tipo_operacion,
tip_producto,
canal,
tipo_persona,
usuario_bp,
matriz_ope,
macro_corredor_ope,
territorio_ope,
ind_apertura

select
fecha_cierre,
--isnull(territorio,'SIN ASIGNAR') territorio,
--isnull(corredor,'SIN ASIGNAR') corredor,
tip_producto,
--count(distinct concat_ws('-',num_doc_cliente,tip_doc_cliente,pais_cliente) ) num_clientes
count(distinct num_doc_cliente) num_clientes
from #B
group by
grouping sets(
(fecha_cierre),
(fecha_cierre,tip_producto)
--(fecha_cierre),
--(fecha_cierre,isnull(territorio,'SIN ASIGNAR')),
--(fecha_cierre,isnull(territorio,'SIN ASIGNAR'),isnull(corredor,'SIN ASIGNAR'))
)
order by 1,2


 drop table #A,#B--,#J
"""

REPORTE = ReporteLote(
    comando="michael-captaciones",
    descripcion='Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos)',
    frecuencia="mensual",
    servidor="mish",
    base="storage",
    sql=SQL,
    avisos=('Si WCAP001 no tiene la fecha, hay que correr antes el SP storage.com_pas.PSLWCAP001 (ver comentario del SQL original en docs/LEGADO).',),
    archivo="Datos Cierre {MES} {AA}",
    hojas=(Hoja("Captaciones"),),
    libro_compartido=True,
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
