# ADR-0014: Backend con Clean Architecture por capas

> **Actualización 2026-10-16 ([ADR-0016](./ADR-0016-monolito-modular.md))**: las capas ya no son carpetas globales de `src/`; viven dentro de cada módulo (`src/modulos/<módulo>/<capa>`) y lo compartido en `src/core/`. Las rutas de este documento son las anteriores.

- Estado: Vigente
- Fecha: 2026-10-16
- Sustituye en parte: ADR-0001 (dónde viven `config` y `db`), ADR-0005 (dónde viven el ejecutor y el registro) y ADR-0011 (capas de la API). Las decisiones de fondo de esos ADR siguen vigentes; solo cambia **dónde** están.

## Contexto

El backend creció por capas de hecho, no de diseño:

- `api/servicios.py` (510 líneas) mezclaba catálogo, verificación, argumentos de ejecución, archivos, vista previa y edición del `.env`, y dependía a la vez de la base de datos, del ejecutor y del registro.
- `reportes/comun/` mezclaba reglas puras (`fechas`) con infraestructura (`excel`, `imagen`, SMTP).
- `reportes/config.py` era una hoja de la que dependía todo: rutas, `.env`, servidores y también *dónde vive cada base* (conocimiento del negocio).
- `api/*` importaba `reportes.*` y `mcp_google` sin ninguna frontera; cada caso de uso repetía las mismas líneas para escribir el `.env` y actualizar `os.environ` (seis veces).
- La única forma de probar un caso de uso era parchear funciones de módulos concretos (`monkeypatch.setattr(servicios, "leer_sql", …)`).

Restricciones que se mantienen: 1–2 personas, un solo proceso, ejecución manual (ADR-0007), 25 reportes del legado con sus rutas, números y carpetas de salida (ADR-0010), y las compuertas de gobernanza (ADR-0003).

## Alternativas

| Opción | Qué es | Costo | Por qué sí / no |
|---|---|---|---|
| **A. Clean Architecture por capas** | `dominio ← aplicacion ← infraestructura / interfaces`, con puertos y una raíz de composición | Medio: ~100 archivos movidos; las pruebas existentes lo cubren | **Elegida.** Da una regla de dependencia comprobable y casos de uso aislados |
| B. Módulos verticales por funcionalidad | Un paquete por contexto (`validacion/`, `ejecuciones/`, `entregas/`…) con mini-capas | Mayor: más fronteras que decidir y puertos duplicados | Escala mejor con varios equipos; para 1–2 personas añade carpetas sin beneficio inmediato |
| C. Solo ordenar lo crítico | Partir `servicios.py` y mover el I/O a `infra/` | Bajo | No cumple el objetivo: la dependencia seguiría siendo implícita y nada la protegería |

## Decisión

```text
backend/src/
  dominio/            reglas puras del negocio. Solo biblioteca estándar.
  aplicacion/         casos de uso, puertos (Protocol) y contratos (dto.py)
    casos_uso/        catalogo · verificacion · ejecuciones · archivos · configuracion · correo_reporte
                      validacion · google · notificaciones · herramientas_envio · sesion
  infraestructura/    adaptadores de los puertos: bd, excel, imagen, correo_smtp, google/, entorno, cola_ejecuciones, …
  interfaces/
    web/              Django: proyecto + una app por tema (ADR-0015)
    cli/              consola (`main.py`)
    mcp/              servidor MCP de envío (stdio)
  reportes/           un módulo por reporte del legado (mismas rutas r<NN>_<nombre>.py)
  composicion.py      raíz de composición: conecta los adaptadores a los puertos
```

### Regla de dependencia (la comprueba `arquitectura-capas`)

| Capa | Puede importar | No puede importar |
|---|---|---|
| `dominio` | `dominio` | cualquier otra capa; I/O, `os`, `sys`, red, `pandas`, `pydantic`, frameworks |
| `aplicacion` | `dominio` | `infraestructura`, `interfaces`; librerías de I/O (`smtplib`, `urllib.request`, `sqlalchemy`, `openpyxl`, `django`…) |
| `infraestructura` | `aplicacion`, `dominio` | `interfaces` |
| `interfaces` | `aplicacion`, `dominio`, `composicion` | `infraestructura` (la cablea `composicion`) |
| `reportes` (plugins) | `dominio`, `aplicacion`, `infraestructura` | `interfaces` |
| `composicion` | todas | — |

`pandas` y `pydantic` se admiten en `aplicacion` como **tipos de datos** (resultados tabulares y contratos), no como I/O. Los reportes son el anillo exterior: llevan T-SQL y formato de salida y pueden usar la infraestructura directamente.

### Puertos (en `aplicacion/puertos.py`)

| Puerto | Qué abstrae | Adaptador |
|---|---|---|
| `AccesoBD` | los 3 servidores SQL Server | `infraestructura/bd.py` |
| `Entorno` | `.env`, variables, carpetas de datos, corte configurado | `infraestructura/entorno.py` |
| `ExportadorExcel` | escritura del libro | `infraestructura/excel.py` |
| `ColaEjecuciones` | subprocesos de `main.py` e historial | `infraestructura/cola_ejecuciones.py` |
| `HistorialValidacion` | fichas de cada verificación | `infraestructura/historial_validacion.py` |
| `LectorArchivos` | vista previa de Excel | `infraestructura/lector_archivos.py` |
| `CorreoSMTP` | cuenta MIS y webhook de Chat | `infraestructura/correo_smtp.py` |
| `GoogleWorkspace` | Gmail, Chat y servidores MCP oficiales | `infraestructura/google/cliente.py` |

Un adaptador puede ser un **módulo** (un módulo con las funciones correctas cumple el `Protocol`). Los casos de uso llaman `puertos().bd.leer_sql(...)`; las pruebas parchean el adaptador o registran un doble con `aplicacion.puertos.registrar(...)`.

### Piezas que cambiaron de lugar

| Antes | Ahora |
|---|---|
| `reportes/config.py` | `dominio/servidores.py` (qué base vive en qué servidor), `dominio/errores.py` (`ConfiguracionError`) e `infraestructura/configuracion.py` (rutas, `.env`, conexión) |
| `reportes/db.py` | `infraestructura/bd.py` |
| `reportes/registro.py` | `dominio/reportes.py` (`carpeta_salida` → `aplicacion/rutas.py`) |
| `reportes/tablas.py`, `reglas_fecha.py` | `dominio/tablas.py`, `dominio/reglas_fecha.py` |
| `reportes/verificacion.py` | `dominio/verificacion.py` (estados y mensajes) + `aplicacion/verificacion.py` (consulta a la BD) |
| `reportes/comun/ejecutor.py` | `aplicacion/ejecucion.py` (`ReporteLote`, `Hoja`, `correr`) |
| `reportes/comun/fechas.py` | `dominio/fechas.py` (puro) + `aplicacion/cortes.py` (lee el `.env` por el puerto) |
| `reportes/comun/excel.py` | `dominio/formato_excel.py` (`Columna`, `Resumen`) · `aplicacion/columnas.py` · `infraestructura/excel.py` |
| `reportes/comun/{imagen,correo,entrega_*}.py` | `infraestructura/{imagen,correo_smtp}.py`, `infraestructura/entregas/`, `dominio/entregas.py` |
| `api/servicios.py` | `aplicacion/casos_uso/{catalogo,verificacion,ejecuciones,archivos,configuracion}.py` |
| `api/{mcp,notificaciones,validacion,envio_correo,sesion}.py` | `aplicacion/casos_uso/{google,notificaciones,validacion,correo_reporte,sesion}.py` |
| `api/esquemas.py` | `aplicacion/dto.py` |
| `api/app.py` | `interfaces/web/` (Django, una app por tema; antes `interfaces/http/`) |
| `api/ejecuciones.py`, `api/entorno.py` | `infraestructura/cola_ejecuciones.py`, `infraestructura/entorno.py` |
| `mcp_google/cliente.py` / `servidor.py` | `infraestructura/google/cliente.py` / `interfaces/mcp/servidor.py` (+ `aplicacion/casos_uso/herramientas_envio.py`) |
| `reportes/cli_tablas.py` | `interfaces/cli/tablas.py` |

### Lo que NO cambió (contratos estables)

- Las **rutas y nombres de los 25 reportes** (`reportes/diarios/r02_…`, `reportes/mensuales/<piero|erick>/r<NN>_…`) y sus carpetas de salida (ADR-0010).
- Los **comandos de consola** (`python main.py …`), sus argumentos y códigos de salida.
- Las **URL, métodos y códigos HTTP de la API** y los contratos de `dto.py` (el frontend no cambió).
- Las variables del `.env` y los argumentos de cada reporte.

## Cómo se extiende

- **Reporte nuevo**: módulo en `reportes/…` con `ReporteLote`; se registra en `dominio/reportes.py`, sus tablas en `dominio/tablas.py`. Importa `aplicacion.ejecucion` y, si lo necesita, `infraestructura.bd`. Ver la [guía](../../development/report-creation-guide.md).
- **Integración nueva** (otro canal de entrega, otra base): define el `Protocol` en `aplicacion/puertos.py`, implementa el adaptador en `infraestructura/`, regístralo en `composicion.py` y llámalo desde un caso de uso.
- **Caso de uso nuevo**: función en `aplicacion/casos_uso/<tema>.py` que usa `puertos()`; contrato en `dto.py`; vista en `interfaces/web/apps/<tema>/views.py`; prueba en `tests/aplicacion/casos_uso/`.

## Consecuencias

- **Pruebas por capa**: `tests/dominio`, `tests/aplicacion`, `tests/infraestructura`, `tests/interfaces`, `tests/reportes` (cada carpeta es un paquete, así dos `test_verificacion.py` de capas distintas no chocan).
- **Compuerta nueva** `arquitectura-capas` en `validar_gobernanza.py`: una importación hacia afuera o una librería de I/O en una capa interior es un error. Es una *función de aptitud* de la arquitectura: protege la decisión sin depender de la disciplina.
- **`prueba-vecina`** exime a `interfaces/web/apps/` y a `settings`/`urls`/`wsgi` (se prueban por HTTP en `tests/interfaces/web/test_api.py`).
- Se podaron de la línea base las entradas que ya no producía ningún hallazgo (`tabla-fecha-por-validar`, y `fechas.py`, que ahora tiene prueba); no se congeló nada nuevo (ADR-0003).
- Los registros de la web que guardaban rutas de código cambian: la API arranca con `python manage.py runserver 127.0.0.1:8000 --noreload` y el servidor MCP de envío es `backend/src/interfaces/mcp/servidor.py` (**quien lo haya pegado en su cliente MCP debe copiar de nuevo la configuración desde la pestaña Conectar**).

## Riesgos y reversibilidad

- Es una reorganización sin cambio de comportamiento: la red de seguridad son las 300+ pruebas, la compuerta de capas y un arranque real de la API y de la consola.
- Los adaptadores como módulos acoplan la prueba al nombre de sus funciones; si un adaptador crece, se convierte en clase sin tocar a quien lo usa.
- Reversible por Git (rama `refactor/clean-architecture`); los ADR-0001, 0005 y 0011 conservan la intención original.
