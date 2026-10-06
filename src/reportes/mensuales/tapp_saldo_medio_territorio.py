"""TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy).

Comando: python main.py tapp-saldo-medio-territorio --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/tapp_saldo_medio_territorio/. Tablas: ver tablas.USO["tapp-saldo-medio-territorio"].
"""

from __future__ import annotations

from ..comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
use storage;
go

-- INICIO
IF OBJECT_ID('appj.dbo.salmediovigente1') IS NOT NULL DROP TABLE appj.dbo.salmediovigente1
create table #SalMVi  (hfecpro date null,htipcod int null,hcodrel varchar(250)null,HSALMEDMNVIGE float null)

 select RFEC,row_number() over( order by rfec asc )ord  into #fec from storage.ref.rcalen001 where rfec between '@@F_ANT@@' and '@@F@@' and RCIEBT=1

declare @i int=1,@f int,@cf date
set @f =(select count(*) from #fec)

while @i <=@f
begin

set @cf=(select rfec from #fec where ord=@i)

 select A.RFEC RFECCAL,B.RFEC RFECPRO
 into #A--drop table #A
 from storage.util.FVECFEC01(@cf,'ini-hoy|cal') A
 cross apply storage.util.FVECFEC01(A.RFEC,'hoy') B


 ;with a_ as (
 select distinct RFECPRO
 from #A
 ),
 a as (
 select string_agg(format(RFECPRO,'yyyyMMdd'),',') v
 from a_
 )
 select *
 into #B--drop table #B
 from [ref].[FJERCOR02]((select v from a)) C    --select * from [ref].[FJERCOR02]('20220605')

 ;with a_saldo_vigente as (
 select distinct RFECPRO
 from #A
 ),
 b as (
 select A.RFECPRO HFECPRO,
 SCODSEC HCODSEC,
 isnull(RCODUCO,'9999') HCODUCO,
 isnull(RCODUNI,'9999') HCODUNI,
 isnull(RCODGRU,'9999') HCODGRU,
 isnull(cast(RCODCOR as varchar(50)),'9999') HCODCOR,
 isnull(cast(RCODTER as varchar(50)),'9999') HCODTER,
 B.ssalvigmn HSALCAPMNVIGE,
 case when isnull(P.RCODPROD,-99) in (16,17,20,21,22) then B.ssalvigmn else 0 end HSALPGMNVIGE,
 case when isnull(P.RCODPROD,-99) not in (16,17,20,21,22) then B.ssalvigmn else 0 end HSALSPGMNVIGE
 from a_saldo_vigente A
 left join storage.[com_act].SDAS001 B
 on A.RFECPRO=B.SFECPRO and B.SCODAGR=6
 left join #B C
 on C.RFECPRO=B.SFECPRO and C.RCODSEC=B.SCODSEC
 left join storage.com_act.RETP001 P
 on P.RCODMOD=B.SCODMOD and P.RTIPOPE=B.STIPOPE
 )
 ,
  c as (
 select @cf HFECPRO,
 HCODSEC,HCODUCO,HCODUNI,HCODGRU,HCODCOR,HCODTER,
 sum(HSALCAPMNVIGE)/day(@cf) HSALMEDMNVIGE,
 sum(HSALPGMNVIGE)/day(@cf) HSALMPGMNVIGE,
 sum(HSALSPGMNVIGE)/day(@cf) HSALMSPGMNVIGE
 from #A A
 left join b B
 on A.RFECPRO=B.HFECPRO
 group by grouping sets(
 (),
 (HCODSEC),
 (HCODUCO),
 (HCODUNI),
 (HCODGRU),
 (HCODCOR),
 (HCODTER)
 )
 )
 select HFECPRO,
 case
 when HCODSEC is not null then 1
 WHEN HCODUCO Is not null then 17
 --when HCODADM is not null then 11
 when HCODUNI is not null then 18
 when HCODGRU is not null then 21
 when HCODCOR is not null then 19
 when HCODTER is not null then 20
 else 7
 end HTIPCOD ,
  coalesce(
  cast(HCODSEC as varchar(50)),
  cast(HCODUCO as varchar(50)),
  cast(HCODUNI as varchar(50)),
  cast(HCODGRU as varchar(50)),
  cast(HCODCOR as varchar(50)),
  cast(HCODTER as varchar(50)),'231') HCODREL,
  HSALMEDMNVIGE,HSALMPGMNVIGE,HSALMSPGMNVIGE
  into #SMVIGE--drop table #SM
 from c

 insert into #SalMVi
 select hfecpro,htipcod,hcodrel,HSALMEDMNVIGE  from #SMVIGE where htipcod=20

 set @i =@i+1

 drop table #A,#B,#SMVIGE
end
 --

 select * into appj.dbo.salmediovigente1 from #SalMVi   ---select * from #SalMVi   drop table appj.dbo.salmediovigente1

-- FIN INICIO

-- CORRECCIÓN: Se cambió @f a @f_str para evitar la colisión de variables
declare @f_str nvarchar(max)
;with cte_a as (
select distinct hfecpro from #SalMVi
)
select @f_str =  string_agg(format(hfecpro,'yyyyMMdd'),',') from  cte_a

SELECT *
INTO #Jerarquia
FROM [ref].[FJERCOR02](@f_str);

select a.*,b.RDESGRU ,b.rdester
into #SlMedioVi
from appj.dbo.salmediovigente1  a
left join (select distinct rfecpro,RDESGRU,rdester,rcodter  from #Jerarquia) b
on a.hfecpro=b.rfecpro and a.hcodrel=b.RCODTER
order by a.hfecpro asc

;with cte_a as (
SELECT *
       FROM   storage.[com_act].[sdaf002]
       WHERE  scodagr IN ('3')
       AND    sfecpro IN (select rfec from #fec) --select * from #fec
       )
select  Sum(sintmesmn)/Sum(smondesmn) tppmes ,rdester,rdesgru,sfecpro into #tappmes
from cte_a _TS_1
LEFT JOIN (select distinct rfecpro,RDESGRU,rdester,rcodter,rcodsec  from #Jerarquia) _JC
          ON        _TS_1.sfecpro=_JC.rfecpro
          AND       _JC.rcodsec=_TS_1.scodsec
group by rdester,rdesgru,sfecpro



;with cte_a as (
SELECT *
       FROM   storage.[com_act].[sdas001]
       WHERE  scodagr IN ('3')
       AND    sfecpro IN (select rfec from #fec) --select * from #fec
       )
select Sum(sintstockmn)/Sum(ssalcapmn) tppmstock ,rdester,rdesgru,sfecpro into #tappstock
from cte_a _TS_1
LEFT JOIN (select distinct rfecpro,RDESGRU,rdester,rcodter,rcodsec  from #Jerarquia) _JC
          ON        _TS_1.sfecpro=_JC.rfecpro
          AND       _JC.rcodsec=_TS_1.scodsec
group by rdester,rdesgru,sfecpro


;with cta_a as (
select a.hfecpro,a.rdesgru,a.rdester,tppmes,tppmstock,HSALMEDMNVIGE  from #SlMedioVi a  --select * from #tappmes
left join #tappmes  b  --select * from #SlMedioVi
on a.hfecpro=b.sfecpro and a.rdester=b.rdester and a.rdesgru=b.rdesgru
left join #tappstock c
on a.hfecpro=c.sfecpro and a.rdester=c.rdester and a.rdesgru=c.rdesgru
where hcodrel not in('9999')
)
select * from cta_a order by 1 asc
"""

REPORTE = ReporteLote(
    comando="tapp-saldo-medio-territorio",
    descripcion='TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy)',
    frecuencia="mensual",
    servidor="mish",
    base="storage",
    sql=SQL,
    avisos=('Este reporte crea/borra la tabla permanente appj.dbo.salmediovigente1 (como el proceso manual original).',),
    escribe_en_bd=True,
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
