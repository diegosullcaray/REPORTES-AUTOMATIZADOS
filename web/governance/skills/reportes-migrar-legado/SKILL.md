---
name: reportes-migrar-legado
description: Cómo pasar un reporte manual de docs/LEGADO a un reporte automatizado. Usar cuando se toma un procedimiento manual del legado.
---

# Migrar un reporte del legado

1. Lee en `docs/LEGADO/` la carpeta completa: `NOTAS.docx` (también transcrito en [procedimientos](../../docs/business/procedimientos_manuales_legado.md)), SQL, PDF de correo, plantilla Excel.
2. Llena la [ficha de reporte](../../docs/templates/report-spec-template.md) citando cada regla a su fuente.
3. Copia el T-SQL del legado a un módulo `ReporteLote` ([reportes-ejecutor](../reportes-ejecutor/SKILL.md)) reemplazando cada fecha fija por un token (`@@F@@`…); verifica contra el original.
4. Implementa el módulo siguiendo [reportes-arquitectura-modulos](../reportes-arquitectura-modulos/SKILL.md).
5. Reproduce la salida manual de un mes conocido y compara cifras (evidencia en `docs/evidence/`).
6. Registra, regenera inventario, `verificar.py`.
7. Registra el reporte y sus tablas (`registro.py`, `tablas.py`) y actualiza el [catálogo](../../docs/business/domain-catalog.md).

No edites ni muevas el original ([ADR-0004](../../docs/architecture/adr/ADR-0004-legado-intacto.md)).
