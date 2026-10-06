--====================================================================--
------------------- INFORMACIÓN PARA PARA FINANZAS ---------------------
--====================================================================--

--1. DIAGRAMA DE VENN-----------------------------------------------

--====================================================================--
------------------- DIAGRAMA DE VENN PARA FINANZAS ---------------------
--====================================================================--

--ANTES REVISA CUAL ES LA FECHA DEL CIERRE DE MES (PUEDE QUE SEA EL 29)
declare @p_fecha date ='20260331' -- CAMBIAR

--== Creando temporales por cartera ==--


	-- a. Temporal de Activos --
	----------------------------
		if		(object_id('tempdb..#TmpCCD')) is not null drop table #TmpCCD
		select	distinct a.Num_Doc															
		into	#TmpCCD
		from	[INTCOM].[dbo].[ccd] a
		where	a.Fecha_Cierre= '20260331' --@p_fecha



	-- b. Temporal de Seguros --
	----------------------------

		if		(object_id('tempdb..#TmpCCS')) is not null drop table #TmpCCS

		select	distinct case when	len(a.Num_Doc)<8 then right('00000000'+a.Num_Doc,8) else a.Num_Doc end Nro_Doc_Identidad
		into	#TmpCCS
		from	[INTCOM].[dbo].[CCS_FUND_F]	a
		where	a.fecha_reporte='20260228' --@p_fecha
		and		a.cod_seguro in ('3','7','803','200','14','806','815','8','802','814','999')
		and		a.DESC_ESTADO in ('ACTIVO','VIGENTE')

	-- c. Temporal de Captaciones Ajustados --
	--------------------------------------
		if			(object_id('tempdb..#Bq')) is not null drop table #Bq
		select		BNUMDOC--,S1.SDESEST
					,Case	when Max(Case When SDESEST<>'INACTIVAS' Then 1 Else 0 End)=1 Then 'ACTIVAS' Else 'INACTIVAS' end Desc_Estado
					,case	when	SUM(HSDOMN) between -9999999999 and 1.0 then 'CON SALDO <= PEN 1.00' 
					when	SUM(HSDOMN)>1.0 and sum(HSDOMN)<=50.0 then 'CON SALDO < 1.00 a 50.00]' 
					when	SUM(HSDOMN)>50.0 then 'CON SALDO > 50.00' end Rango
		into		#Bq		--drop table #Bq
		From		DWH.[dbo].[HCARCAP001] H
		LEFT JOIN DWH.[DBO].[BREGPER001] P ON H.BIDCLI = P.BIDPER
		LEFT JOIN DWH.DBO.SCARCAP001 S1 ON H.SIDS001 = S1.SIDS001
		WHERE H.HFECPRO='2026-03-31'
		group by	BNUMDOC	


select distinct Desc_Estado from  #Bq
select top 3 * from #Bq

select distinct SDESEST from DWH.DBO.SCARCAP001






	SELECT H.HFECPRO, P.BTIPDOC,P.BNUMDOC,  H.BCTACLI,C.BSUBOPE, H.BSUCCLI, M.BCODMOD,
        S2.SFECAPE,S1.SDTIPOPE,S1.SDESEST, S4.SDTIPCTA, S1.SDESMON
FROM DWH.[dbo].[HCARCAP001] H
LEFT JOIN DWH.[DBO].[BREGPER001] P ON H.BIDCLI = P.BIDPER
LEFT JOIN DWH.DBO.SCARCAP001 S1 ON H.SIDS001 = S1.SIDS001
LEFT JOIN DWH.DBO.SCARCAP002 S2 ON H.SIDS002 = S2.SIDS002
LEFT JOIN DWH.DBO.SCARCAP004 S4 ON H.SIDS004 = S4.SIDS004
LEFT JOIN DWH.DBO.BREGMOD002 M (NOLOCK) ON H.BIDMOD = M.BIDMOD
left join dwh.[dbo].[BREGCAP001] C ON H.BIDCAP=C.BIDCAP 
WHERE H.HFECPRO='2026-03-31'
 
select top 2  * from [dbo].[HCARCAP001]
select top 2  * from [dbo].[BREGPER001]
select top 2  * from [dbo].[SCARCAP001]
select top 2  * from [dbo].[SCARCAP002]
select top 2  * from [dbo].[SCARCAP004]
select top 2  * from [dbo].[BREGMOD002]
select top 2  * from [dbo].[BREGCAP001]


		if			(object_id('tempdb..#Aq')) is not null drop table #Aq
		select		*
		into		#Aq		
		from		[RCC_CD].[DB202602].[dbo].[CCP20260228] -- ** CAMBIAR **



		
		if			(object_id('tempdb..#Bq')) is not null drop table #Bq
		select		Numero_Doc
					,Case	when Max(Case When Desc_Estado<>'INACTIVAS' Then 1 Else 0 End)=1 Then 'ACTIVAS' Else 'INACTIVAS' end Desc_Estado
					,case	when	SUM(saldo_mn) between -9999999999 and 1.0 then 'CON SALDO <= PEN 1.00' 
					when	SUM(saldo_mn)>1.0 and sum(saldo_mn)<=50.0 then 'CON SALDO < 1.00 a 50.00]' 
					when	SUM(saldo_mn)>50.0 then 'CON SALDO > 50.00' end Rango
		into		#Bq		--drop table #Bq
		From		#Aq A
		group by	Numero_Doc	

		if			(object_id('tempdb..#tmp0012')) is not null drop table #tmp0012
		select		distinct case when len(Numero_Doc)<8 then right('00000000'+Numero_Doc,8) else	Numero_Doc end Numero_Doc	
		into		#tmp0012--drop table #tmp0012
		from		#Bq
		where		not (Desc_Estado='INACTIVAS' and rango='CON SALDO <= PEN 1.00')

--== Creando temporales por tipo de cliente ==--

	-- Solo Activos --
	------------------
		if			(object_id('tempdb..#A')) is not null drop table #A
		select		distinct A.Num_Doc, 'A' Tipo
		into		#A
		from		#TmpCCD A
		left join	#tmp0012 B 	on		A.Num_Doc collate Modern_Spanish_CI_AS=B.Numero_Doc collate Modern_Spanish_CI_AS
		left join	#TmpCCS C 	on		A.Num_Doc collate Modern_Spanish_CI_AS=C.Nro_Doc_Identidad collate Modern_Spanish_CI_AS
		where		B.Numero_Doc is null and C.Nro_Doc_Identidad is null

	-- Solo Captaciones --
	------------------
		if			(object_id('tempdb..#B')) is not null drop table #B
		select		distinct A.Numero_Doc, 'P' Tipo
		into		#B
		from		#tmp0012 A
		left join	#TmpCCD B	on		A.Numero_Doc collate Modern_Spanish_CI_AS=B.Num_Doc collate Modern_Spanish_CI_AS
		left join	#TmpCCS C	on		A.Numero_Doc collate Modern_Spanish_CI_AS=C.Nro_Doc_Identidad collate Modern_Spanish_CI_AS
		where		B.Num_Doc is null and C.Nro_Doc_Identidad is null

	-- Solo Seguros --
	------------------
		if			(object_id('tempdb..#G')) is not null drop table #G
		select		distinct A.Nro_Doc_Identidad, 'S' Tipo
		into		#G
		from		#TmpCCS A
		left join	#tmp0012 B	on		A.Nro_Doc_Identidad collate Modern_Spanish_CI_AS=B.Numero_Doc collate Modern_Spanish_CI_AS
		left join	#TmpCCD C	on		A.Nro_Doc_Identidad collate Modern_Spanish_CI_AS=C.Num_Doc collate Modern_Spanish_CI_AS
		where		B.Numero_Doc is null and C.Num_Doc is null

	-- Activos / Captaciones --
	-----------------------	
		if			(object_id('tempdb..#C')) is not null drop table #C
		select		distinct A.Num_Doc, 'AP' Tipo
		into		#C
		from		#TmpCCD A
		join		#tmp0012 B	on		A.Num_Doc collate Modern_Spanish_CI_AS=B.Numero_Doc collate Modern_Spanish_CI_AS
		left join	#TmpCCS C	on		A.Num_Doc collate Modern_Spanish_CI_AS=C.Nro_Doc_Identidad collate Modern_Spanish_CI_AS
		where		C.Nro_Doc_Identidad is null

	-- Activos / Seguros --
	-----------------------
		if			(object_id('tempdb..#D')) is not null drop table #D
		select		distinct A.Num_Doc, 'AS' Tipo
		into		#D
		from		#TmpCCD A
		join		#TmpCCS B	on		A.Num_Doc collate Modern_Spanish_CI_AS=B.Nro_Doc_Identidad collate Modern_Spanish_CI_AS
		left join	#tmp0012 c	on		A.Num_Doc collate Modern_Spanish_CI_AS=C.Numero_Doc collate Modern_Spanish_CI_AS
		where		C.Numero_Doc is null

	-- Captaciones / Seguros --
	-----------------------
		if			(object_id('tempdb..#E')) is not null drop table #E
		select		distinct A.Nro_Doc_Identidad, 'PS' Tipo
		into		#E
		from		#TmpCCS A
		join		#tmp0012 B	on		A.Nro_Doc_Identidad collate Modern_Spanish_CI_AS=B.Numero_Doc collate Modern_Spanish_CI_AS
		left join	#TmpCCD C	on		A.Nro_Doc_Identidad collate Modern_Spanish_CI_AS=C.Num_Doc collate Modern_Spanish_CI_AS
		where		C.Num_Doc is null

		-- Activos / Captaciones / Seguros --
	---------------------------------
		if			(object_id('tempdb..#F')) is not null drop table #F
		select		distinct A.Num_Doc, 'APS' Tipo
		into		#F
		from		#TmpCCD A
		join		#tmp0012 B	on		A.Num_Doc collate Modern_Spanish_CI_AS=B.Numero_Doc collate Modern_Spanish_CI_AS
		join		#TmpCCS C	on		A.Num_Doc collate Modern_Spanish_CI_AS=C.Nro_Doc_Identidad collate Modern_Spanish_CI_AS


--== Uniendo Temporales ==--

	-- Resultado --
	----------------
		if			(object_id('tempdb..#BaseUnion')) is not null drop table #BaseUnion
		select		distinct Num_Doc collate Modern_Spanish_CI_AS num_doc, Tipo
		into		#BaseUnion							from		#A
		union       select		distinct Num_Doc collate Modern_Spanish_CI_AS, Tipo				from		#C
		union       select		distinct Numero_Doc collate Modern_Spanish_CI_AS, Tipo			from		#B
		union       select		distinct Nro_Doc_Identidad collate Modern_Spanish_CI_AS, Tipo	from		#G
		union       select		distinct Num_Doc collate Modern_Spanish_CI_AS, Tipo				from		#D
		union       select		distinct Nro_Doc_Identidad collate Modern_Spanish_CI_AS, Tipo	from		#E
		union       select		distinct Num_Doc collate Modern_Spanish_CI_AS, Tipo				from		#F  -- SELECT COUNT(*) FROM #BaseUnion  734 206
 
--== Caracteristicas de los Clientes ==--  SELECT TOP 3 * FROM #BaseUnion 

-- declare @p_fecha date ='20251231'

		if			(object_id('tempdb..#APERTURA')) is not null drop table #APERTURA
		select		Numero_Doc,max(Fecha_Apertura) Fecha_Apertura  
		into		#APERTURA --drop table #APERTURA   
		from		[DB202602].[dbo].[CCP20260228] -- cambiar
		group by	Numero_Doc   -- select count(*) from #APERTURA
  
		if			(object_id('tempdb..#CLIENTE_SUCURSAL')) is not null drop table #CLIENTE_SUCURSAL
		select		Fecha_Cierre,A.Numero_Doc,max(Cod_Suc)Cod_Suc,max(Ubigeo)Ubigeo  
		into		#CLIENTE_SUCURSAL--select count(*) from #CLIENTE_SUCURSAL
		from		[DB202602].[dbo].[CCP20260228] A -- cambiar 
		join		#APERTURA B on A.Numero_Doc collate Modern_Spanish_CI_AS=B.Numero_Doc collate Modern_Spanish_CI_AS and A.Fecha_Apertura=B.Fecha_Apertura  
		group by	Fecha_Cierre,A.Numero_Doc   
  
		if			(object_id('tempdb..#CLIENTE_GENERO')) is not null drop table #CLIENTE_GENERO
		select		Numero_Doc,max(Genero)Genero  
		into		#CLIENTE_GENERO--drop table #CLIENTE_GENERO  
		from		[DB202602].[dbo].[CCP20260228] A  -- cambiar
		group by	A.Numero_Doc     --select count(*) from #CLIENTE_GENERO


		if			(object_id('tempdb..#CLIENTE_PASIVO')) is not null drop table #CLIENTE_PASIVO
		select		A.*,B.Genero  
		into		#CLIENTE_PASIVO--drop table #CLIENTE_PASIVO  
		from		#CLIENTE_SUCURSAL A    -- select count(*) from #CLIENTE_PASIVO
		left join	#CLIENTE_GENERO B on A.Numero_Doc=B.Numero_Doc -- select top 3 * from    #CLIENTE_PASIVO
  
 

		if			(object_id('tempdb..#DESEMBOLSO')) is not null drop table #DESEMBOLSO
		select		Num_Doc,max(Fec_Desembolso) Fec_Desembolso  
		into		#DESEMBOLSO --drop table #DESEMBOLSO   
		from		ccd
		where		eomonth(Fecha_Cierre)=eomonth(@p_fecha)
		group by	Num_Doc
		   
   		if			(object_id('tempdb..#CLIENTE_SUCURSAL_ACT')) is not null drop table #CLIENTE_SUCURSAL_ACT 
		select		A.Fecha_Cierre,A.Num_Doc,max(Cod_Suc_Of_Credito)Cod_Suc_Of_Credito,max(Ubigeo) Ubigeo  
		into		#CLIENTE_SUCURSAL_ACT--drop table #CLIENTE_SUCURSAL_ACT  
		from		ccd A  
		join		#DESEMBOLSO B on A.Num_Doc collate Modern_Spanish_CI_AS=B.Num_Doc collate Modern_Spanish_CI_AS and A.Fec_Desembolso=B.Fec_Desembolso  
		where		eomonth(A.Fecha_Cierre)=eomonth(@p_fecha)  
		group by	A.Fecha_Cierre,A.Num_Doc
		   
   		if			(object_id('tempdb..#CLIENTE_GENERO_ACT')) is not null drop table #CLIENTE_GENERO_ACT
		select		A.Num_Doc,max(Genero_Persona) Genero  
		into		#CLIENTE_GENERO_ACT--drop table #CLIENTE_GENERO_ACT  
		from		ccd A  
		where		eomonth(A.Fecha_Cierre)=eomonth(@p_fecha)
		group by	A.Num_Doc  
		
		if			(object_id('tempdb..#CLIENTE_ACTIVO')) is not null drop table #CLIENTE_ACTIVO
		select		A.*,B.Genero  
		into		#CLIENTE_ACTIVO--drop table #CLIENTE_ACTIVO  
		from		#CLIENTE_SUCURSAL_ACT A   
		left join	#CLIENTE_GENERO_ACT B on A.Num_Doc=B.Num_Doc    

		-------------------------
		if			(object_id('tempdb..#CLIENTE_SEGURO')) is not null drop table #CLIENTE_SEGURO
		select		FECHA_REPORTE as Fecha_Cierre,case  when	len(a.Num_Doc)<8 then right('00000000'+a.Num_Doc,8) else a.Num_Doc end Num_Doc,max(a.COD_AGENCIA) Cod_Suc_Of_Credito,max(s.sngc13ugeo) Ubigeo,f.pfcant Genero
		into		#CLIENTE_SEGURO--drop table #CLIENTE_GENERO_ACT  
		from		dbo.CCS_FUND_F A  
		left join bt.fsd002 f on f.pftdoc=a.TIPO_DOC and f.pfndoc=a.NUM_DOC
		left join bt.sngc13 s on s.sngc13tdoc=a.tipo_doc and s.sngc13ndoc=a.num_doc and s.DOCOD=1
		where		eomonth(A.FECHA_REPORTE)=eomonth(@p_fecha) -- Verificar fechas de fin de mes
		and			a.cod_seguro in ('3','7','803','200','14','806','815','8','802','814','999')
		and			a.DESC_ESTADO in ('ACTIVO','VIGENTE')
		group by	FECHA_REPORTE,case when len(a.Num_Doc)<8 then right('00000000'+a.Num_Doc,8) else a.Num_Doc end,f.pfcant

		--select * from sngc13
		--select * from fsd002
				
        --173361


		--select * from #CLIENTE_ACTIVO
		---------------------------
		if			(object_id('tempdb..#CLIENTES_DATOS')) is not null drop table #CLIENTES_DATOS
		select		fecha_cierre,num_doc collate Modern_Spanish_CI_AS num_doc,cod_suc_of_credito,ubigeo collate Modern_Spanish_CI_AS ubigeo,genero collate Modern_Spanish_CI_AS genero  
		into		#CLIENTES_DATOS--drop table #CLIENTES_DATOS  
		from		#CLIENTE_ACTIVO  
		UNION		
		select		A.*   
		from		#CLIENTE_PASIVO A  
		left join	#CLIENTE_ACTIVO B on A.Numero_Doc collate Modern_Spanish_CI_AS=B.Num_Doc collate Modern_Spanish_CI_AS  
		where		B.Num_Doc is null  
		UNION		
		select		A.fecha_cierre,a.num_doc collate Modern_Spanish_CI_AS num_doc,a.cod_suc_of_credito,a.ubigeo collate Modern_Spanish_CI_AS ubigeo,a.genero collate Modern_Spanish_CI_AS genero
		from		#CLIENTE_SEGURO A  
		left join	#CLIENTE_ACTIVO B on A.Num_Doc collate Modern_Spanish_CI_AS=B.Num_Doc collate Modern_Spanish_CI_AS  
		left join	#CLIENTE_PASIVO C on A.Num_Doc collate Modern_Spanish_CI_AS=C.Numero_Doc collate Modern_Spanish_CI_AS
		where		B.Num_Doc is null and C.Numero_Doc is null  		 
  
		if			(object_id('tempdb..#DATOS_CLIENTES_FINAL')) is not null drop table #DATOS_CLIENTES_FINAL
		select		A.Fecha_Cierre,case when  len(A.Num_Doc)<8 then right('00000000'+A.Num_Doc,8) else A.Num_Doc end Numero_Doc,Cod_Suc_Of_Credito,Genero,Ubigeo,'' cTerritorio,'' cRegion,'' cDesAgeMat --B.cTerritorio,B.cRegion,B.cDesAgeMat  
		into		#DATOS_CLIENTES_FINAL--select top 3 *from #DATOS_CLIENTES_FINAL  
		from		#CLIENTES_DATOS A   
		--left join	(select distinct ncodageori,cTerritorio,cRegion,cDesAgeMat from agencias_dim_ic) B on A.Cod_Suc_Of_Credito=B.nCodAgeOri  



		--SELECT * FRom #DATOS_CLIENTES_FINAL where Cod_Suc_Of_Credito is null

		if			(object_id('tempdb..#BASE_FINAL_0')) is not null drop table #BASE_FINAL_0
		select		@p_fecha as FEcha_Cierre,a.Tipo,a.Num_Doc,b.Cod_Suc_Of_Credito,b.Genero,b.Ubigeo,case when b.Cod_Suc_Of_Credito='135' then 'LIMA ORIENTE' else b.cTerritorio end cTerritorio,case when b.Cod_Suc_Of_Credito='135' then 'LIMA 1' else b.cRegion end cRegion,case when b.Cod_Suc_Of_Credito='135' then 'AG JAVIER PRADO' else b.cDesAgeMat end cDesAgeMat
		into		#BASE_FINAL_0
		from		#BaseUnion				a
		left join	#DATOS_CLIENTES_FINAL	b
		on			a.Num_Doc collate Modern_Spanish_CI_AS=b.Numero_Doc collate Modern_Spanish_CI_AS

		delete from #BASE_FINAL_0 where ubigeo like '%.%';

		INSERT INTO		[INTCOM].[dbo].[clientes_netos_ds]    
		select			*
		from			#BASE_FINAL_0
------------   SOLO CORRER HASTA AHI: PRIMERA PARTE ---------------------------

-- select distinct FEcha_Cierre from dbo.clientes_netos_ds 


-- primero ejecutar para el mes de 2023
-- ejecutar luego para el mes de 2023
-- truncate table [INTCOM].[dbo].[clientes_netos_ds]  

-- select count(*) from #DATOS_CLIENTES_FINAL where fecha_cierre = '2023-12-30' -- 1 193 345
-- select * from #BaseUnion
-- select count(*) from dbo.clientes_netos_ds where Fecha_cierre = '2022-12-31' -- 700 081
-- select count(*) from dbo.clientes_netos_ds where Fecha_cierre = '2023-12-30' -- 724 613


select fecha_cierre,count(*) t from dbo.clientes_netos_ds group by fecha_cierre;

select num_doc, FEcha_Cierre
from dbo.clientes_netos_ds
where Tipo like '%P%'
group by num_doc, FEcha_Cierre
having count (distinct ubigeo) > 1

select num_doc, FEcha_Cierre
from dbo.clientes_netos_ds
where Tipo like '%P%'
group by num_doc, FEcha_Cierre
having count (num_doc) > 1

select * from dbo.clientes_netos_ds

select * from 
-- luego ejecutar 
	-- Resultado Final --
	---------------------
	

		--== Diagrama de Venn==-- 

		select tipo,count(num_doc) from #BaseUnion where num_doc != '' group by tipo -- Daniel Roque de la Cruz 

		
		--== Pasivos ==-- Manuel Siccha 

		--total
		select		Fecha_Cierre,count(num_doc)
		from		dbo.clientes_netos_ds
		where		Tipo like '%P%'
		group by	Fecha_Cierre
		


		--genero
			select		Fecha_Cierre,Genero,count(distinct num_doc)
			from		dbo.clientes_netos_ds -- select top 3* from dbo.clientes_netos_ds
			where		Tipo like '%P%' --and Fecha_Cierre in ('2019-01-31','2020-01-31')
			group by	Fecha_Cierre,Genero


		--ruralidad
		--select *  from clientes_netos_ds order by num_doc

		select		a.Fecha_Cierre,b.tipo, count(distinct a.num_doc) Clientes							
		from		clientes_netos_ds a
		left join	distritos_rural_alv				b
		on			a.UBIGEO=b.Ubigeo
		--and			a.Tipo like '%P%'  --and	a.Fecha_Cierre in ('2019-01-31','2020-01-31')
		group by	a.Fecha_Cierre,b.tipo

		--Edad
		if			(object_id('tempdb..#TMPccp')) is not null drop table #TMPccp
		select		EOMONTH(Fecha_Cierre) Fecha_Cierre,Numero_Doc,Fecha_Nac_creacion					--pt0
		into		#TMPccp		--drop table #TMPccp
		from		(select * from [RCC_CD].[DB202502].[dbo].[CCP20250228] -- CAMBIAR (es el año pasado)
					union select * from [RCC_CD].[DB202602].[dbo].[CCP20260228]) a -- CAMBIAR y poner el año actual
		where		Fecha_Cierre in ('20260228','20250228') -- CAMBIAR

		if			(object_id('tempdb..#An_cl_1')) is not null drop table #An_cl_1
		select		Fecha_Cierre,num_doc														--pt1
		into		#An_cl_1	--drop table #An_cl_1
		from		dbo.clientes_netos_ds
		where		Tipo like '%P%'

		if			(object_id('tempdb..#P_AJ_Edad')) is not null drop table #P_AJ_Edad
		select		a.Fecha_Cierre,a.num_doc,													--pt2
					datediff(yy,b.Fecha_Nac_creacion,a.Fecha_Cierre) as Edad		
		into		#P_AJ_Edad --drop table #P_AJ_Edad
		from		#An_cl_1	A
		left join	#TMPccp		B
		on			a.num_doc collate Modern_Spanish_CI_AS=b.Numero_Doc collate Modern_Spanish_CI_AS
		and			eomonth(a.Fecha_Cierre)=eomonth(b.Fecha_Cierre)

		select		Fecha_Cierre,
					case when Edad<='30' then 'MENOR 30'						--pt3
						when Edad>'30' then 'MAYOR 30'
						else  'MAYOR 30'
					end as R_EDAD,count( distinct num_doc) Clientes					
		from		#P_AJ_Edad
		group by	Fecha_Cierre,case when Edad<='30' then 'MENOR 30'
						when Edad>'30' then 'MAYOR 30' 
						else  'MAYOR 30'
					end
		

		--== Seguros ==--

		-- TOTAL --
		select Fecha_Reporte,count(distinct NUM_DOC) NroClientes
		FROM (
			SELECT Fecha_Reporte, NUM_DOC
			FROM intcom.dbo.CCS_FUND_F
			WHERE Fecha_Reporte = '20250531' AND DESC_ESTADO IN ('ACTIVO', 'VIGENTE')  -- CAMBIAR
    
			UNION ALL
    
			SELECT Fecha_Reporte, NUM_DOC
			FROM intcom.dbo.CCS_FUND_f
			WHERE Fecha_Reporte = '20260531' AND DESC_ESTADO IN ('ACTIVO', 'VIGENTE')  -- CAMBIAR
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
    WHERE s.Fecha_Reporte = '20250531'  -- cambiar
    
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
    WHERE s.Fecha_Reporte = '20260531' -- cambiar . La tabla dbo.CCS_FUND_F tiene datos del 2022, la tabla CCS_FUND_F tiene info del 2023 
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

