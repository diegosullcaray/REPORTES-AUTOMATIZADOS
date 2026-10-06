
IF OBJECT_ID('tempdb..#desem') IS NOT NULL
BEGIN
    DROP TABLE #desem;
END;

CREATE TABLE #desem 
(HFECPRO date,HCODOPE int,HNUMDOC varchar(20),HTIPDOC smallint,HPAIS smallint,HCODMOD smallint,HTIPOPE smallint,HSUBTIP smallint,HCTACLI int,HCODSUC smallint,HCODSEC varchar(10),HFECDESA date,HMONDES numeric(17,2),HSALCAPMN numeric(17,2),HCODMON smallint,HNUMTAS numeric(9,6),BIDMOD int,SIDS002 int,SIDS006 int)

EXEC dwh.dbo.GDESEMCRE001 
@tbl_temp='#desem'
,@fecs='20260630'



-- 1. Limpieza de la tabla temporal si ya existe
IF OBJECT_ID('tempdb..#pedido') IS NOT NULL DROP TABLE #pedido;

-- 2. Creación de la tabla #pedido con cálculo de EDAD y CLIENTE_NUEVO
SELECT 
    c.HFECPRO,
    c.HNUMDOC,
    c.HTIPDOC,
    c.HPAIS,
    c.HCTACLI,
    c.HCODOPE,
    -- Cálculo preciso de la EDAD
    DATEDIFF(YEAR, s6.SFECPER, c.HFECPRO)
        - CASE 
            WHEN DATEADD(YEAR, DATEDIFF(YEAR, s6.SFECPER, c.HFECPRO), s6.SFECPER) > c.HFECPRO 
            THEN 1 ELSE 0 
          END AS EDAD,
    -- Lógica de Cliente Nuevo
    CASE 
        WHEN ds.HCTACLI IS NOT NULL THEN 'Nuevo' 
        ELSE 'Antiguo' 
    END AS TIPO_CLIENTE
INTO #pedido
FROM #desem c
LEFT JOIN [dwh].[dbo].[SCARCRE006] s6 ON c.SIDS006 = s6.SIDS006
LEFT JOIN [csd].[dbo].[Clientes_DS] ds ON c.HCTACLI = ds.HCTACLI and c.HFECPRO = ds.HFECPRO;


-- select top 3  * from #pedido  select distinct TIPO_CLIENTE from #pedido 
-- 3. Conteo de valores únicos solicitado (Edad 18-30 y Clientes Nuevos)
SELECT 
    HFECPRO, 
	    COUNT(DISTINCT 
        CAST(HNUMDOC AS VARCHAR) + '-' + 
        CAST(HTIPDOC AS VARCHAR) + '-' + 
        CAST(HPAIS AS VARCHAR)
    ) AS Total_General,
    -- Conteo solo de Clientes Nuevos
    COUNT(DISTINCT 
        CASE WHEN TIPO_CLIENTE = 'Nuevo' THEN 
            CAST(HNUMDOC AS VARCHAR) + '-' + 
            CAST(HTIPDOC AS VARCHAR) + '-' + 
            CAST(HPAIS AS VARCHAR) 
        ELSE NULL END
    ) AS Total_Nuevos
FROM #pedido
WHERE EDAD BETWEEN 18 AND 30
GROUP BY HFECPRO
ORDER BY HFECPRO;


---- STOCK
-- DROP table #stock_joven
select * into #stock from [dwh].[dbo].[HCARCRE001] c WHERE c.HFECPRO = '2026-06-30'

SELECT 
    c.HFECPRO,
    doc.BNUMDOC,
    doc.BTIPDOC,
    doc.BPAIS,
    c.BCTACLI,
    c.BCODOPE,
    DATEDIFF(YEAR, s6.SFECPER, c.HFECPRO)
        - CASE 
            WHEN DATEADD(YEAR, DATEDIFF(YEAR, s6.SFECPER, c.HFECPRO), s6.SFECPER) > c.HFECPRO 
            THEN 1 ELSE 0 
          END AS EDAD
INTO #stock_joven
FROM #stock c -- select top 3 * from [dwh].[dbo].[BREGPER001]
LEFT JOIN [dwh].[dbo].[SCARCRE006] s6 ON c.SIDS006 = s6.SIDS006
LEFT JOIN [dwh].[dbo].[BREGPER001] doc ON c.BIDCLI = doc.BIDPER 

SELECT 
    -- Conteo total stock
    HFECPRO, 
	    COUNT(DISTINCT 
        CAST(BNUMDOC AS VARCHAR) + '-' + 
        CAST(BTIPDOC AS VARCHAR) + '-' + 
        CAST(BPAIS AS VARCHAR)
    ) AS Total_General
FROM #stock_joven
WHERE EDAD BETWEEN 18 AND 30
GROUP BY HFECPRO
ORDER BY HFECPRO;


