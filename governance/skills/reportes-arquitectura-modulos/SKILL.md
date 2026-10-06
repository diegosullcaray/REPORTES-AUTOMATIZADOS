---
name: reportes-arquitectura-modulos
description: Estructura canónica del proyecto de reportes y dónde va cada archivo. Usar al crear o ubicar un reporte, un SQL, una plantilla o una utilidad compartida.
---

# Arquitectura de módulos

```text
src/reportes/
  config.py        rutas + 3 BD          (único que lee .env)
  db.py            acceso a BD           (único que abre conexiones)
  registro.py      catálogo de reportes
  comun/           utilidades compartidas
  diarios/<reporte>.py
  mensuales/<reporte>.py
sql/<diarias|mensuales>/<reporte>/<nombre>.sql
plantillas/<frecuencia>/<reporte>_base.xlsx|xlsm
tests/test_<modulo>.py
```

## Reglas
1. Un reporte = un módulo con `main(argv) -> int` registrado en `registro.py`.
2. Los reportes no se importan entre sí; lo compartido sube a `comun/`.
3. Nombres `snake_case`, sin espacios ni tildes.
4. Salidas en `config.DIR_SALIDAS / "<reporte>"`.
5. Al agregar un reporte: `generar_inventario.py` y `verificar.py`.
