# Setup

Requisitos: Python 3.11+, **ODBC Driver 17 for SQL Server**, acceso de red a los 3 servidores (`MISHWBDDES01`, `172.24.2.213` y `172.20.0.70`) y, solo para la web, **Node 20+**.

## Backend (motor y API)

```bash
cd backend
python -m venv env && env\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env          # credenciales y fecha de corte (no se versiona)
# en .env define la fecha de corte: FECHA_CORTE_MENSUAL=AAAA-MM-DD (y FECHA_CORTE_DIARIA para los diarios)
python main.py probar-conexiones
cd .. && python governance/scripts/verificar.py   # desde la raíz
```

Para entrar a la web define también `WEB_USUARIO` y `WEB_CLAVE` en `backend/.env` ([ADR-0012](../architecture/adr/ADR-0012-acceso-a-la-web-y-ajustes-editables.md)).

## Frontend (web)

```bash
cd frontend
npm install
npm run dev
```

Arranque completo de la web (API + web) y qué hace cada pantalla: [interfaz web](./runbooks/interfaz-web.md).

Si no tienes acceso a producción (`slc`), solicita a quien administra la BD que ejecute el SQL y te envíe el resultado, o que habilite tu usuario.
