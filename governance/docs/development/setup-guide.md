# Setup

Requisitos: Python 3.11+, **ODBC Driver 17 for SQL Server**, acceso de red a 172.20.0.70 y 172.24.2.213.

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env          # credenciales y fecha de corte (no se versiona)
# en .env define la fecha de corte: FECHA_CORTE_MENSUAL=AAAA-MM-DD (y FECHA_CORTE_DIARIA para los diarios)
python main.py probar-conexiones
python governance/scripts/verificar.py
```

Si no tienes acceso a producción (`slc`), solicita a quien administra la BD que ejecute el SQL y te envíe el resultado, o que habilite tu usuario.
