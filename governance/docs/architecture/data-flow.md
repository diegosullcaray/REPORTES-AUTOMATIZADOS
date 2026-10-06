# Flujo de datos

1. `main.py <reporte> --fecha …` resuelve el módulo en `registro.py`.
2. El módulo calcula el periodo (reglas de fecha) y arma parámetros.
3. `db.leer_sql(alias, sql, params)` consulta (hilos opcionales entre bloques independientes).
4. Validación: vacío ≠ error, fuente al corte, variables críticas.
5. Transformación en pandas (normalizar llaves, agrupar productos).
6. Exportación a `salidas/<reporte>/`.
7. Entrega manual (correo) o carga (CMG Mora → `SBTVRIE001`).

Ver [linaje](../data/lineage.md).
