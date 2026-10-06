		--== Seguros ==--

		-- TOTAL --
		select Fecha_Reporte,count(distinct NUM_DOC) NroClientes
		FROM (
			SELECT Fecha_Reporte, NUM_DOC
			FROM intcom.dbo.CCS_FUND_F
			WHERE Fecha_Reporte = '20250630' AND DESC_ESTADO IN ('ACTIVO', 'VIGENTE')  -- CAMBIAR
    
			UNION ALL
    
			SELECT Fecha_Reporte, NUM_DOC
			FROM intcom.dbo.CCS_FUND_f
			WHERE Fecha_Reporte = '20260630' AND DESC_ESTADO IN ('ACTIVO', 'VIGENTE')  -- CAMBIAR
		) CombinedData
		group by Fecha_Reporte


---------EJECUTAR en INTCOM
-- indicadores de seguro
--drop table #base

WITH Base AS (
    SELECT DISTINCT
        s.fecha_reporte,
        s.tipo_doc,
        s.num_doc,
        f.pfcant genero,
        DATEDIFF(YEAR, f.pffnac, s.fecha_reporte) edad,
        u.sngc13ugeo ubigeo,
        r.Tipo ruralidad
    FROM intcom.dbo.CCS_FUND_F s
    LEFT JOIN intcom.bt.fsd002 f ON f.PFNDOC = s.num_doc
    LEFT JOIN intcom.bt.sngc13 u ON u.sngc13ndoc = s.num_doc
    LEFT JOIN intcom.[dbo].[distritos_rural_alv] r ON (CASE WHEN LEN(r.ubigeo) = 5 THEN '0' + CONVERT(VARCHAR, r.ubigeo) ELSE r.ubigeo END) = u.sngc13ugeo
    WHERE s.Fecha_Reporte = '20250630'  -- cambiar
    
    UNION ALL
    
    SELECT DISTINCT
        s.fecha_reporte,
        s.tipo_doc,
        s.num_doc,
        f.pfcant genero,
        DATEDIFF(YEAR, f.pffnac, s.fecha_reporte) edad,
        u.sngc13ugeo ubigeo,
        r.Tipo ruralidad
    FROM intcom.dbo.CCS_FUND_F  s -- SELECT TOP 3 * FROM dbo.CCS_FUND_F ORDER BY FECHA_REPORTE DESC
    LEFT JOIN intcom.bt.fsd002 f ON f.PFNDOC = s.num_doc
    LEFT JOIN intcom.bt.sngc13 u ON u.sngc13ndoc = s.num_doc
    LEFT JOIN intcom.[dbo].[distritos_rural_alv] r ON (CASE WHEN LEN(r.ubigeo) = 5 THEN '0' + CONVERT(VARCHAR, r.ubigeo) ELSE r.ubigeo END) = u.sngc13ugeo
    WHERE s.Fecha_Reporte = '20260630' -- cambiar . La tabla dbo.CCS_FUND_F tiene datos del 2022, la tabla CCS_FUND_F tiene info del 2023 
)
SELECT * INTO #base from base; -- DROP TABLE #base

----genero
select fecha_reporte,genero,count(*) t from (
select distinct fecha_reporte,tipo_doc,num_doc,genero from #base where genero in ('M','F')
) s
group by fecha_reporte,genero
order by fecha_reporte,genero;

------ruralidad
select fecha_reporte,ruralidad,count(*) t from (
select distinct fecha_reporte,tipo_doc,num_doc,ruralidad from #base where ruralidad in ('Rural','Urbano')
) s
group by fecha_reporte,ruralidad
order by fecha_reporte,ruralidad;

------edad
select fecha_reporte,rango_edad,count(*) t from (
select distinct fecha_reporte,tipo_doc,num_doc,case when edad<30 then '< 30' else '>=30' end rango_edad from #base where edad>0
) s
group by fecha_reporte,rango_edad   
order by fecha_reporte,rango_edad;