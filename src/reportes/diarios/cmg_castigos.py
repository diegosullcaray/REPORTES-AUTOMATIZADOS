"""CMG Mora · recuperación de castigos 12M (SRECCAST12M): suma de SDAS005 en los últimos 11 cierres.

Comando: python main.py cmg-castigos --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/cmg_castigos/. Tablas: ver tablas.USO["cmg-castigos"].
"""

from __future__ import annotations

from ..comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
USE storage
GO

DECLARE @FecRep date = DATEADD(DAY, 1, '@@F_ISO@@')
PRINT @FecRep

SELECT TOP 11 RFEC INTO #RFEC
FROM storage.ref.RCALEN001
WHERE RCIEBT = 1 AND RFEC < @FecRep
ORDER BY RFEC DESC

SELECT SUM(SSRECUMN) SRECCAST12M
FROM storage.[com_act].[SDAS005]
WHERE SFECPRO IN (SELECT RFEC FROM #RFEC) AND SCODAGR = 1

DROP TABLE #RFEC
"""

REPORTE = ReporteLote(
    comando="cmg-castigos",
    descripcion='CMG Mora · recuperación de castigos 12M (SRECCAST12M): suma de SDAS005 en los últimos 11 cierres',
    frecuencia="diaria",
    alias="slc",
    sql=SQL,
    hojas=(Hoja("Castigos 12M"),),
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
