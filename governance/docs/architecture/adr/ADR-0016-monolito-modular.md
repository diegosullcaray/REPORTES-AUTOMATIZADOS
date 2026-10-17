# ADR-0016: Monolito modular, Clean Architecture dentro de cada módulo

- Estado: Vigente
- Fecha: 2026-10-16
- Sustituye en parte: la disposición «una capa por carpeta de `src/`» de [ADR-0014](./ADR-0014-clean-architecture-backend.md) y la ubicación `src/interfaces/web` de [ADR-0015](./ADR-0015-django-como-interfaz-http.md). Se conservan sus reglas (dependencia hacia adentro, puertos, Django como capa HTTP).

## Contexto

Con capas globales (`dominio/`, `aplicacion/`, `infraestructura/`, `interfaces/`) cada tema nuevo (correo, Google, sesión) añadía archivos en las cuatro carpetas y nada impedía que un tema usara las entrañas de otro. Para escalar se agrupa por **módulos de negocio** y las capas viven dentro de cada uno.

## Decisión

```text
backend/
  config/                  proyecto Django y composicion.py (raíz de composición)
  src/core/                núcleo compartido: bd, entorno, configuracion, puertos (registro genérico), excepciones, http, dto, fechas, servidores
  src/modulos/<módulo>/    dominio · aplicacion · infraestructura · interfaces (y catalogo/ en reportes)
```

Módulos: `reportes` (catálogo, ejecución, verificación, validación, ejecuciones), `notificaciones` (correo SMTP y webhook de Chat), `integraciones` (Google Workspace y MCP) y `sistema` (sesión, cuenta, perfil, ajustes y servidores).

Reglas (las exige `arquitectura-capas`):
1. Dentro de un módulo la dependencia apunta solo hacia adentro (`dominio ← aplicacion ← infraestructura / interfaces`).
2. Entre módulos solo se usa el `dominio` y la `aplicacion` del destino, nunca sus `puertos`: cada módulo expone una fachada (`notificaciones/aplicacion/correo.py`, `integraciones/aplicacion/mensajeria.py`). Grafo sin ciclos: `reportes → notificaciones, integraciones`; `sistema → reportes, notificaciones, integraciones`.
3. `core` no depende de ningún módulo; sus adaptadores (`bd`, `entorno`, `configuracion`) solo los usan la infraestructura, el catálogo y `config`.
4. Cada módulo tiene su propio registro de puertos (`core.puertos.Registro`); `config/composicion.py` los conecta.
5. `config` solo se importa desde las entradas (`interfaces`).

## Consecuencias

- Un módulo nuevo (p. ej. otro canal de entrega) se añade sin tocar los demás; mover un módulo a otro servicio es cortar por su fachada.
- La API HTTP no cambia (mismas rutas y DTO); sí cambian la ruta del servidor MCP (`backend/src/modulos/integraciones/interfaces/mcp/servidor.py`: hay que volver a copiar la configuración desde la pestaña Conectar) y la ubicación de las pruebas (espejo de `src/`).
- Revertir es mover carpetas: no hay lógica nueva, solo ubicación y las fachadas.
