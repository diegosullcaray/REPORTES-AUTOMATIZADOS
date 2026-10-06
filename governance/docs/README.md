# Documentación — Reportes Automatizados

Entorno Python que automatiza los reportes de Financiera Confianza sobre 3 servidores SQL Server (`mish`, `slc`, `rcc`); cada reporte usa su propia base de datos.

| Área | Responsabilidad |
|---|---|
| [`data/`](./data/README.md) | **Gobierno del dato** (eje): glosario, catálogo, contratos, linaje, calidad, clasificación, responsabilidades |
| [`architecture/`](./architecture/README.md) | Cómo está construido: capas, flujo, inventario, decisiones |
| [`business/`](./business/README.md) | Reportes, solicitantes, procedimientos heredados, roadmap |
| [`development/`](./development/README.md) | Setup, convenciones, guía de nuevo reporte, pruebas, compuertas |
| [`security/`](./security/README.md) | Secretos, amenazas, remediación |
| [`templates/`](./templates/README.md) | Plantillas de trabajo |
| [`evidence/`](./evidence/README.md) | Auditorías e incidentes |
| [`onboarding.md`](./onboarding.md) | Primer día y ruta de lectura |

El archivo histórico del que parte todo está en `docs/LEGADO/` (raíz del repo, solo lectura).

## Por dónde empezar

| Si quieres… | Lee |
|---|---|
| Entender el producto | [Visión](./business/product-vision.md) |
| Ver qué reportes existen y cuáles faltan | [Catálogo de reportes](./business/domain-catalog.md) |
| Saber a qué base conecta cada cosa | [Contrato de conexiones](./data/contracts/conexiones-bd.md) |
| Agregar un reporte | [Guía de nuevo reporte](./development/report-creation-guide.md) |
| **Ejecutar un reporte / cierre de mes** | [Runbooks](./development/runbooks/README.md) |
| **Saber qué tabla usa cada reporte** | [Inventario de tablas](./data/tables-inventory.md) |
| Rastrear una cifra | [Linaje](./data/lineage.md) |
| Ver el estado generado del código | [Inventario](./architecture/module-inventory.md) |
