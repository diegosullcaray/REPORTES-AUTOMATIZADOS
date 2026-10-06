# Gobierno del dato

Los reportes alimentan decisiones de Riesgos, Finanzas y la Gerencia. Un script roto se ve; **una cifra equivocada no**. Un reporte puede ejecutar sin error y entregar el corte del mes equivocado, o duplicar asesores, y nadie lo nota hasta que llega al correo del gerente.

## Documentos

| Documento | Responde a |
|---|---|
| [Glosario](./glossary.md) | ¿Qué significa este término? |
| [Catálogo](./catalog.md) | ¿Qué datos se consumen y de qué base salen? |
| [Inventario de tablas](./tables-inventory.md) | **¿Qué tabla usa cada reporte y a quién pedir que la actualice?** (generado) |
| [Contratos](./contracts/README.md) | ¿Cuál es la forma exacta del dato en el borde? |
| [Linaje](./lineage.md) | ¿Por dónde pasó esta cifra? |
| [Calidad](./quality.md) | ¿Cómo sé que es correcta? |
| [Clasificación](./classification.md) | ¿Qué cuidado requiere? |
| [Responsabilidades](./stewardship.md) | ¿Quién decide sobre este dato? |

## Principios

1. **Este proyecto no es fuente de verdad.** Lee de las bases y presenta; no corrige negocio con transformaciones silenciosas.
2. **Un reporte sin contrato no se automatiza.** Fecha de corte, base, tablas, solicitante y regla de negocio se documentan antes (ver [ficha de reporte](../templates/report-spec-template.md)).
3. **Vacío y error son estados distintos.** `Castigos` vacío puede ser válido; una consulta fallida no. Nunca se confunden.
4. **Si una variable crítica es cero, se aborta.** Ejemplo vigente: CMG Mora no genera INSERTs si provisiones = 0.
5. **Credenciales solo en `.env`.** Ver [seguridad](../security/README.md).
6. **Toda cifra se rastrea hasta su origen**: base, tabla, fecha de corte, versión de SQL.
7. **Lo que se puede derivar del código, se deriva** ([inventario generado](../architecture/module-inventory.md)).

## Las tres preguntas antes de entregar un dato

```text
¿QUÉ?      reporte + SQL versionado         → identifica la consulta
¿DE DÓNDE? alias de BD (dw_raw|rcc|slc) + tabla  → delimita el origen
¿DE CUÁNDO? fecha de corte                  → fija el momento (fin de mes, día hábil previo, lunes→sábado)
```
