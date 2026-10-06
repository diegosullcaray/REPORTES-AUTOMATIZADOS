"""Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas.

Comando: python main.py productos-verdes --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/productos_verdes/. Tablas: ver tablas.USO["productos-verdes"].
"""

from __future__ import annotations

from ..comun.ejecutor import ReporteLote, correr

SQL = r"""
IF OBJECT_ID('tempdb..#jer_ods') IS NOT NULL
BEGIN
    DROP TABLE #jer_ods;
END;

CREATE TABLE #jer_ods
(RFECPRO date,RCODFC varchar(20),RDESFC varchar(250),RCODGRU varchar(20),RDESGRU varchar(250),RCODTER varchar(20),RDESTER varchar(250),RCODCOR varchar(20),RDESCOR varchar(250),RCODUNI varchar(20),RDESUNI varchar(250),RCODUCO varchar(20),RDESUCO varchar(250),RCODSEC varchar(20))

EXEC dwh.dbo.GJERREG001
@fecs='@@F@@'
,@tbl_temp='#jer_ods'
,@cod_jer=3





IF OBJECT_ID('tempdb..#desem') IS NOT NULL
BEGIN
    DROP TABLE #desem;
END;


CREATE TABLE #desem
(HFECPRO date,HCODOPE int,HNUMDOC varchar(20),HTIPDOC smallint,HPAIS smallint,HCODMOD smallint,HTIPOPE smallint,HSUBTIP smallint,HCTACLI int,HCODSUC smallint,HCODSEC varchar(10),HFECDESA date,HMONDES numeric(17,2),HSALCAPMN numeric(17,2),HCODMON smallint,HNUMTAS numeric(9,6),BIDMOD int,SIDS002 int,SIDS006 int)

EXEC dwh.dbo.GDESEMCRE001
@tbl_temp='#desem'
,@fecs='@@F@@'


SELECT c.*,BCODMOD,BTIPOPE,BSUBTIP, p.RDESSUBP, p.RDESPROD,j.RDESTER,  -- DROP TABLE #consolidado
 case when  p.RDESPROD  IN('Agro Vencimiento Verde','Agro Cuota Verde','Agro Cuota Flexible Verde') then 'AGRO' else 'Emprendimiento' end  RDESPROD2
INTO #consolidado -- DROP TABLE #consolidado
FROM #desem c -- SELECT TOP 10 * FROM #desem
LEFT JOIN [dwh].[dbo].[BREGMOD001] AS b ON c.BIDMOD = b.BIDMOD -- SELECT TOP 10 * FROM [dwh].[dbo].[BREGUBT001]
LEFT JOIN [dwh].[dbo].[RTIPCRE001] AS t1 ON b.BCODMOD = t1.RCODMOD AND b.BTIPOPE = t1.RTIPOPE  -- SELECT TOP 10 * FROM [dwh].[dbo].[RTIPCRE001]
LEFT JOIN [dwh].[dbo].[RTIPCRE002] AS t2 ON b.BCODMOD = t2.RCODMOD AND b.BTIPOPE = t2.RTIPOPE AND b.BSUBTIP = t2.RSUBTIP  -- SELECT  * FROM  slc.dbo.RETP006
LEFT JOIN [dwh].[dbo].[RTIPCRE003] AS t3 ON t3.RCODPROD = -- SELECT TOP 10 * FROM [dwh].[dbo].[VPLAPER001]
    CASE
        WHEN t2.RCODPROD IS NULL THEN t1.RCODPROD
        ELSE t2.RCODPROD
    END
LEFT JOIN [dwh].[dbo].[VPLAPER001] per ON c.HCODSEC = per.HCODBT
LEFT JOIN slc.dbo.RETP006 p on b.BCODMOD = p.RCODMOD and b.BTIPOPE = p.RTIPOPE and b.BSUBTIP = p.RSUBTIP
--LEFT JOIN [dwh].[dbo].[BREGUBT001] bt ON c.HCODSEC = bt.BIDUBT
LEFT JOIN #jer_ods j ON EOMONTH(c.HFECPRO) = EOMONTH(j.RFECPRO) AND per.HCODBT = j.RCODSEC
wHERE p.RDESSUBP in ('Producto Verde')
--WHERE BCODMOD IN (101, 104)  -- Agua y Saneamiento
--                  AND BTIPOPE IN (11, 12, 13, 14)
--                  AND BSUBTIP IN (1,45,28)

-------  Calculo de monto desembolsado, total de operaciones, tasa stock, tasa entrada

SELECT
    HFECPRO, RDESPROD2,
    SUM(HMONDES) as monto_desembolsado,
    count (distinct HCODOPE) as numero_operaciones,
    SUM(HMONDES * HNUMTAS)/SUM(HMONDES) AS tasa_entrada,
    count( distinct HNUMDOC) as clientes
FROM #consolidado
GROUP BY HFECPRO,RDESPROD2
order by 1 --

SELECT
HFECPRO, RDESPROD2,RDESTER,
 count( distinct HNUMDOC) as clientes
FROM #consolidado
GROUP BY HFECPRO,RDESPROD2,RDESTER
order by 1,2,3 --

-------  CALCULO STOCK

SELECT * --DROP TABLE #stock
INTO #stock -- select top 3 * from #stock
FROM [dwh].[dbo].[HCARCRE001] -- select top 3 * from [dwh].[dbo].[HCARCRE001]
WHERE HFECPRO IN ( SELECT RFEC FROM [dwh].[dbo].[RFECSIS001] WHERE RFEC = '@@F@@' AND RCIEBT = 1)

SELECT c.*,BCODMOD,BTIPOPE,BSUBTIP, p.RDESSUBP, p.RDESPROD, s2.SNUMTAS, doc.BNUMDOC,j.RDESTER, -- DROP TABLE #consolidado_stock
 case when  p.RDESPROD  IN('Agro Vencimiento Verde','Agro Cuota Verde','Agro Cuota Flexible Verde') then 'AGRO' else 'Emprendiendo' end  RDESPROD2
INTO #consolidado_stock -- drop table #consolidado_stock
FROM #stock c -- SELECT TOP 10 * FROM #consolidado
LEFT JOIN [dwh].[dbo].[BREGMOD001] AS b ON c.BIDMOD = b.BIDMOD -- SELECT TOP 10 * FROM [dwh].[dbo].[BREGUBT001]
LEFT JOIN [dwh].[dbo].[RTIPCRE001] AS t1 ON b.BCODMOD = t1.RCODMOD AND b.BTIPOPE = t1.RTIPOPE  -- SELECT TOP 10 * FROM [dwh].[dbo].[RTIPCRE001]
LEFT JOIN [dwh].[dbo].[RTIPCRE002] AS t2 ON b.BCODMOD = t2.RCODMOD AND b.BTIPOPE = t2.RTIPOPE AND b.BSUBTIP = t2.RSUBTIP  -- SELECT TOP 10 * FROM [dwh].[dbo].[RTIPCRE002]
LEFT JOIN [dwh].[dbo].[RTIPCRE003] AS t3 ON t3.RCODPROD = -- SELECT  * FROM slc.dbo.RETP006
    CASE
        WHEN t2.RCODPROD IS NULL THEN t1.RCODPROD
        ELSE t2.RCODPROD
    END
LEFT JOIN slc.dbo.RETP006 p on b.BCODMOD = p.RCODMOD and b.BTIPOPE = p.RTIPOPE and b.BSUBTIP = p.RSUBTIP
LEFT JOIN [dwh].[dbo].[BREGUBT001] bt ON c.BCODSEC = bt.BIDUBT
LEFT JOIN [dwh].[dbo].[BREGPER001] doc ON c.BIDCLI = doc.BIDPER
LEFT JOIN [dwh].[dbo].[SCARCRE002] AS s2 ON c.SIDS002 = s2.SIDS002 -- select top 3 * from [dwh].[dbo].[BREGUBT001]
LEFT JOIN #jer_ods j ON EOMONTH(c.HFECPRO) = EOMONTH(j.RFECPRO) AND bt.BCODUBT = j.RCODSEC
wHERE p.RDESSUBP in ('Producto Verde')


SELECT -- drop table #consolidado_stock
    HFECPRO,RDESPROD2,
    SUM(HSALCAR) as Saldo_cartera,
    SUM(HSALCAP) as Saldo_capital,
    SUM(HSALCAP * SNUMTAS)/SUM(HSALCAP) AS tasa_stock,
    COUNT(distinct BNUMDOC) as clientes_stock
FROM #consolidado_stock -- select top 3 * from #consolidado_stock
--WHERE RDESSUBP2 = 'Crédito Educativo'
GROUP BY HFECPRO,RDESPROD2
order by 1 --


SELECT
HFECPRO, RDESPROD2,RDESTER,
 count( distinct BNUMDOC) as clientes
FROM #consolidado_stock
GROUP BY HFECPRO,RDESPROD2,RDESTER
order by 1,2,3 --

select top 3  * from #consolidado_stock
"""

REPORTE = ReporteLote(
    comando="productos-verdes",
    descripcion='Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas',
    frecuencia="mensual",
    servidor="slc",
    base="slc",
    sql=SQL,
    archivo="7. Productos_verdes_{mes3}{AA}",
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
