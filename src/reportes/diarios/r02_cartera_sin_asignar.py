"""Cartera sin asignar (diario, legado «02 Cartera sin asignar»): cartera por sectorista/territorio sin asignación.

Comando: python main.py cartera-sin-asignar --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/cartera_sin_asignar/. Tablas: ver tablas.USO["cartera-sin-asignar"].
"""

from __future__ import annotations

from ..comun.ejecutor import Hoja, ReporteLote, correr
from ..comun.excel import Resumen
from ..comun.entrega_correo import EntregaCorreoResumen

SQL = r"""
USE [storage]
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


--INGRESAR FECHA
DECLARE @FecRep DATE = '@@F_ISO@@'



IF OBJECT_ID('tempdb..#SECVAL') IS NOT NULL
DROP TABLE #SECVAL;

SELECT SCODSEC INTO #SECVAL FROM storage.[com_act].SDAS001 WHERE SFECPRO= @FecRep
EXCEPT
SELECT RCODSEC FROM storage.ref.FJERCOR02(@FecRep)

CREATE CLUSTERED INDEX IX_Temp_Vendedor ON #SECVAL(SCODSEC);

;with cta_a as (
    SELECT
        HSALCAPMN, HCODSEC, HSUCCLI, HASEOPER, HCTACLI, HDESCLI, HCODOPE, HCODMOD, HTIPOPE, HSUBTIP
    FROM storage.[com_act].HCDA001 WHERE HFECPRO = @FecRep
)
SELECT
    'FC' NIVEL
    ,A.HASEOPER Asesor_Operativo
    ,A.HCTACLI Cuenta_Cliente
    ,A.HDESCLI Nom_Cliente
    ,A.HCODOPE Operacion
    ,A.HSALCAPMN Saldo_Capital
    ,_P3.RDESGRU02 as Grupo
    ,ISNULL(C.RDESTER,'NULL') Territorio
    ,C.RDESCOR Corredor
    ,C.RDESAGE Agencia_Cli
    ,B.RDESUNI Unidad_Negocio
FROM cta_a A
LEFT JOIN (select * from storage.ref.FJERCOR02(@FecRep)) B on A.HCODSEC = B.RCODSEC
LEFT JOIN storage.ref.vjercor03 C on A.HSUCCLI = C.RCODAGE
LEFT JOIN STORAGE.[COM_ACT].RETP002 _P2 ON A.HCODMOD=_P2.RCODMOD AND A.HTIPOPE=_P2.RTIPOPE AND _P2.RSUBTIP=A.HSUBTIP
LEFT JOIN STORAGE.[COM_ACT].RETP001 _P1 ON A.HCODMOD=_P1.RCODMOD AND A.HTIPOPE=_P1.RTIPOPE
LEFT JOIN STORAGE.[COM_ACT].RETP003 _P3 ON ISNULL(_P2.RCODPROD,_P1.RCODPROD)=_P3.RCODPROD
WHERE A.HASEOPER IN ('','--') OR A.HASEOPER IS NULL
OR EXISTS ( SELECT 1  FROM #SECVAL t1 WHERE t1.SCODSEC=A.HASEOPER)
ORDER BY C.RCODTER, C.RCODCOR, C.RDESAGE
DROP TABLE #SECVAL


--select DISTINCT RCODAGE,RDESAGE from storage.ref.vjercor04 where rdester='SUR 1.'
--select DISTINCT RCODAGE from storage.ref.vjercor03 where rdester='SUR 1'
"""

REPORTE = ReporteLote(
    comando="cartera-sin-asignar",
    descripcion='Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación',
    frecuencia="diaria",
    servidor="mish",
    base="storage",
    sql=SQL,
    archivo="Cartera-Sin asignar-{AAAA-MM-DD}",
    hojas=(Hoja("DATA_MIS_v2"),),
    resumenes=(Resumen("RESUMEN_v2", ("NIVEL", "Grupo", "Territorio", "Corredor", "Agencia_Cli"), "Saldo_Capital",
                      "TERRITORIO POR CLIENTE", "SALDO CARTERA - MIS"),),
    entrega=EntregaCorreoResumen(),   # correo con la tabla resumen (imagen) y el Excel: prueba -> conforme -> todos
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
