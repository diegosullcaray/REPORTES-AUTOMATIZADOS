
-- ____________ --
-- ** CREDITOS * --
-- ____________ --

------------------------------------------------------------------------------------CREDITOS
-- select distinct fecha_cierre from ccd order by 1 desc

SELECT
	cierre,'Creditos', codigo_pais, Nacionalidad,
	COUNT(DISTINCT CONCAT_WS('-', ISNULL(codigo_pais,'-999'), ISNULL(tipo_doc,'-999'), ISNULL(num_doc,'00000000'))) AS Clientes
from
(
	SELECT DISTINCT
		eomonth(fecha_cierre) cierre, tipo_doc,num_doc, codigo_pais, case when tipo_doc not in ('21', '9', '15') then 'Extranjero' else 'Peru' end Nacionalidad
	FROM [INTCOM].[DBO].[ccd] 
	WHERE fecha_cierre = '2026-07-31' and tipo_persona='F' -- between '2023-04-29' and '2023-04-29'
--rcc_cd.db202303.dbo.ccd20230331
) s
GROUP BY cierre, codigo_pais, Nacionalidad


-- ____________ --
-- ** PASIVOS * --
-- ____________ --

DROP TABLE #temp001

SELECT 
    eomonth(fecha_cierre) AS cierre, 
	tipo_doc, numero_doc, cod_pais, tipo_persona,
    CASE 
        WHEN tipo_doc NOT IN ('21', '9', '15') THEN 'Extranjero' 
        ELSE 'Peru' 
    END AS pais,
    CASE 
        WHEN Max(CASE WHEN Desc_Estado <> 'INACTIVAS' THEN 1 ELSE 0 END) = 1 THEN 'ACTIVAS' 
        ELSE 'INACTIVAS' 
    END AS Desc_Estado, 
	CASE
		WHEN SUM(saldo_mn) between -9999999999 and 1.0 then 'CON SALDO <= PEN 1.00' 
		WHEN SUM(saldo_mn)>1.0 and sum(saldo_mn)<=50.0 then 'CON SALDO < 1.00 a 50.00]' 
		WHEN SUM(saldo_mn)>50.0 then 'CON SALDO > 50.00' end Rango
INTO #temp001
FROM rcc_cd.db202607.dbo.ccp20260731 c -- CAMBIAR
WHERE tipo_persona = 'F' 
GROUP BY eomonth(fecha_cierre), tipo_doc, numero_doc, cod_pais, tipo_persona

SELECT 
    cierre, 
    'Pasivos' AS Tipo,
    cod_pais, 
    pais, 
    COUNT(DISTINCT CONCAT_WS('-', ISNULL(cod_pais,'-999'), ISNULL(tipo_doc,'-999'), ISNULL(numero_doc,'00000000'))) AS Clientes
FROM  
    #temp001
WHERE 
    NOT (Desc_Estado = 'INACTIVAS' AND rango = 'CON SALDO <= PEN 1.00')
GROUP BY 
    cierre, cod_pais, pais;

-- select Genero, count (Genero)
-- from rcc_cd.db202403.dbo.ccp20240331 c -- CAMBIAR 
-- left join fsd001 f on f.petdoc=c.tipo_doc and f.pendoc=c.numero_doc collate SQL_Latin1_General_CP1_CI_AS 
-- where tipo_persona='F' group by Genero having sum(saldo_mn)>1 and Max(case When Desc_Estado<>'INACTIVAS' then 1 Else 0 End)=1

-- ____________ --
-- ** SEGUROS * --
-- ____________ --

SELECT
    cierre,
    'Seguros' AS Categoria,
    pais AS cod_pais,
    Nacionalidad,
    COUNT(DISTINCT CONCAT_WS('-', ISNULL(pais, '-999'), ISNULL(tipo_doc, '-999'), ISNULL(num_doc, '00000000'))) AS Clientes
FROM
(
    SELECT DISTINCT
        EOMONTH(fecha_reporte) AS cierre,
        tipo_doc,
        num_doc,
        pais,
        CASE 
            WHEN tipo_doc IN ('21', '9', '15') THEN 'Peru' 
			WHEN tipo_doc = '99' THEN 'Juridico'
            ELSE 'Extranjero' 
        END AS Nacionalidad
    FROM intcom.[dbo].[CCS_FUND_F] ccd -- SELECT TOP 3 * FROM [dbo].[CCS_FUND_F] ORDER BY FECHA_REPORTE DESC
    WHERE desc_estado IN ('ACTIVO', 'VIGENTE') 
    AND EOMONTH(fecha_reporte) = '2026-06-30' -- cambiar
) s
GROUP BY cierre, pais, Nacionalidad;

-- select distinct fecha_reporte from [dbo].[CCS_FUND_F] order by 1 desc

