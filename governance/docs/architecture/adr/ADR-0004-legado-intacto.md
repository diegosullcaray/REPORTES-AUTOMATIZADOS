# ADR-0004: `docs/LEGADO` se conserva intacto

- Estado: Vigente · Fecha: 2026-10-06

## Decisión
El archivo histórico no se edita ni se mueve. El código vivo es una copia normalizada (snake_case, sin espacios) en `sql/`, `src/` y `plantillas/`. Duplicados detectados en `HEREDADO DE ERICK` (`Reporte_finanzas` parcial vs `Reportes Finanzas-…001` completo): se usó la completa.

## Consecuencias
El legado sirve de especificación ([migrador](../../../agents/07-migrador-legado.md)). Contiene credenciales históricas: ver [hallazgos](../../security/findings.md).
