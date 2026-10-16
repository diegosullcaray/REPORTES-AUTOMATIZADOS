---
name: reportes-arquitectura-modulos
description: Estructura canónica del proyecto de reportes y dónde va cada archivo. Usar al crear o ubicar un reporte, un SQL, una plantilla o una utilidad compartida.
---

# Arquitectura de módulos

Clean Architecture por capas ([ADR-0014](../../docs/architecture/adr/ADR-0014-clean-architecture-backend.md)): `dominio ← aplicacion ← infraestructura / interfaces`.

```text
src/
  dominio/           reglas puras: reportes.py (catálogo), tablas.py, servidores.py, fechas.py, reglas_fecha.py, verificacion.py
  aplicacion/        ejecucion.py (flujo común: tablas al corte → consulta → validación → Excel), casos_uso/, puertos.py, dto.py
  infraestructura/   bd.py (único que abre conexiones), configuracion.py (único que lee .env), excel.py, correo_smtp.py, google/ …
  interfaces/        http/ (rutas), cli/, mcp/
  reportes/
    diarios/r<NN>_<nombre>.py              el SQL va incrustado en el módulo; <NN> = número del legado
    mensuales/piero/r<NN>_<nombre>.py      heredados de Piero (01…09)
    mensuales/erick/r<NN>_<nombre>.py      heredados de Erick (01…03)
  composicion.py     conecta los adaptadores a los puertos
data/inputs/<reporte>/         archivos que entran (Excel/CSV, formatos base); no versionado
data/outputs/<reporte>/        archivos que generan los reportes; no versionado
tests/<capa>/test_<modulo>.py  dominio · aplicacion · infraestructura · interfaces · reportes
```

## Reglas
1. Un reporte = un módulo con `main(argv) -> int` registrado en `dominio/reportes.py`.
2. Los reportes no se importan entre sí; lo compartido sube a `dominio/` o `aplicacion/`.
3. Nombres `snake_case`, sin espacios ni tildes.
4. Entradas en `DIR_INPUTS / "<reporte>"`; salidas en `DIR_OUTPUTS / "<reporte>"` (`infraestructura/configuracion.py`; en la aplicación, `aplicacion/rutas.carpeta_salida`).
5. La dependencia solo apunta hacia adentro: el dominio no importa nada de afuera, la aplicación no importa la infraestructura (usa puertos) y las interfaces no importan la infraestructura (la cablea `composicion.py`). La regla `arquitectura-capas` falla si no se cumple.
6. Al agregar un reporte: `generar_inventario.py` y `verificar.py`.
