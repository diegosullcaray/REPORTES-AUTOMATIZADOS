# REPORTES-AUTOMATIZADOS

Reportes de Financiera Confianza en Python, **ejecutados por ti bajo demanda** (sin tareas programadas), con una interfaz web opcional para gestionarlos desde el navegador.

> **Regla que manda sobre todo:** cuando la documentación y el código discrepan, gana el código y se corrige el documento. Reglas del repositorio: [AGENTS.md](AGENTS.md).

## Qué hay en cada carpeta

| Carpeta | Qué es | Empieza por |
|---|---|---|
| [`backend/`](backend/README.md) | Motor de reportes en Python (conexión a SQL Server, validación de tablas al corte, Excel, correo) y la API de la web | [backend/README.md](backend/README.md) |
| [`frontend/`](frontend/README.md) | Interfaz web (Next.js + shadcn, estética Dokploy) con login, reportes y ejecuciones | [frontend/README.md](frontend/README.md) |
| [`governance/`](governance/readme.md) | Marco de gobernanza: agentes, skills, documentación, runbooks y compuertas (`verificar.py`) | [governance/readme.md](governance/readme.md) |
| `docs/LEGADO/` | Archivo histórico, solo lectura | — |

## Arranque rápido

```bat
:: Motor: ver backend/README.md (instalación, .env, reportes)
cd backend
python main.py listar

:: Web: API en una terminal y web en otra (ver frontend/README.md)
cd backend && python -m uvicorn api.app:app --app-dir src --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

## Antes de commitear

```bat
python governance\scripts\verificar.py     :: gobernanza + inventarios + pruebas del backend
```

En `frontend/`: `npm test`, `npx tsc --noEmit`, `npx eslint src` y `npx next build`. **No regeneres la línea base para destrabar** una compuerta ([ADR-0003](governance/docs/architecture/adr/ADR-0003-linea-base-de-gobernanza.md)).

## Documentación

Todo el marco está en [`governance/`](governance/readme.md): [runbooks](governance/docs/development/runbooks/README.md), [catálogo de reportes](governance/docs/business/domain-catalog.md), [seguridad](governance/docs/security/README.md) y [decisiones de diseño (ADR)](governance/docs/architecture/decision-records.md).
