# Linaje del dato

```text
Servidores y bases origen (mish / slc / rcc)
      │  T-SQL incrustado en el módulo del reporte (tokens de fecha)
      ▼
reportes.db (único acceso, parámetros enlazados)
      ▼
Módulo del reporte (src/reportes/<frecuencia>/<reporte>.py): validación + transformación pandas
      ▼
salidas/<reporte>/…  (Excel / TXT de INSERTs)
      ▼
Correo / carga a [storage].[com_act].[SBTVRIE001] / Excel de plantilla
```

## Frescura de las tablas
Un reporte solo es confiable si **todas** sus tablas llegaron al corte. `python main.py tablas <reporte> --fecha-corte <corte> --verificar` compara `MAX(columna_fecha)` con el corte; ver [inventario de tablas](./tables-inventory.md) y [runbooks](../development/runbooks/README.md).

## Cómo rastrear una cifra
1. Reporte y fecha de corte (nombre del archivo en `salidas/`).
2. SQL exacto: la constante `SQL` del módulo, en el commit de esa ejecución.
3. Servidor, base de datos y tabla (ver [catálogo](./catalog.md)).
4. Transformaciones: funciones del módulo (agrupaciones de producto, normalización de llaves).

Una cifra que no se pueda rastrear con estos cuatro pasos **no está gobernada**.

## Puntos de riesgo conocidos
- Cruces entre servidores (RCC ↔ SLC): las llaves se normalizan como texto (sin espacios ni `.0`); diagnosticar el cruce.
- Cachés `.pkl` de Bancarizados: evitan reconsultar; usar `--sin-cache` ante dudas.
- CMG Mora trunca `CMGMora_Recaudo` en cada ejecución: no ejecutar dos veces en paralelo.
