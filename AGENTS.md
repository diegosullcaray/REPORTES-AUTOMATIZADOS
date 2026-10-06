# Reglas base — Reportes Automatizados

Python + 3 bases SQL Server (`dw_raw`, `rcc`, `slc`). Marco completo: [governance/readme.md](governance/readme.md).

1. **Gana el código** cuando documentación y código discrepan; se corrige el documento.
2. **Conexiones**: solo vía `src/reportes/db.py` con un alias. Nunca `pyodbc.connect`/`create_engine` en otro sitio.
3. **Secretos**: solo `.env`. Jamás en código, SQL ni docs. Si aparecen en `docs/LEGADO`, no se copian; se reportan en `governance/docs/security/findings.md`.
4. **`docs/LEGADO` es solo lectura**; el código vivo está en `src/` y `sql/`; datos locales en `data/inputs/` (entradas) y `data/outputs/` (salidas), no versionados.
5. **SQL** en `sql/` con parámetros enlazados; **entradas** en `data/inputs/`, **salidas** en `data/outputs/`.
6. **Vacío ≠ error**; variable crítica en 0 ⇒ abortar.
7. Cada reporte: `main(argv) -> int`, registrado en `registro.py`, con `tests/test_<modulo>.py`.
8. Antes de commitear: `python governance/scripts/verificar.py`. No regenerar la línea base para destrabar.
9. Agentes: [governance/agents/README.md](governance/agents/README.md) · Skills: `governance/skills/`.
