# Visión del sistema

Backend como **monolito modular** ([ADR-0016](./adr/ADR-0016-monolito-modular.md)): cada módulo de negocio es un contexto con sus propias capas de Clean Architecture ([ADR-0014](./adr/ADR-0014-clean-architecture-backend.md)); `core/` es el núcleo compartido y `config/` la raíz de composición y el proyecto Django. Las reglas las comprueba `arquitectura-capas`.

```text
                  config/ (Django + composicion.py: conecta los adaptadores a los puertos)
                          │
   ┌──────────────┬───────┴────────┬────────────────┐
   ▼              ▼                ▼                ▼
 sistema ──► reportes ──► notificaciones      integraciones      diccionario ──► reportes
   │            └──────────────────────────────► ▲
   └─────────────────────────────────────────────┘   (cada flecha: solo por dominio/aplicación del destino)

 dentro de cada módulo:   interfaces ──► aplicacion ◄── infraestructura        aplicacion ──► dominio
                          (HTTP·CLI·MCP) (casos de uso,   (BD, Excel, correo,
                                          puertos, dto)    Google, cola)
```

```text
backend/
  main.py                          entrada de la consola (delegada a modulos/reportes/interfaces/cli)
  manage.py                        entrada de Django
  src/
    core/                        núcleo compartido: bd.py (ÚNICO acceso a SQL Server), configuracion.py, entorno.py (.env), puertos.py,
                                 excepciones.py, servidores.py (qué base vive en qué servidor), fechas.py, http.py, dto.py
    modulos/
      reportes/                  catálogo, ejecución, verificación de tablas, archivos, validación masiva y ejecuciones
        dominio/                 reportes.py (catálogo), tablas.py, reglas_fecha.py, verificacion.py, formato_excel.py, archivos.py
        aplicacion/              ejecucion.py (ReporteLote, correr), puertos.py, dto.py, casos_uso/
        infraestructura/         excel.py, imagen.py, lector_archivos.py, cola_ejecuciones.py, historial_validacion.py, entregas/
        interfaces/              web/ (Django: apps, urls, vistas/), cli/ (comandos de main.py)
        catalogo/                un módulo por reporte del legado: diarios/ · mensuales/piero/ · mensuales/erick/
      notificaciones/            correo corporativo (SMTP) y aviso al webhook de Chat: dominio · aplicacion (correo.py = API pública) · infraestructura · interfaces/web
      integraciones/             Google Workspace: aplicacion (mensajeria.py = API pública) · infraestructura/google · interfaces/{web,mcp}
      diccionario/            diccionario de datos de los reportes MIS (generado desde SQL Server): consultas · cruce con el registro de tablas · procesos propios. dominio · aplicacion · infraestructura · interfaces/web
      sistema/                   sesión, cuenta, perfil, ajustes y servidores: aplicacion · interfaces/web
  config/                        (en backend/) proyecto Django (settings, urls, middleware, wsgi) y composicion.py (raíz de composición)
  tests/                           pytest, espejo de src/: core · config · modulos/<módulo>/<capa>
data/inputs/                       archivos que entran (Excel/CSV, formatos base) — no versionado
data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>/   salidas con el orden del legado — no versionado
governance/                        este marco
docs/LEGADO/                       archivo histórico, solo lectura
```

## Reglas

| Dónde | Puede importar | Nunca |
|---|---|---|
| `dominio` (de un módulo) | su `dominio` y `core` público | otra capa · `os`, `sys`, red, `pandas`, `pydantic`, frameworks (`django`) |
| `aplicacion` | su `dominio` y `aplicacion` | su `infraestructura`/`interfaces` · `smtplib`, `urllib.request`, `sqlalchemy`, `openpyxl`, `django`… |
| `infraestructura` | su `aplicacion` y `dominio`; adaptadores de `core` | su `interfaces` |
| `interfaces` | su `aplicacion` y `dominio` | su `infraestructura` y los adaptadores de `core` (los cablea `config`) |
| `catalogo` (reportes) | `dominio`, `aplicacion`, `infraestructura` del módulo | `interfaces`; otros reportes entre sí |
| otro módulo | solo `dominio` y `aplicacion` (API pública, sin `puertos`) de los módulos de los que depende | ciclos; `infraestructura`/`interfaces` ajenas |
| `core` | solo sí mismo | `modulos` |
| `config` | todo | — |

Grafo permitido: `reportes → notificaciones, integraciones`; `diccionario → reportes` (cruza el diccionario con el registro de tablas); `sistema → reportes, notificaciones, integraciones`; `notificaciones` e `integraciones` no dependen de nadie.

Reglas que se conservan de ADR anteriores:
1. Solo `core/bd.py` conoce pyodbc/SQLAlchemy (regla `conexion-solo-en-db`).
2. Solo `core/` y la infraestructura de cada módulo leen variables de entorno y escriben el `.env`; los casos de uso lo hacen por el puerto `Entorno`.
3. El T-SQL va incrustado en el módulo del reporte (`ReporteLote.sql`) con tokens de fecha; el ejecutor los resuelve desde `--fecha-corte`.
4. Cada reporte expone `main(argv) -> int` y se registra en `modulos/reportes/dominio/reportes.py`; sus tablas, en `modulos/reportes/dominio/tablas.py`.

## Cómo se conecta

`config/composicion.py` crea los adaptadores y los registra en el registro de puertos de cada módulo (`modulos/<módulo>/aplicacion/puertos.py`) y en el del núcleo (`core/puertos.py`); la API, la consola y el servidor MCP lo importan al arrancar. Los casos de uso piden lo que necesitan con `puertos().…` y `nucleo().bd`/`nucleo().entorno`. Lo que un módulo ofrece a otro es una fachada de su aplicación (`notificaciones/aplicacion/correo.py`, `integraciones/aplicacion/mensajeria.py`). Las pruebas parchean el adaptador o registran un doble con el `registrar(...)` del registro.

## Estado de la migración
16 reportes usan el ejecutor común (`ReporteLote`). Los 5 primeros migrados (CMG Mora, Bancarizados ×2, Extranjeros, Indicadores) tienen lógica Python propia y utilidades repetidas (`Periodo`, `cronometro`, `exportar_excel`): candidatos a converger al ejecutor. Ver [roadmap](../business/roadmap.md).
