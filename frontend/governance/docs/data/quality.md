# Calidad del dato

| Control | Dónde | Qué detecta |
|---|---|---|
| **Tablas al corte** (`tablas --verificar`) | todos los reportes | tabla desactualizada o del día inexistente |
| Fecha de corte válida (fin de mes) | `Periodo` en reportes mensuales | corte equivocado |
| Última fecha disponible | `sql_ultima_fecha` en bloques | fuente sin cargar al corte |
| Provisiones ≠ 0 | CMG Mora | carga incompleta de `PROV_PROY_*` |
| Existencia de tabla `PROV_PROY_<fecha>_0` | CMG Mora | proceso previo no corrió |
| Diagnóstico de cruce | Bancarizados | clientes sin match entre RCC y SLC |
| Validaciones de resumen | indicadores_clientes | totales incoherentes |

Pendiente: controles equivalentes para los reportes aún manuales (ver [roadmap](../business/roadmap.md)).
