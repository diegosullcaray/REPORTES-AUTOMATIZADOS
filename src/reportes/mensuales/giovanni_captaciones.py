"""Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones.

Comando: python main.py giovanni-captaciones --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/giovanni_captaciones/. Tablas: ver tablas.USO["giovanni-captaciones"].
"""

from __future__ import annotations

from ..comun.ejecutor import ReporteLote, correr

SQL = r"""
use storage;
go
declare @date date='@@F_ISO@@'
/*
select * from storage.[com_pas].[sdps010]
where SFECPRO='20230831' and SCODAGR=8
*/
;with cte_a as (
select * from storage.[com_pas].[sdps013]
where SFECPRO=@date and SCODAGR=8
),
cte_aa as (
select p.RDESCPROD02,b.*
from cte_a b
left join storage.[com_pas].[RETP001] P     --select * from storage.[com_pas].[RETP001]
on P.RCODMOD=B.SSBMOD and P.RTIPOPE=B.SSBTOPE
)  ,
CTE_BB AS (
SELECT RDESCPROD02,SSUCCLI,SUM(SSALMN)SSALMN
FROM cte_aa
GROUP BY RDESCPROD02,SSUCCLI
)
,
CTE_B AS (
select   DISTINCT b.RCODAGEH, b.RDESAGEH  RDESAGEH, a.RDESCPROD02, a.SSALMN   ,ISNULL(b.RDESMAT,'sin asignar')RDESMAT,
isnull(b.RDESMAC,'sin asignar')RDESMAC,isnull(b.RDESTER ,'sin asignar')RDESTER
from CTE_BB a
LEFT join  storage.ref.VJERCOR04 b  --select * from  storage.ref.VJERCOR04 where rcodage=1
on a.SSUCCLI=b.RCODAGE
)
SELECT * FROM CTE_B



-- Saldo Medio

USE storage;
GO
DECLARE @date DATE = '@@F@@';
;WITH cte_a AS (
    SELECT *
    FROM storage.com_pas.wjas004
    WHERE (
            HTIPCOD = 4
            OR
            (HTIPCOD = 16 AND HCODREL IN ('98', '136', '198', '216'))
          )
      AND HFECPRO = @date
)
SELECT DISTINCT
    a.HFECPRO,
    b.RDESAGEH,
    a.RDESCPROD02,
    a.HSALMEDMN
FROM cte_a a
INNER JOIN storage.ref.VJERCOR04 b
    ON a.HCODREL = b.RCODAGE  -- Recuerda verificar si es RCODAGE o RCODAGEH
ORDER BY a.HFECPRO ASC;
"""

REPORTE = ReporteLote(
    comando="giovanni-captaciones",
    descripcion='Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones',
    frecuencia="mensual",
    servidor="mish",
    base="storage",
    sql=SQL,
    archivo="Saldo Medio y Puntual Captaciones_{AAAAMMDD}",
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
