"""Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos).

Comando: python main.py michael-castigos --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/michael_castigos/. Tablas: ver tablas.USO["michael-castigos"].
"""

from __future__ import annotations

from ...comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
--drop table appj.dbo.CUBO_CREDITOS

declare @fec1 varchar(20),@fec2 varchar(20),@tc float
select @fec1='@@F_ANT@@',@fec2='@@F@@'
select @tc=RVALCA from storage.ref.RTCM001 where eomonth(RFECCIE)=eomonth(@fec1)

select *
into #A
from storage.[com_act].HCDA001
where HFECPRO=@fec1

select * into #JER from storage.ref.FJERCOR01(@fec2)

select
A.HCODOPE operacion,
case when A.HCODMON=0 then A.HMONDES else A.HMONDES*@tc end monto_desem_mn,
A.HNUMTAS*case when A.HCODMON=0 then A.HMONDES else A.HMONDES*@tc end interes_mes_mn,
A.HNUMTAS tasa,
A.HSALCAPMN saldo_capital_mn,
A.HNUMTAS*A.HSALCAPMN interes_stock_mn,
isnull(G.ROPEFEC,A.HFECDES) fecha_desem,
A.HCODMON cod_moneda,
iif(A.HCODMON=0,'SOLES','DOLARES') des_moneda,
A.HCODMOD modulo,
A.HDESMOD nom_modulo,
A.HTIPOPE tip_ope,
A.HDTIPOPE des_tip_ope,
A.HSUBTIP sub_tip_ope,
A.HDSUBTIP des_sub_tip_ope,
T3.RDESPROD tip_prod_comercial,
T3.RDESGRU01 gru_prod_comercial,
case when T3.RDESPROD like '%fae%' or T3.RDESPROD like '%react%' then 'PROGRAMAS DEL GOBIERNO' else 'PRODUCTOS FC' end programa_gob,
A.HCTACLI cta_cliente,
A.HDESCLI nom_cliente,
A.HNUMDOC num_doc_cliente,
A.HTIPDOC tip_doc_cliente,
A.HPAIS pais_cliente,
A.HGENPER gen_cliente,
A.HTIPPER tip_per_cliente,
A.HSUCCLI cod_oficina,
A.HDSUCCLI des_oficina,
A.HASEOPER cod_sectorista,
P.HNUMDOC num_doc_sectorista,
P.HDESPER nom_sectorista,
C.RDESGRU gru_sectorista,
C.RDESADM administrador,
C.RDESCOR corredor,
C.RDESTER territorio
into #B
from #A A
left join [storage].[com_act].[RFOC001] G
on A.[HCODOPE]=G.RCODOPE and A.[HINDCAR]<>'REFINANCIADO' and A.[HCODMOD]<>110
left join storage.com_act.RETP001 T1
on T1.RCODMOD=A.HCODMOD and T1.RTIPOPE=A.HTIPOPE
left join storage.com_act.RETP002 T2
on T2.RCODMOD=A.HCODMOD and T2.RTIPOPE=A.HTIPOPE and T2.RSUBTIP=A.HSUBTIP
left join storage.com_act.RETP003 T3
on isnull(T2.RCODPROD,T1.RCODPROD)=T3.RCODPROD
left join #JER C
on C.RCODSEC=A.HASEOPER
left join storage.gpr.VPPH001 P
on P.HCODBT=A.HASEOPER

select *
into #C
from storage.[com_act].HCCA001
 where HFECPRO=@fec2

select A.HFECPRO fecha_cierre,A.HSALCAS*iif(A.HCODMON=101,@tc,1) saldo_castigado_mn,B.*
from #C A
left join #B B
on A.HCODOPE=B.operacion

--drop table #A,#B,#C,#JER
"""

REPORTE = ReporteLote(
    comando="michael-castigos",
    descripcion='Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos)',
    frecuencia="mensual",
    servidor="mish",
    base="storage",
    sql=SQL,
    vacio_valido=True,
    archivo="Datos Cierre {MES} {AA}",
    hojas=(Hoja("Castigos"),),
    libro_compartido=True,
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
