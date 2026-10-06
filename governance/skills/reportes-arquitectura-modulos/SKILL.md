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
  comun/ejecutor.py  flujo común: conexión → tablas al corte → consulta → validación → Excel
  comun/fechas.py   cortes y tokens @@F@@…
  tablas.py         tablas de cada reporte (servidor, tipo, columna de fecha)
  diarios/r<NN>_<nombre>.py              el SQL va incrustado en el módulo; <NN> = número del legado
  mensuales/piero/r<NN>_<nombre>.py      heredados de Piero (01…09)
  mensuales/erick/r<NN>_<nombre>.py      heredados de Erick (01…03)
data/inputs/<reporte>/         archivos que entran (Excel/CSV, formatos base); no versionado
data/outputs/<reporte>/        archivos que generan los reportes; no versionado
tests/test_<modulo>.py
```

## Reglas
1. Un reporte = un módulo con `main(argv) -> int` registrado en `registro.py`.
2. Los reportes no se importan entre sí; lo compartido sube a `comun/`.
3. Nombres `snake_case`, sin espacios ni tildes.
4. Entradas en `config.DIR_INPUTS / "<reporte>"`; salidas en `config.DIR_OUTPUTS / "<reporte>"`.
5. Al agregar un reporte: `generar_inventario.py` y `verificar.py`.
