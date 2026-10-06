
--== Pasivos ==-- Manuel Siccha 

select H.* 
into #temp_pasivo -- drop table #temp_pasivo
from DWH.[dbo].[HCARCAP001] H
WHERE H.HFECPRO='2025-07-31'


IF OBJECT_ID('tempdb..#Bq_1') IS NOT NULL DROP TABLE #Bq_1;

SELECT		
    CONCAT(P.BTIPDOC, '-', P.BPAIS, '-', P.BNUMDOC) AS Codigo_Cliente, 
    MAX(S3.SGENPER) AS SGENPER,MAX(S3.SCODUBI) AS UBIGEO,
	DATEDIFF(YEAR, s3.SFECCRE, H.HFECPRO)
        - CASE 
            WHEN DATEADD(YEAR, DATEDIFF(YEAR, s3.SFECCRE, H.HFECPRO), s3.SFECCRE) > h.HFECPRO 
            THEN 1 ELSE 0 
          END AS EDAD,
    P.BTIPDOC, 
    P.BPAIS,  
    P.BNUMDOC,
	H.HFECPRO,
    CASE 
        WHEN MAX(CASE WHEN S1.SDESEST <> 'INACTIVAS' THEN 1 ELSE 0 END) = 1 THEN 'ACTIVAS' 
        ELSE 'INACTIVAS' 
    END AS Desc_Estado,
    CASE 
        WHEN SUM(H.HSDOMN) BETWEEN -9999999999 AND 1.0 THEN 'CON SALDO <= PEN 1.00' 
        WHEN SUM(H.HSDOMN) > 1.0 AND SUM(H.HSDOMN) <= 50.0 THEN 'CON SALDO < 1.00 a 50.00]' 
        WHEN SUM(H.HSDOMN) > 50.0 THEN 'CON SALDO > 50.00' 
    END AS Rango
INTO #Bq_1
FROM #temp_pasivo H -- select top 3 * from #temp_pasivo
LEFT JOIN DWH.[DBO].[BREGPER001] P ON H.BIDCLI = P.BIDPER
LEFT JOIN DWH.DBO.SCARCAP001 S1 ON H.SIDS001 = S1.SIDS001
LEFT JOIN DWH.DBO.SCARCAP003 S3 ON H.SIDS003 = S3.SIDS003
--LEFT JOIN DWH.DBO.SCARCAP004 S4 ON H.SIDS004 = S4.SIDS004
GROUP BY P.BTIPDOC, P.BPAIS, P.BNUMDOC,DATEDIFF(YEAR, s3.SFECCRE, H.HFECPRO)
        - CASE 
            WHEN DATEADD(YEAR, DATEDIFF(YEAR, s3.SFECCRE, H.HFECPRO), s3.SFECCRE) > h.HFECPRO 
            THEN 1 ELSE 0 
          END,H.HFECPRO;

--total
select	HFECPRO, count(Codigo_Cliente)
from #Bq_1
where not (Desc_Estado='INACTIVAS' and rango='CON SALDO <= PEN 1.00') -- 728 157
group by HFECPRO

--genero
select		HFECPRO,SGENPER,count(Codigo_Cliente)
from		#Bq_1-- select top 3 *  from #Bq_1 where HFECPRO =''
where not (Desc_Estado='INACTIVAS' and rango='CON SALDO <= PEN 1.00') -- select distinct HFECPRO from wks.dbo.MIDE_HALTCLI002
group by	SGENPER,HFECPRO -- select count(*) from wks.dbo.MIDE_HALTCLI002 where HFECPRO = ''

--ruralidad
select		HFECPRO,b.tipo, count(Codigo_Cliente) Clientes							
from		#Bq_1 a
left join	[INTCOM].[DBO].[distritos_rural_alv] b on a.UBIGEO= ISNULL (b.Ubigeo,'000000' )
where not (Desc_Estado='INACTIVAS' and rango='CON SALDO <= PEN 1.00') 
group by	b.tipo,HFECPRO

-- edad
select
HFECPRO,
	case when Edad<='30' then 'MENOR 30'			
	when Edad>'30' then 'MAYOR 30'
	else  'MAYOR 30'
	end as R_EDAD,count( distinct Codigo_Cliente) Clientes					
from #Bq_1
where not (Desc_Estado='INACTIVAS' and rango='CON SALDO <= PEN 1.00') 
group by case when Edad<='30' then 'MENOR 30'
						when Edad>'30' then 'MAYOR 30' 
						else  'MAYOR 30'
					end	,HFECPRO

