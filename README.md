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
python iniciar.py                  :: API (127.0.0.1:8000) + web (http://localhost:3000), con el navegador abierto
```

Un solo comando levanta el **backend** y el **frontend**, muestra los dos registros en una terminal (`[api]` y `[web]`), espera a que respondan y abre el navegador. **Ctrl+C** detiene los dos. Solo necesita Python y Node 20+; usa el entorno `backend/env` y, la primera vez, instala las dependencias de la web (`npm install`).

| Opción | Para qué |
|---|---|
| `--prod` | compila y sirve la web (`npm run build` + `npm start`) en vez del modo desarrollo |
| `--sin-navegador` | no abre el navegador |
| `--puerto-api 8100` · `--puerto-web 3100` | usar otros puertos si los de por defecto están ocupados |

Antes de la primera vez: crea el entorno y el `.env` del backend ([instalación](backend/README.md#2-instalación-paso-a-paso-primera-vez)) y define en `backend/.env` `WEB_USUARIO` y `WEB_CLAVE` para poder iniciar sesión. Si dice que un puerto está en uso, ya hay una API o una web corriendo: ciérralas (Ctrl+C en su terminal) y vuelve a lanzar.

Para trabajar solo con el motor, sin web: `cd backend` y `python main.py listar` (guía completa en [backend/README.md](backend/README.md)). Para arrancar cada parte por separado: [sección 5 del backend](backend/README.md#5-api-de-la-web) y [frontend/README.md](frontend/README.md).

## Antes de commitear

```bat
python governance\scripts\verificar.py     :: gobernanza + inventarios + pruebas del backend
```

En `frontend/`: `npm test`, `npx tsc --noEmit`, `npx eslint src` y `npx next build`. **No regeneres la línea base para destrabar** una compuerta ([ADR-0003](governance/docs/architecture/adr/ADR-0003-linea-base-de-gobernanza.md)).

## Documentación

Todo el marco está en [`governance/`](governance/readme.md): [runbooks](governance/docs/development/runbooks/README.md), [catálogo de reportes](governance/docs/business/domain-catalog.md), [seguridad](governance/docs/security/README.md) y [decisiones de diseño (ADR)](governance/docs/architecture/decision-records.md).
