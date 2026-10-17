# Flujo de datos

1. `main.py <reporte> --fecha-corte …` (`modulos/reportes/interfaces/cli/principal.py`) resuelve el módulo en `modulos/reportes/dominio/reportes.py`;
   `modulos/reportes/aplicacion/ejecucion.correr()` orquesta: conexión → **tablas al corte** (si faltan: no ejecuta + mensaje a Producción) → consulta → **validación de datos** → Excel.
   La web hace lo mismo por la API: `modulos/reportes/interfaces/web` (Django) → caso de uso `ejecuciones` → cola → subproceso de `main.py`.
2. El módulo calcula el periodo (reglas de fecha de `modulos/reportes/dominio/fechas.py`) y arma parámetros.
3. `core/bd.leer_sql(servidor, sql, params, base=…)` consulta, a través del puerto `bd` (hilos opcionales entre bloques independientes).
4. Validación: vacío ≠ error, fuente al corte, variables críticas.
5. Transformación en pandas (normalizar llaves, agrupar productos).
6. Exportación a `data/outputs/<reporte>/` (`modulos/reportes/infraestructura/excel.py`, por el puerto `excel`).
7. Entrega manual (correo, Chat) o carga (CMG Mora → `SBTVRIE001`).

Ver [linaje](../data/lineage.md) y la [visión del sistema](./system-overview.md).
