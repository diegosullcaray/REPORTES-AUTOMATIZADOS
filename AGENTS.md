# Reglas base — Reportes Automatizados

Repo en dos partes: `backend/` (Python, API y motor de reportes) y `frontend/` (web Next.js). Los comandos de Python se ejecutan dentro de `backend/`.

Python + 3 servidores SQL Server (`mish`, `slc`, `rcc`); **la base de datos la elige cada reporte** (`base=`), no el `.env`. Marco completo: [governance/readme.md](governance/readme.md).

1. **Gana el código** cuando documentación y código discrepan; se corrige el documento.
2. **Conexiones**: solo vía `backend/src/reportes/db.py` indicando servidor y base. Nunca `pyodbc.connect`/`create_engine` en otro sitio.
3. **Secretos**: solo `.env`. Jamás en código, SQL ni docs. Si aparecen en `docs/LEGADO`, no se copian; se reportan en `governance/docs/security/findings.md`.
4. **`docs/LEGADO` es solo lectura**; el código vivo está en `backend/src/` (el T-SQL va incrustado en cada reporte; **no hay carpeta `sql/`**); datos locales en `backend/data/inputs/` (entradas) y `backend/data/outputs/` (salidas), no versionados.
5. **Reporte = módulo `.py`** con `ReporteLote`: fechas solo por tokens (`@@F@@`…), nunca literales; el ejecutor valida tablas al corte y datos, y exporta a Excel; **entradas** en `backend/data/inputs/`, **salidas** en `backend/data/outputs/`.
6. **Los reportes los ejecuta una persona bajo demanda** (sin tareas programadas). La fecha de corte sale de `--fecha-corte` o del `.env` (`FECHA_CORTE_MENSUAL` / `FECHA_CORTE_DIARIA`), nunca de una constante en el código.
7. **Orden del legado**: cada reporte conserva el número y el responsable (Piero/Erick) de su carpeta en `docs/LEGADO`: módulo `r<NN>_<nombre>.py` y salida `backend/data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>/`.
8. **Correo**: la cuenta MIS, su contraseña y el webhook solo en `.env`. Antes de enviar a la lista siempre se envía una prueba a `CORREO_PRUEBA` y se espera el conforme del usuario.
9. **Vacío ≠ error**; variable crítica en 0 ⇒ abortar.
10. Cada reporte: `main(argv) -> int`, registrado en `registro.py`, con `backend/tests/test_<modulo>.py`.
11. Antes de commitear: `python governance/scripts/verificar.py`. No regenerar la línea base para destrabar.
12. Agentes: [governance/agents/README.md](governance/agents/README.md) · Skills: `governance/skills/`.
