-- Reporte para el Directorio

-- Esta primera parte se corre en INTCOM
---- Tabla Temporal
if	(object_id('tempdb..#base')) is not null drop table #base

SELECT 
		c.Fecha_Cierre 
		, c.Cta_Cliente
		, c.Genero_Persona
		, DATEDIFF(YEAR, f.pffnac, c.Fecha_Cierre) edad
		, r.Tipo
INTO #base -- SELECT TOP 3 * FROM #base
FROM [INTCOM].[dbo].[ccd] c
	LEFT JOIN [INTCOM].bt.fsd002 f ON f.PFNDOC  COLLATE Modern_Spanish_CI_AS = c.Num_Doc COLLATE Modern_Spanish_CI_AS
    LEFT JOIN [INTCOM].bt.sngc13 u ON u.sngc13ndoc COLLATE Modern_Spanish_CI_AS = c.Num_Doc COLLATE Modern_Spanish_CI_AS
    LEFT JOIN [INTCOM].[dbo].[distritos_rural_alv] r ON (CASE WHEN LEN(r.ubigeo) = 5 THEN '0' + CONVERT(VARCHAR, r.ubigeo) ELSE r.ubigeo END) = u.sngc13ugeo
WHERE Fecha_Cierre in ('2025-07-31','2026-07-31') -- select top 3 * from #base

--- 1.- Total de clientes
select Fecha_Cierre , count(distinct Cta_Cliente) as total_clientes from #base  group by Fecha_Cierre 

--- 2.- Mujeres
select Fecha_Cierre, count(distinct Cta_Cliente) as mujeres  from #base where Genero_Persona = 'F' group by Fecha_Cierre 

--- 3.- Ruralidad
select Fecha_Cierre , count(distinct Cta_Cliente) as ruralidad from #base where  Tipo = 'Rural' group by Fecha_Cierre 

--- 4.- Edad
select Fecha_Cierre, count(distinct Cta_Cliente) as edad from #base where  edad<30 group by Fecha_Cierre 

-- ESTA PARTE SE CORRE EN EL 213
-- BANCARIZADOS Y EXLUSIVOS ES DE UN MES ANTERIROR
use slc
go

-- Total de nuevos clientes
select HFECPRO, count( distinct HCTACLI) Clientes_nuevos from  [csd].[dbo].[Clientes_DS] 
WHERE HFECPRO IN ('2026-06-30','2025-06-30') GROUP BY HFECPRO

-- Bancarizados del total de nuevos
select HFECPRO, count(distinct HCTACLI) Bancarizados from [csd].[dbo].[Clientes_DS] 
WHERE HFECPRO IN ('2026-06-30','2025-06-30') AND HINDBANC = '1' GROUP BY HFECPRO 

-- Exlcusivos del total de nuevos
select HFECPRO, count(distinct HCTACLI) Exclusivos from [csd].[dbo].[Clientes_DS] 
WHERE HFECPRO IN ('2026-06-30','2025-06-30') AND HINDBANCEXC = '1'  GROUP BY HFECPRO 

