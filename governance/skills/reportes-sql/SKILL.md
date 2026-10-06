---
name: reportes-sql
description: Cómo se escribe, parametriza y versiona el SQL de los reportes. Usar al migrar una query del legado o al crear una nueva.
---

# SQL de reportes

- Vive en `sql/<frecuencia>/<reporte>/<nombre>.sql`, se carga con `cargar_sql()`.
- **Parámetros enlazados** para fechas y filtros; la fecha de corte nunca se edita a mano en el archivo.
- Nombres de tabla dinámicos (`PROV_PROY_<YYYYMMDD>_0`) solo con valores generados desde `datetime.date` y verificando `OBJECT_ID` antes de consultar.
- Lotes con tabla temporal o SP: `leer_ultimo_resultado` (misma sesión).
- Escrituras (`TRUNCATE`/`INSERT`): `conexion_pyodbc("dw_raw")`, con validación previa y sin ejecutar dos veces en paralelo.
- Sin credenciales ni servidores en el SQL; los linked servers (`rcc_cd`) sí se documentan en el [catálogo](../../docs/data/catalog.md).
- Variantes históricas (p. ej. `seguros_original` vs `seguros_remasterizado`) se conservan hasta decidir cuál rige; la decisión se anota en la ficha.
