# Auditoría inicial — 2026-10-06

Alcance: reorganización del repositorio y creación del marco de gobernanza.

| Hallazgo | Detalle | Estado |
|---|---|---|
| Credenciales en texto plano | ver [SEC-001](../../security/findings.md) | Abierto |
| 5 implementaciones de conexión | unificadas en `db.py` | Cerrado |
| Rutas `D:\…` fijas | reemplazadas por `config.DIR_SALIDAS` | Cerrado |
| Carpetas duplicadas en legado | `Reporte_finanzas` vs `Reportes Finanzas-…001` | Documentado ([ADR-0004](../../architecture/adr/ADR-0004-legado-intacto.md)) |
| SQL embebido y sin pruebas en 5 módulos | congelado en la línea base | Deuda registrada |
| SQL sin automatizar | 22 archivos | Roadmap |

Comando de referencia: `python governance/scripts/validar_gobernanza.py --sin-linea-base`.
