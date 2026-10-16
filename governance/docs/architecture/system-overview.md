# Visión del sistema

Backend con **Clean Architecture por capas** ([ADR-0014](./adr/ADR-0014-clean-architecture-backend.md)): la dependencia apunta solo hacia adentro y la comprueba la regla `arquitectura-capas`.

```text
                     interfaces ──┐
                (HTTP · consola · MCP)
                                  ▼
 infraestructura ───────►  aplicacion  ───────►  dominio
 (BD, Excel, correo,       (casos de uso,        (reglas puras del negocio)
  Google, .env, cola)       puertos, dto)
        ▲                       ▲
        └──── composicion.py ───┘   conecta los adaptadores a los puertos al arrancar
```

```text
backend/
  main.py                          entrada de la consola (delegada a interfaces/cli)
  src/
    dominio/                       reglas puras: sin I/O ni frameworks
      errores.py                   ConfiguracionError, ErrorDatos, ErrorIntegracion
      reportes.py                  catálogo de reportes (comando → módulo, responsable, carpeta)
      tablas.py                    registro de TABLAS por reporte (servidor, tipo, columna de fecha)
      servidores.py                qué base vive en qué servidor (mish / slc / rcc)
      fechas.py · reglas_fecha.py  cortes, tokens @@F@@… y cómo usa cada reporte la fecha
      verificacion.py              estados, causas y mensaje de solicitud a Producción
      formato_excel.py             Columna / Resumen: cómo sale un resultado en el Excel
      entregas.py · archivos.py    a quién se entrega y qué archivos son entregables
    aplicacion/                    casos de uso + puertos
      puertos.py                   AccesoBD, Entorno, ExportadorExcel, ColaEjecuciones, … (Protocol)
      ejecucion.py                 flujo común de todo reporte de lote (ReporteLote, correr)
      verificacion.py · cortes.py · rutas.py · columnas.py · destinatarios.py
      dto.py                       contratos de entrada y salida (Pydantic)
      casos_uso/                   catalogo · verificacion · ejecuciones · archivos · configuracion
                                   correo_reporte · validacion · google · notificaciones · sesion
    infraestructura/               adaptadores de los puertos
      configuracion.py             rutas, .env y conexión a los 3 servidores
      bd.py                        ÚNICO acceso a SQL Server (pyodbc / SQLAlchemy)
      entorno.py · excel.py · imagen.py · correo_smtp.py · cola_ejecuciones.py
      historial_validacion.py · lector_archivos.py
      google/cliente.py            Gmail, Chat y servidores MCP oficiales
      entregas/                    correo del resumen diario (cuenta MIS) y entrega por Chat
    interfaces/
      web/                         API de la web (Django): settings, urls, middleware, http.py y apps/ (una por tema)
      cli/principal.py · tablas.py comandos de `main.py`
      mcp/servidor.py              servidor MCP de envío (stdio)
    reportes/                      un módulo por reporte del legado
      diarios/r<NN>_<nombre>.py    reportes diarios (número de «01 TAREAS DIARIAS»)
      mensuales/piero/r<NN>_…      reportes heredados de Piero (01…09)
      mensuales/erick/r<NN>_…      reportes heredados de Erick (01…03)
    composicion.py                 raíz de composición
  data/inputs/                     archivos que entran (Excel/CSV, formatos base) — no versionado
  data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>/   salidas con el orden del legado — no versionado
  tests/                           pytest, por capa: dominio · aplicacion · infraestructura · interfaces · reportes
governance/                        este marco
docs/LEGADO/                       archivo histórico, solo lectura
```

## Reglas de capas

| Capa | Puede importar | Nunca |
|---|---|---|
| `dominio` | `dominio` | otra capa · `os`, `sys`, red, `pandas`, `pydantic`, frameworks (`django`) |
| `aplicacion` | `dominio` | `infraestructura`, `interfaces` · `smtplib`, `urllib.request`, `sqlalchemy`, `openpyxl`, `django`… |
| `infraestructura` | `aplicacion`, `dominio` | `interfaces` |
| `interfaces` | `aplicacion`, `dominio`, `composicion` | `infraestructura` (la cablea `composicion`) |
| `reportes` | `dominio`, `aplicacion`, `infraestructura` | `interfaces`; otros reportes entre sí |
| `composicion` | todas | — |

Reglas que se conservan de ADR anteriores:
1. Solo `infraestructura/bd.py` conoce pyodbc/SQLAlchemy (regla `conexion-solo-en-db`).
2. Solo `infraestructura/` lee variables de entorno y escribe el `.env`; los casos de uso lo hacen por el puerto `Entorno`.
3. El T-SQL va incrustado en el módulo del reporte (`ReporteLote.sql`) con tokens de fecha; el ejecutor los resuelve desde `--fecha-corte`.
4. Cada reporte expone `main(argv) -> int` y se registra en `dominio/reportes.py`; sus tablas, en `dominio/tablas.py`.

## Cómo se conecta

`composicion.py` crea un adaptador por puerto y los registra en `aplicacion/puertos.py`; la API, la consola y el servidor MCP lo importan al arrancar. Los casos de uso piden lo que necesitan con `puertos().bd`, `puertos().entorno`… Las pruebas parchean el adaptador o registran un doble con `aplicacion.puertos.registrar(...)`.

## Estado de la migración
16 reportes usan el ejecutor común (`ReporteLote`). Los 5 primeros migrados (CMG Mora, Bancarizados ×2, Extranjeros, Indicadores) tienen lógica Python propia y utilidades repetidas (`Periodo`, `cronometro`, `exportar_excel`): candidatos a converger al ejecutor. Ver [roadmap](../business/roadmap.md).
