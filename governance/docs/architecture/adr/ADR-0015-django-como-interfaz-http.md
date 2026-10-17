# ADR-0015: Django como interfaz HTTP, una app por módulo

> **Actualización 2026-10-16 ([ADR-0016](./ADR-0016-monolito-modular.md))**: el proyecto Django es `backend/config/` y cada módulo aporta su app en `modulos/<módulo>/interfaces/web`. Las rutas de este documento son las anteriores.

- Estado: Vigente
- Fecha: 2026-10-16
- Sustituye en parte: ADR-0011 (la API ya no es FastAPI) y la ubicación `interfaces/http` de [ADR-0014](./ADR-0014-clean-architecture-backend.md).

## Contexto

Con la Clean Architecture ([ADR-0014](./ADR-0014-clean-architecture-backend.md)) la capa HTTP quedó reducida a *traducir* peticiones a casos de uso: ninguna regla de negocio vive en ella. Eso permitió cambiar de framework sin tocar el dominio, la aplicación ni la infraestructura. Se pidió que el backend sea **Django modularizado**.

## Alternativas

| Opción | Qué es | Veredicto |
|---|---|---|
| **A. Django reemplaza a FastAPI, vistas JSON con los DTO actuales** | Un proyecto Django (`interfaces/web`) con una app por tema; vistas finas que validan con Pydantic (`aplicacion/dto.py`) | **Elegida.** Mismas URL y mismo JSON: el frontend no cambia; una sola interfaz HTTP; sin duplicar contratos |
| B. Django junto a FastAPI | Dos interfaces HTTP | Doble mantenimiento y dos servidores |
| C. Django REST Framework | Serializers y ViewSets | Obliga a reescribir los contratos como serializers (duplica `dto.py`) y añade una dependencia |
| D. Django con ORM y modelos | Mover datos y reglas a modelos | Pierde la arquitectura limpia; las bases SQL Server del legado no encajan en el ORM |

## Decisión

```text
backend/
  manage.py                       python manage.py runserver 127.0.0.1:8000 --noreload
  src/interfaces/web/
    settings.py · urls.py · wsgi.py     proyecto Django (sin base de datos, sin sesiones ni plantillas de Django)
    http.py                             respuestas JSON de los DTO, lectura validada del cuerpo y de la consulta
    middleware.py                       sesión obligatoria + traducción de errores (422 / 404 / ErrorHttp)
    apps/
      sesion/         /api/sesion · /api/cuenta
      reportes/       catálogo, detalle, verificación, archivos, descarga, correo por reporte
      validacion/     verificar, historial, mensaje por Chat
      ejecuciones/    encolar, historial, eliminar
      configuracion/  perfil, ajustes, servidores, notificaciones
      google/         MCP de Google Workspace y firma de Gmail
```

- **Cada app es un módulo**: `apps.py`, `urls.py` y `views.py`. Una funcionalidad nueva = una app nueva en `INSTALLED_APPS` y su `include` en `urls.py`.
- **Las vistas no tienen reglas**: llaman a un caso de uso de `aplicacion/casos_uso/`. Los errores de negocio (`PeticionInvalida`, `NoEncontrado`) los traduce el middleware.
- **Contrato idéntico**: mismas URL, métodos y códigos; los errores de validación siguen siendo `{"detail": [{"loc","msg","type"}]}` (lo que lee `frontend/src/lib/api.ts`).
- **Sesión propia**: la cookie firmada de `aplicacion/casos_uso/sesion.py` (HttpOnly, SameSite=Strict) sigue siendo la sesión; no se usan `django.contrib.sessions`, `auth`, `admin` ni CSRF. Con SameSite estricto, el servidor solo en `127.0.0.1` y `ALLOWED_HOSTS` acotado, el modelo de amenaza no cambia.
- **Arranque**: `wsgi.py` conecta los adaptadores (`composicion`) y arranca la cola de ejecuciones **una vez por proceso**; por eso se lanza con `--noreload` (con recarga automática habría dos procesos).
- **Compuerta**: `django` entra en las librerías prohibidas para `dominio` y `aplicacion`; solo `interfaces` lo importa.

## Consecuencias

- Se eliminan `fastapi` y `uvicorn` de `requirements.txt` (y `httpx` del de desarrollo); entran `Django`, `asgiref`, `sqlparse` y `pydantic` explícito (antes llegaba por FastAPI).
- Las pruebas usan `django.test.Client` (`tests/cliente_web.py`, con la misma API que el cliente anterior): **ninguna aserción cambió**.
- `runserver` es el servidor de desarrollo de Django. Es suficiente para esta herramienta local (un analista, `127.0.0.1`); si algún día se publica en red, se sirve el mismo `wsgi.py` con un servidor WSGI de producción.
- Ya no existe `/openapi.json` ni `/docs`; el contrato vive en `aplicacion/dto.py` y en `frontend/src/lib/tipos.ts`.
- `iniciar.py` espera a la API consultando `/api/sesion` (responde 401 sin sesión: está arriba).

## Reversibilidad

Alta: la interfaz es la única capa que cambió. Volver a FastAPI es reescribir `interfaces/web` (≈400 líneas de vistas) sin tocar nada más.
