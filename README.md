# REPORTES-AUTOMATIZADOS

Reportes de Financiera Confianza en Python, **ejecutados por ti bajo demanda** (no hay tareas programadas), sobre 3 servidores SQL Server (`mish`, `slc`, `rcc`); cada reporte elige su base de datos.

- Gobernanza (estructura, agentes, skills, docs, compuertas): **[governance/readme.md](governance/readme.md)**
- Reglas para agentes: [AGENTS.md](AGENTS.md)

```bash
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env                     # completar credenciales
# en .env: FECHA_CORTE_MENSUAL=AAAA-MM-DD / FECHA_CORTE_DIARIA=AAAA-MM-DD
python main.py listar
python main.py <reporte>                 # usa la fecha de corte del .env (o --fecha-corte AAAA-MM-DD)
python main.py probar-conexiones
python governance/scripts/verificar.py   # compuertas antes de cada commit
```
