---
name: web-modulos-escalables
description: Cómo crecer la web por módulos sin acoplar pantallas. Usar al añadir una funcionalidad o una ruta nueva.
---

# Módulos escalables de la web

```
src/
  app/(auth)/        pantallas públicas (login), sin sidebar
  app/(panel)/       pantallas con sidebar; rutas delgadas que solo montan un feature
  proxy.ts           sin cookie de sesión → /login
  features/<tema>/   orquestación de una pantalla: auth, reportes, ejecuciones, inicio…
  components/        presentación reutilizable (sin llamar a la API)
  lib/api.ts         única puerta a la API · lib/formato.ts funciones puras · lib/tipos.ts contratos
```

- Un tema nuevo = carpeta nueva en `features/` + ruta en `app/(panel)/`; no se toca otro feature.
- Un feature importa de `components/` y `lib/`, nunca de otro feature salvo por su componente público (p. ej. `VisorLog`, `DialogoVistaPrevia`).
- Contenido compartido entre diálogo y página = un componente (`ContenidoEjecucion`), no dos copias.
- Endpoint nuevo: ruta en `src/api/app.py`, regla en `servicios.py`, contrato en `esquemas.py`, método en `lib/api.ts`, prueba en `tests/test_app.py`.
- Cierre: `npm test`, `npx tsc --noEmit`, `npx eslint src`, `npx next build`.
