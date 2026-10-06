/*--------------*/
-- BANCARIZADOS POR PRODUCTO --
/*--------------*/

-- JERARQUÍA COMERCIAL --

-- Eliminación de tabla temporal para jerarquías si existe

IF OBJECT_ID('tempdb..#jer_ods') IS NOT NULL
BEGIN
    DROP TABLE #jer_ods;
END;

CREATE TABLE #jer_ods 
(RFECPRO date,RCODFC varchar(20),RDESFC varchar(250),RCODGRU varchar(20),RDESGRU varchar(250),RCODTER varchar(20),RDESTER varchar(250),RCODCOR varchar(20),RDESCOR varchar(250),RCODUNI varchar(20),RDESUNI varchar(250),RCODUCO varchar(20),RDESUCO varchar(250),RCODSEC varchar(20))

EXEC dwh.dbo.GJERREG001 
@fecs='20260731'
,@tbl_temp='#jer_ods'
,@cod_jer=3

-- DESEMBOLSOS --

-- Eliminación de tabla temporal para desembolsos si existe

IF OBJECT_ID('tempdb..#desem') IS NOT NULL
BEGIN
    DROP TABLE #desem;
END;

-- Creación de tabla temporal para desembolsos

CREATE TABLE #desem 
(HFECPRO date,HCODOPE int,HNUMDOC varchar(20),HTIPDOC smallint,HPAIS smallint,HCODMOD smallint,HTIPOPE smallint,HSUBTIP smallint,HCTACLI int,HCODSUC smallint,HCODSEC varchar(10),HFECDESA date,HMONDES numeric(17,2),HSALCAPMN numeric(17,2),HCODMON smallint,HNUMTAS numeric(9,6),BIDMOD int,SIDS002 int,SIDS006 int)

-- Ejecutamos sp 

EXEC dwh.dbo.GDESEMCRE001 
@tbl_temp='#desem'
,@fecs='20260731' -- CAMBIAR

/*------------------------------*/
---------------DATA--------------
/*------------------------------*/

-- Eliminación de tabla temporal si existe

IF OBJECT_ID('tempdb..#df') IS NOT NULL
BEGIN
    DROP TABLE #df;
END;

-- Creación de la tabla temporal DF para almacenamiento de información cruzada

SELECT *
INTO #df
FROM 
(
	SELECT A.*, t3.*, J.*
	FROM #desem AS A
		LEFT JOIN [dwh].[dbo].[RTIPCRE001] AS t1
			ON A.HCODMOD  = t1.RCODMOD
				AND A.HTIPOPE = t1.RTIPOPE
		LEFT JOIN [dwh].[dbo].[RTIPCRE002] AS t2
			ON A.HCODMOD  = t2.RCODMOD
				AND A.HTIPOPE = t2.RTIPOPE
				AND A.HSUBTIP = t2.RSUBTIP
		LEFT JOIN [dwh].[dbo].[RTIPCRE003] AS t3
			 ON t3.RCODPROD =
					CASE
					   WHEN t2.RCODPROD IS NULL
						   THEN  t1.RCODPROD
					   ELSE t2.RCODPROD
					   END 
		LEFT JOIN #jer_ods AS J 
			ON A.hfecpro = J.rfecpro 
			AND A.HCODSEC = J.RCODSEC 
) AS df

-- Se cruza DF con otras tablas para sacar el atributo que me permita obtener los productos: Palabra de Mujer, Agropecuario, etc. 

IF OBJECT_ID('tempdb..#prueba') IS NOT NULL
BEGIN
    DROP TABLE #prueba;
END;

SELECT
	A.HFECPRO, A.HCODOPE, A.HNUMDOC, A.HTIPDOC, A.HCTACLI
	, t3.*
INTO #prueba
FROM #df A
	left join [dwh].[dbo].[BREGMOD001] as b
		on A.BIDMOD = b.BIDMOD
	left join [dwh].[dbo].[RTIPCRE001] as t1
		on b.BCODMOD  = t1.RCODMOD
			and b.BTIPOPE = t1.RTIPOPE
	left join [dwh].[dbo].[RTIPCRE002] as t2
		on b.BCODMOD  = t2.RCODMOD
			and b.BTIPOPE = t2.RTIPOPE
			and b.BSUBTIP = t2.RSUBTIP
	left join [dwh].[dbo].[RTIPCRE003] as t3
		 on t3.RCODPROD =
				case
				   when t2.RCODPROD IS NULL
					   then  t1.RCODPROD
				   else t2.RCODPROD
				   end 

-- Selección de clientes nuevos

IF OBJECT_ID('tempdb..#new') IS NOT NULL
BEGIN
    DROP TABLE #new ;
END;

SELECT 
	HCTACLI, HCODSEC, HINDGEN, HINDMIGR, HINDRUR, HINDBANC, hfecpro
INTO #new
FROM [csd].[dbo].[Clientes_DS]
WHERE 
    hfecpro IN ( '20260731') -- solo se cambia esto a la fecha que se tiene que reportar


-- Cruce de tabla de Clientes nuevos con Desembolsados (el código elimina duplicados)

IF OBJECT_ID('tempdb..#df_1_no_duplicates ') IS NOT NULL
BEGIN
    DROP TABLE #df_1_no_duplicates ;
END;

WITH CTE AS (
    SELECT 
        p.HFECPRO, p.HCODOPE, p.HNUMDOC, p.HTIPDOC, p.RDESPROD, 
		n.HINDBANC,
        ROW_NUMBER() OVER (PARTITION BY p.HFECPRO, p.HCTACLI ORDER BY (SELECT NULL)) AS RowNum
    FROM #prueba p 
    INNER JOIN #new n ON p.HCTACLI = n.HCTACLI AND p.HFECPRO = n.HFECPRO
)
SELECT *
INTO #df_1_no_duplicates
FROM CTE
WHERE RowNum = 1;


--select * from #df_1_no_duplicates where RDESPROD like '%IMPULSA%'

-- Código agrupa Consumo y Crédito Educativo como CONSUMO y Emprendiendo Confianza e Iniciando
-- confianza PYME como EMPRENDIENDO CONFIANZA. El resto se mantiene igual

SELECT
    CASE 
        WHEN RDESPROD IN ('AGROPECUARIO', 'CONSTRUYENDO CONFIANZA', 'GARANTIA LIQUIDA', 'INICIANDO OFICIOS', 'PALABRA DE MUJER', 'TRABAJADORES FC') THEN RDESPROD
        WHEN RDESPROD IN ('CONSUMO', 'CREDITO EDUCATIVO') THEN 'CONSUMO'
        WHEN RDESPROD IN ('EMPRENDIENDO CONFIANZA', 'INICIANDO CONFIANZA PYME') THEN 'EMPRENDIENDO CONFIANZA'
		ELSE RDESPROD
    END AS CATEGORIA,
    COUNT(RDESPROD) AS CANTIDAD
FROM #df_1_no_duplicates
WHERE HINDBANC = 1
GROUP BY
    CASE 
        WHEN RDESPROD IN ('AGROPECUARIO', 'CONSTRUYENDO CONFIANZA', 'GARANTIA LIQUIDA', 'INICIANDO OFICIOS', 'PALABRA DE MUJER', 'TRABAJADORES FC') THEN RDESPROD
        WHEN RDESPROD IN ('CONSUMO', 'CREDITO EDUCATIVO') THEN 'CONSUMO'
        WHEN RDESPROD IN ('EMPRENDIENDO CONFIANZA', 'INICIANDO CONFIANZA PYME') THEN 'EMPRENDIENDO CONFIANZA'
		ELSE RDESPROD
    END
ORDER BY 1 ASC;

