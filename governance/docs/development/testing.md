# Pruebas

- `pytest` en `tests/`, espejo de `src/`: `tests/core`, `tests/config` y `tests/modulos/<módulo>/<capa>`; `tests/conftest.py` añade `src/` y `backend/` al path y conecta los adaptadores (`from config import composicion`).
- **Nunca** se prueba contra las bases reales: se prueban reglas de fecha, transformaciones puras y configuración. Las consultas se validan manualmente en un entorno con acceso y se deja evidencia en [evidence](../evidence/README.md).
- Convención: un `tests/<ruta espejo>/test_<modulo>.py` por módulo (regla `prueba-vecina`); las apps de Django (vistas y rutas) se prueban por HTTP en `tests/config/test_api.py` con `tests/cliente_web.py`. Cada carpeta de pruebas es un paquete (`__init__.py`).
- Para código que llama a la base de datos, parchear el adaptador del puerto (`monkeypatch.setattr(core.bd, "leer_sql", falso)`) o registrar un doble con el `registrar(...)` del registro de puertos (`core.puertos.nucleo`, `modulos/<módulo>/aplicacion/puertos.puertos`). El historial de validación de las pruebas va a una carpeta temporal (`conftest.py`).

```bash
python -m pytest -q
```

## Frontend

Desde `frontend/`, antes de entregar (regla 7 de `frontend/AGENTS.md`):

```bash
npm test                 # node --test sobre src/**/*.test.ts (formato, colores…)
npx tsc --noEmit
npx eslint src
npx next build
```

`src/lib/colores.test.ts` exige que los componentes usen solo tokens `--mis-*` (sin hex ni `rgb()`); los gráficos de `components/grafico.tsx` resuelven esos tokens en el navegador, por eso no llevan colores fijos.
