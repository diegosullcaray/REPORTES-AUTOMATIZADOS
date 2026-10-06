"""Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar».

Comando: python main.py giovanni-seguros --fecha-corte AAAA-MM-DD
Lógica: T-SQL heredado de docs/LEGADO (fechas fijas convertidas en tokens @@F@@…); el ejecutor común valida
tablas al corte, ejecuta, valida datos y exporta a data/outputs/giovanni_seguros/. Tablas: ver tablas.USO["giovanni-seguros"].
"""

from __future__ import annotations

from ..comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
-- Declaración de variables nativas de SQL Server
DECLARE @tip_cod INT = 7;
DECLARE @cod_rel VARCHAR(50) = '231';
DECLARE @dFechaMax DATE = '@@F@@';
DECLARE @FecJerar DATE = '@@F@@';

WITH cte_a AS (
    SELECT
        b.*,
        ep03.RCODPROD,
        CASE
             WHEN ep03.RCODPROD = 1  THEN 'AGRO'
             WHEN ep03.RCODPROD = 2  THEN 'CC'
             WHEN ep03.RCODPROD = 3  THEN 'CE'
             WHEN ep03.RCODPROD = 4  THEN 'EC'
             WHEN ep03.RCODPROD = 5  THEN 'ICPYME'
             WHEN ep03.RCODPROD = 6  THEN 'PDM'
             WHEN ep03.RCODPROD = 7  THEN 'CONS'
             WHEN ep03.RCODPROD = 8  THEN 'GL'
             WHEN ep03.RCODPROD = 9  THEN 'TFC'
             WHEN ep03.RCODPROD = 10 THEN 'CONV'
             WHEN ep03.RCODPROD = 11 THEN 'HIP'
             WHEN ep03.RCODPROD = 12 THEN 'IC'
             WHEN ep03.RCODPROD = 13 THEN 'MAXI'
             WHEN ep03.RCODPROD = 14 THEN 'OTROS'
             WHEN ep03.RCODPROD = 15 THEN 'PFE'
             WHEN ep03.RCODPROD = 16 THEN 'CFAE'
             WHEN ep03.RCODPROD = 17 THEN 'REACT'
             WHEN ep03.RCODPROD = 18 THEN 'IO'
             WHEN ep03.RCODPROD = 19 THEN 'IN'
             WHEN ep03.RCODPROD = 20 THEN 'INCFAE'
             WHEN ep03.RCODPROD = 21 THEN 'NFAE'
        END AS cod_s
    FROM storage.[com_act].[SDAF002] b
    LEFT JOIN storage.[com_act].RETP001 ep01
        ON ep01.RCODMOD = b.SCODMOD AND ep01.RTIPOPE = b.STIPOPE
    LEFT JOIN storage.[com_act].RETP002 ep02
        ON ep02.RCODMOD = b.SCODMOD AND ep02.RTIPOPE = b.STIPOPE AND ep02.RSUBTIP = b.SSUBTIP
    LEFT JOIN storage.[com_act].RETP003 ep03
        ON ep03.RCODPROD = ISNULL(ep02.RCODPROD, ep01.RCODPROD)
    WHERE b.SFECPRO = @dFechaMax AND b.SCODAGR = 6
),
cte_b AS (
    SELECT
        'Cartera' AS tip,
        CAST(NULL AS INT) AS seg,
        a.RCODPROD,
        CAST(ISNULL(c.RCODSEC, '0') AS VARCHAR(250)) AS scoddescrip,
        c.RDESGRU,
        c.RDESCOR,
        NULLIF(c.RDESTER, 'SIN ASIGNAR') AS rdester,
        NULLIF(c.RDESSEC, 'NO ENCONTRADO') AS descripcion,
        SUM(a.SNUMOPE) AS snumope,
        a.cod_s
    FROM cte_a a
    LEFT JOIN storage.[ref].WJERCOR03 c
        ON a.SCODSEC = c.RCODSEC AND a.SFECPRO = c.RFECPRO AND c.RINDFEC = 'ACTUAL'
        AND CASE
                WHEN @tip_cod = 15 THEN ISNULL(CAST(c.RCODTER AS VARCHAR(250)), '9999')
                WHEN @tip_cod = 14 THEN CAST(c.RCODCOR AS VARCHAR(250))
                WHEN @tip_cod = 13 THEN CAST(c.RCODGRU AS VARCHAR(250))
                WHEN @tip_cod = 11 THEN CAST(c.RCODUNI AS VARCHAR(250))
                ELSE '1'
            END = CASE WHEN @tip_cod = 7 THEN '1' ELSE @cod_rel END
    GROUP BY a.RCODPROD, CAST(ISNULL(c.RCODSEC, '0') AS VARCHAR(250)), c.RDESGRU, c.RDESCOR, c.RDESTER, c.RDESSEC, a.cod_s
),
cte_seg AS (
    SELECT
        b.*,
        ep03.RCODPROD,
        CASE
            WHEN b.SCODSEG = 802 THEN 'S_PC'
            WHEN b.SCODSEG IN (806,815,825) THEN 'S_AG'
            WHEN b.SCODSEG IN (803,817) THEN 'S_MC'
            WHEN b.SCODSEG IN (200,220,230) THEN 'S_MR'
            WHEN b.SCODSEG IN (814,828) THEN 'S_ONCO'
        END AS cod_s
    FROM storage.[com_seg].SDSF001 b
    LEFT JOIN storage.[com_act].RETP001 ep01
        ON ep01.RCODMOD = b.SCODMOD AND ep01.RTIPOPE = b.STIPOPE
    LEFT JOIN storage.[com_act].RETP002 ep02
        ON ep02.RCODMOD = b.SCODMOD AND ep02.RTIPOPE = b.STIPOPE AND ep02.RSUBTIP = b.SSUBTIP
    LEFT JOIN storage.[com_act].RETP003 ep03
        ON ep03.RCODPROD = ISNULL(ep02.RCODPROD, ep01.RCODPROD)
    WHERE b.SFECPRO = @dFechaMax AND b.SCODAGR = 13
),
cte_seg_pc_jer AS (
    SELECT
        'Seguro' AS tip,
        a.SCODSEG AS seg,
        a.RCODPROD,
        CAST(ISNULL(c.RCODSEC, '0') AS VARCHAR(250)) AS scoddescrip,
        c.RDESGRU,
        c.RDESCOR,
        NULLIF(c.RDESTER, 'SIN ASIGNAR') AS rdester,
        NULLIF(c.RDESSEC, 'NO ENCONTRADO') AS descripcion,
        SUM(a.SNUMPLZ) AS snumope,
        a.cod_s
    FROM cte_seg a
    LEFT JOIN storage.[ref].WJERCOR03 c
        ON a.SCODSEC = c.RCODSEC AND a.SFECPRO = c.RFECPRO AND c.RINDFEC = 'ACTUAL'
        AND CASE
                WHEN @tip_cod = 15 THEN ISNULL(CAST(c.RCODTER AS VARCHAR(250)), '9999')
                WHEN @tip_cod = 14 THEN CAST(c.RCODCOR AS VARCHAR(250))
                WHEN @tip_cod = 13 THEN CAST(c.RCODGRU AS VARCHAR(250))
                WHEN @tip_cod = 11 THEN CAST(c.RCODUNI AS VARCHAR(250))
                ELSE '1'
            END = CASE WHEN @tip_cod = 7 THEN '1' ELSE @cod_rel END
    GROUP BY a.SCODSEG, a.RCODPROD, CAST(ISNULL(c.RCODSEC, '0') AS VARCHAR(250)), c.RDESGRU, c.RDESCOR, c.RDESTER, c.RDESSEC, a.cod_s
),
cte_result AS (
    SELECT * FROM cte_b
    UNION ALL
    SELECT * FROM cte_seg_pc_jer
),
cte_metas AS (
    SELECT DISTINCT
        CAST(c.RCODSEC AS VARCHAR(250)) AS rcod,
        SUM(v.HVALVAR) OVER(PARTITION BY c.RCODSEC) AS metaseg
    FROM storage.[com].[VDMCOM01] v
    LEFT JOIN storage.[ref].WJERCOR03 c
        ON v.HCODREL = CAST(c.RCODSEC AS VARCHAR(250))
        AND c.RINDFEC = 'ACTUAL' AND c.RFECPRO = @FecJerar
    WHERE v.HTIPCOD = '2'
      AND v.HCODVAR = 5001
      AND v.HFECPRO = EOMONTH(@dFechaMax)
),
cte_agregacion_seguros AS (
    -- ÚNICO ESCANEO CONDICIONAL PARA T-SQL
    SELECT
        scoddescrip,
        SUM(CASE WHEN RCODPROD IN(4,2,5) AND seg IN(200,802,803) THEN snumope ELSE 0 END) AS t_seg_pyme_cc,
        SUM(CASE WHEN RCODPROD IN(4,2,5) AND seg = 200 THEN snumope ELSE 0 END) AS t_seg_pyme_cc_mr,
        SUM(CASE WHEN RCODPROD IN(4,2,5) AND seg = 803 THEN snumope ELSE 0 END) AS t_seg_pyme_cc_mc,
        SUM(CASE WHEN RCODPROD IN(4,2,5) AND seg = 802 THEN snumope ELSE 0 END) AS t_seg_pyme_cc_pc,

        SUM(CASE WHEN RCODPROD = 1 AND seg IN(802,200,803,806,815) THEN snumope ELSE 0 END) AS t_seg_agro_t,
        SUM(CASE WHEN RCODPROD = 1 AND seg IN(200,220,230) THEN snumope ELSE 0 END) AS agro_multir,
        SUM(CASE WHEN RCODPROD = 1 AND seg = 803 THEN snumope ELSE 0 END) AS agro_multic,
        SUM(CASE WHEN RCODPROD = 1 AND seg = 802 THEN snumope ELSE 0 END) AS agro_pc,
        SUM(CASE WHEN RCODPROD = 1 AND seg IN(806,815) THEN snumope ELSE 0 END) AS agro_agro,

        SUM(CASE WHEN RCODPROD = 7 AND seg IN(802,803) THEN snumope ELSE 0 END) AS t_seg_consumo_t,
        SUM(CASE WHEN RCODPROD = 7 AND seg = 803 THEN snumope ELSE 0 END) AS mc_consumo,
        SUM(CASE WHEN RCODPROD = 7 AND seg = 802 THEN snumope ELSE 0 END) AS pc_consumo,

        SUM(CASE WHEN RCODPROD = 3 AND seg = 802 THEN snumope ELSE 0 END) AS t_seg_ce_t,

        SUM(CASE WHEN RCODPROD = 18 AND seg IN(200,803,802) THEN snumope ELSE 0 END) AS t_seg_io_t,
        SUM(CASE WHEN RCODPROD = 18 AND seg IN(200,220,230) THEN snumope ELSE 0 END) AS mr_io,
        SUM(CASE WHEN RCODPROD = 18 AND seg = 803 THEN snumope ELSE 0 END) AS mc_io,
        SUM(CASE WHEN RCODPROD = 18 AND seg = 802 THEN snumope ELSE 0 END) AS pc_io,

        SUM(CASE WHEN RCODPROD = 18 AND seg = 814 THEN snumope ELSE 0 END) AS t_seg_onco
    FROM cte_result
    WHERE tip = 'Seguro'
    GROUP BY scoddescrip
),
cte_pivot_general AS (
    SELECT
        scoddescrip, descripcion, rdesgru, rdescor, rdester,
        SUM(CASE WHEN cod_s = 'AGRO' THEN snumope ELSE 0 END) AS agro,
        SUM(CASE WHEN cod_s = 'CC' THEN snumope ELSE 0 END) AS cc,
        SUM(CASE WHEN cod_s = 'CE' THEN snumope ELSE 0 END) AS ce,
        SUM(CASE WHEN cod_s = 'EC' THEN snumope ELSE 0 END) AS ec,
        SUM(CASE WHEN cod_s = 'ICPYME' THEN snumope ELSE 0 END) AS icpyme,
        SUM(CASE WHEN cod_s = 'CONS' THEN snumope ELSE 0 END) AS cons,
        SUM(CASE WHEN cod_s = 'IO' THEN snumope ELSE 0 END) AS io,
        SUM(CASE WHEN cod_s = 'S_PC' THEN snumope ELSE 0 END) AS s_pc,
        SUM(CASE WHEN cod_s = 'S_AG' THEN snumope ELSE 0 END) AS s_ag,
        SUM(CASE WHEN cod_s = 'S_MC' THEN snumope ELSE 0 END) AS s_mc,
        SUM(CASE WHEN cod_s = 'S_MR' THEN snumope ELSE 0 END) AS s_mr,
        SUM(CASE WHEN cod_s = 'S_ONCO' THEN snumope ELSE 0 END) AS s_onco
    FROM cte_result
    GROUP BY scoddescrip, descripcion, rdesgru, rdescor, rdester
)
SELECT
    a.scoddescrip, a.descripcion, a.rdesgru, a.rdescor, a.rdester,

    (ISNULL(a.io,0) + ISNULL(a.ce,0) + ISNULL(a.cons,0) + ISNULL(a.agro,0) + ISNULL(a.ec,0) + ISNULL(a.cc,0) + ISNULL(a.icpyme,0)) AS total_ope,
    (ISNULL(a.s_pc,0) + ISNULL(a.s_ag,0) + ISNULL(a.s_mc,0) + ISNULL(a.s_mr,0) + ISNULL(a.s_onco,0)) AS total_seg,

    CASE
        WHEN (ISNULL(a.io,0) + ISNULL(a.ce,0) + ISNULL(a.cons,0) + ISNULL(a.agro,0) + ISNULL(a.ec,0) + ISNULL(a.cc,0) + ISNULL(a.icpyme,0)) = 0 THEN 0
        ELSE CAST((ISNULL(a.s_pc,0) + ISNULL(a.s_ag,0) + ISNULL(a.s_mc,0) + ISNULL(a.s_mr,0) + ISNULL(a.s_onco,0)) AS FLOAT) /
             (ISNULL(a.io,0) + ISNULL(a.ce,0) + ISNULL(a.cons,0) + ISNULL(a.agro,0) + ISNULL(a.ec,0) + ISNULL(a.cc,0) + ISNULL(a.icpyme,0))
    END AS p_pene_total,

    ISNULL(a.s_mr,0) AS multiriesgo, ISNULL(a.s_mc,0) AS multicredito, ISNULL(a.s_pc,0) AS prot_cuota, ISNULL(a.s_ag,0) AS agro_seguro, ISNULL(a.s_onco,0) AS onco,
    ISNULL(a.ec,0) AS emp_confia, ISNULL(a.cc,0) AS const_confia, ISNULL(a.agro,0) AS agro_operacion, ISNULL(a.cons,0) AS consumo, ISNULL(a.ce,0) AS cred_educ,
    ISNULL(a.io,0) AS ini_ofici,

    ISNULL(b.metaseg, 0) AS metaseg,
    CASE WHEN ISNULL(b.metaseg,0) = 0 THEN 0 ELSE (ISNULL(a.s_pc,0) + ISNULL(a.s_ag,0) + ISNULL(a.s_mc,0) + ISNULL(a.s_mr,0)) / b.metaseg END AS avance,

    (ISNULL(a.ec,0) + ISNULL(a.cc,0) + ISNULL(a.icpyme,0)) AS t_ope_pyme_cc,
    agg.t_seg_pyme_cc, agg.t_seg_pyme_cc_mr, agg.t_seg_pyme_cc_mc, agg.t_seg_pyme_cc_pc,

    ISNULL(a.agro,0) AS t_ope_agro,
    agg.t_seg_agro_t,
    CASE WHEN ISNULL(a.agro,0) = 0 THEN 0 ELSE CAST(agg.t_seg_agro_t AS FLOAT) / a.agro END AS pen_agro,
    agg.agro_multir, agg.agro_multic, agg.agro_pc, agg.agro_agro

FROM cte_pivot_general a
LEFT JOIN cte_metas b ON a.scoddescrip = b.rcod
LEFT JOIN cte_agregacion_seguros agg ON a.scoddescrip = agg.scoddescrip;
"""

REPORTE = ReporteLote(
    comando="giovanni-seguros",
    descripcion='Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar»',
    frecuencia="mensual",
    alias="slc",
    sql=SQL,
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
