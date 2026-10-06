# REPORTES-AUTOMATIZADOS

Automatización en Python de los reportes de Financiera Confianza sobre 3 bases de datos (`dw_raw`, `rcc`, `slc`).

- Gobernanza (estructura, agentes, skills, docs, compuertas): **[governance/readme.md](governance/readme.md)**
- Reglas para agentes: [AGENTS.md](AGENTS.md)

```bash
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env                     # completar credenciales
python main.py listar
python main.py probar-conexiones
python governance/scripts/verificar.py   # compuertas antes de cada commit
```
