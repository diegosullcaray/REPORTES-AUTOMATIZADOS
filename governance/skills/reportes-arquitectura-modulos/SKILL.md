---
name: reportes-arquitectura-modulos
description: Estructura canónica del proyecto de reportes y dónde va cada archivo. Usar al crear o ubicar un reporte, un SQL, una plantilla o una utilidad compartida.
---

# Arquitectura de módulos

Monolito modular ([ADR-0016](../../docs/architecture/adr/ADR-0016-monolito-modular.md)): módulos de negocio con capas de Clean Architecture ([ADR-0014](../../docs/architecture/adr/ADR-0014-clean-architecture-backend.md)) dentro de cada uno.

```text
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
    diccionario/            diccionario de datos de los reportes MIS (repo DICCIONARIO, solo lectura): consultas · cruce con el registro de tablas · procesos npm. dominio · aplicacion · infraestructura · interfaces/web
    sistema/                   sesión, cuenta, perfil, ajustes y servidores: aplicacion · interfaces/web
config/                        (en backend/) proyecto Django (settings, urls, middleware, wsgi) y composicion.py (raíz de composición)
data/inputs/<reporte>/         archivos que entran (Excel/CSV, formatos base); no versionado
data/outputs/<reporte>/        archivos que generan los reportes; no versionado
tests/                         espejo de src/: core · config · modulos/<módulo>/<capa>/test_<modulo>.py
```

Un reporte del catálogo: `catalogo/diarios/r<NN>_<nombre>.py`, `catalogo/mensuales/piero/r<NN>_…` (01…09) o `catalogo/mensuales/erick/r<NN>_…` (01…03); el SQL va incrustado en el módulo y `<NN>` es el número del legado.

## Reglas
1. Un reporte = un módulo con `main(argv) -> int` registrado en `modulos/reportes/dominio/reportes.py`.
2. Los reportes no se importan entre sí; lo compartido sube al `dominio/` o la `aplicacion/` del módulo `reportes`.
3. Nombres `snake_case`, sin espacios ni tildes.
4. Entradas en `DIR_INPUTS / "<reporte>"`; salidas en `DIR_OUTPUTS / "<reporte>"` (`core/configuracion.py`; en la aplicación, `aplicacion/rutas.carpeta_salida`).
5. La dependencia solo apunta hacia adentro: el dominio no importa nada de afuera, la aplicación no importa la infraestructura (usa puertos), las interfaces no importan la infraestructura (la cablea `config/composicion.py`) y un módulo solo usa el dominio y la aplicación de otro, sin ciclos. La regla `arquitectura-capas` falla si no se cumple.
6. Al agregar un reporte: `generar_inventario.py` y `verificar.py`.
