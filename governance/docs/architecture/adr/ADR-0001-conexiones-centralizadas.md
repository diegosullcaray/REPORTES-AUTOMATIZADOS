# ADR-0001: Conexiones centralizadas (ajustada por ADR-0006)

- Estado: Vigente · Fecha: 2026-10-06

## Contexto
El legado tenía cinco implementaciones distintas de conexión (pyodbc directo, `create_engine` con y sin credenciales, `Trusted_Connection`), con servidores y credenciales duplicados.

## Decisión
`config.py` define las conexiones; `db.py` es el único que abre conexiones. Los reportes piden por nombre. (Versión inicial: 3 «bases» `dw_raw`/`rcc`/`slc`; reemplazada por 3 **servidores** en [ADR-0006](./ADR-0006-conexion-es-servidor-base-por-reporte.md).)

## Consecuencias
Cambiar un servidor o credencial es editar `.env`. La regla `conexion-solo-en-db` lo hace cumplir. Las bases accesibles por nombre de 3 partes (`dbriesgos`, `INTCOM`, `DWH`, `csd`) no son conexiones propias.

> **Actualización 2026-10-16 ([ADR-0014](./ADR-0014-clean-architecture-backend.md))**: `config.py` es hoy `infraestructura/configuracion.py` (conexiones) y `dominio/servidores.py` (qué base vive en qué servidor); `db.py` es `infraestructura/bd.py`. Sigue siendo el único que abre conexiones.
