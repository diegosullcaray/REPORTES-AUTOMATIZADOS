# Registro de incidentes

| Fecha | Incidente | Causa raíz | Prueba de regresión | Estado |
|---|---|---|---|---|
| 2026-10-18 | Los procesos del Diccionario (`generar`, `verificar`, `test`) terminaban siempre con código 134 en Windows | El lanzador filtraba el entorno con nombres en mixto (`SystemRoot`) y Python los entrega en mayúsculas: `node` arrancaba sin `SYSTEMROOT` y abortaba (`ncrypto::CSPRNG`) | `test_el_proceso_conserva_lo_que_windows_exige` (`tests/modulos/diccionario/infraestructura/test_lanzador.py`) | Cerrado |
