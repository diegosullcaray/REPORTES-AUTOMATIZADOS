# Web de reportes

Interfaz Next.js + shadcn/ui (estética Dokploy) de los reportes automatizados. Pantallas y uso:
[runbook de la interfaz web](../governance/docs/development/runbooks/interfaz-web.md). Decisión: [ADR-0011](../governance/docs/architecture/adr/ADR-0011-interfaz-web.md).

## Iniciar el sistema

Necesita **Node 20+** y dos terminales. La web no hace nada sin la API: la consume por proxy en `/api`.

```bat
:: Terminal 1 — API (desde la raíz del repo, con el entorno activado y el .env completo)
env\Scripts\activate
python -m uvicorn api.app:app --app-dir src --host 127.0.0.1 --port 8000

:: Terminal 2 — Web (desde esta carpeta)
npm install                         :: solo la primera vez
npm run dev                         :: desarrollo
npm run build && npm start          :: uso normal
```

Abre <http://localhost:3000>. Si la API corre en otro puerto: `set REPORTES_API_URL=http://127.0.0.1:PUERTO` antes de arrancar la web.

## Iniciar sesión

Se entra con la **cuenta de Windows** (`DOMINIO\usuario` o `usuario@dominio`). Sin sesión, todo redirige a `/login` y la API responde 401.

| Variable del `.env` (raíz) | Efecto |
|---|---|
| `USUARIOS_WEB` | Usuarios que pueden entrar, separados por coma. Vacío = solo quien ejecuta la API |
| `SESION_SECRETO` | Firma de la cookie. Vacío = se genera en cada arranque y las sesiones caen al reiniciar la API |

La sesión dura 8 horas; tras 5 intentos fallidos el usuario queda bloqueado 5 minutos. Se cierra desde el menú de usuario (pie del sidebar).

## Estructura

```text
src/
  app/(auth)/login/     pantalla de acceso, sin sidebar
  app/(panel)/          pantallas con sidebar; rutas delgadas que montan un feature
  proxy.ts              sin cookie de sesión → /login
  features/<tema>/      orquestación por pantalla: auth, reportes, ejecuciones, inicio
  components/           presentación reutilizable (Marco, TablaDatos, Terminal, diálogos)
  lib/api.ts            única puerta a la API · formato.ts funciones puras · tipos.ts contratos
```

Una funcionalidad nueva = carpeta en `features/` + ruta en `app/(panel)/`. Reglas de diseño y capas: [AGENTS.md](AGENTS.md) y las skills `web-diseno-dokploy` y `web-modulos-escalables` en `../governance/skills/`.

## Antes de entregar

```bat
npm test
npx tsc --noEmit
npx eslint src
npx next build
```

Si `tsc` se queja de tipos de `.next/` tras mover rutas, borra la carpeta `.next` y vuelve a compilar.
