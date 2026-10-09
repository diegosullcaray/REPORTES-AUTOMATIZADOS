<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

## Reglas de la web de reportes

1. **Color solo por token `--mis-*`** (`src/app/tokens.css`, copia de MIS; no se edita aquí). Usa `text-[var(--mis-text-secondary)]`
   o `style={{ background: "var(--mis-surface)" }}`, o las clases de shadcn (que ya apuntan a los tokens). Nada de hex en componentes.
2. **Capas**: `lib/api.ts` es la única puerta a la API; `lib/formato.ts` funciones puras; `components/` presentación;
   `features/` orquestación por pantalla; `app/` solo rutas.
3. **Estados en orden**: error → cargando (esqueleto de la propia tabla) → vacío → contenido (`components/estados.tsx`).
4. **La API decide**: toda regla del reporte se valida en `src/api/servicios.py`; la web solo la anticipa.
5. **Estética Dokploy** (`governance/tasks/tareasdiarias.md`): plana, sin vidrio ni wallpaper; navegación con el `Sidebar` de
   shadcn (`AppSidebar`: retráctil, con el árbol de reportes plegable y el menú de usuario al pie, que lleva a `/perfil`
   con la configuración), migas en `components/encabezado.tsx`; dentro de una vista, tarjetas con `components/tarjeta.tsx`,
   vistas con `components/pagina.tsx`, logs con `components/terminal.tsx`, avisos con `toast` de sonner. Móvil primero.
6. **Patrones copiados de Dokploy** (referencia: `apps/dokploy/components` de github.com/Dokploy/dokploy):
   - Toda sección va en `components/marco.tsx` (marco `bg-sidebar` + panel con sombra, encabezado con ícono, título, descripción y acciones).
   - Toda tabla usa `components/tabla-datos.tsx` (TanStack Table v8: buscador, filtros, recarga, columnas visibles,
     `Ordenable` en encabezados, esqueleto, paginación). No escribir tablas a mano.
   - Estado con `Punto` + `Chip`; tiempos con `<Hace>`; logs en panel lateral con `features/ejecuciones/visor-log.tsx`.
   - Pestañas y secciones en la URL (`?tab=`, `?seccion=`); listas que cambian se refrescan solas (5–10 s).
7. Antes de entregar: `npm test`, `npx tsc --noEmit`, `npx eslint src`, `npx next build`.
