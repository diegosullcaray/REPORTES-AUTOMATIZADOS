# ADR-0013: Repositorio dividido en `backend/` y `frontend/`

- Estado: Vigente
- Fecha: 2026-10-08

## Contexto

El motor Python, la API y la web Next.js convivían en la raíz y en `web/`. Había dos mundos (Python y Node) mezclados con la
gobernanza, y cada uno necesita su propio entorno, dependencias y comandos.

## Decisión

```text
backend/     Python: motor de reportes (src/reportes), API de la web (src/api), tests, data/, requirements, .env, env/
frontend/    Next.js + shadcn (antes web/)
governance/  marco de gobernanza (agentes, skills, docs, scripts)   ← en la raíz, común a ambos
docs/LEGADO/ archivo histórico, solo lectura                        ← en la raíz
```

- **Cada parte tiene su README**: `backend/README.md` (motor y API), `frontend/README.md` (web) y el de la raíz, que solo
  es el mapa del repo.
- **Los comandos de Python se ejecutan dentro de `backend/`** (`python main.py …`, `env\Scripts\activate`); las rutas
  `data/…` y `.env` son las de esa carpeta. Los de la web, dentro de `frontend/`.
- **`governance/scripts/`** sigue en la raíz y apunta a `backend/` (constante `BACK`). Las rutas de la línea base son
  relativas a `backend/` (`src/reportes/…`), por eso no cambió.
- `config.py` toma `RAIZ` como el padre de `src/` (ahora `backend/`), así que `data/` y `.env` viven en `backend/`.

## Consecuencias

- Los documentos de `governance/` citan rutas del código como `src/…`, `tests/…` y `data/…`: son relativas a `backend/`.
- El entorno virtual se recrea en `backend/env` (un venv movido deja de funcionar).
- Se retiró una copia desactualizada de `governance/` que había quedado dentro de la web.
