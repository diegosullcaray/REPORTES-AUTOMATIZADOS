# ADR-0001: Conexiones centralizadas con 3 alias

- Estado: Vigente · Fecha: 2026-10-06

## Contexto
El legado tenía cinco implementaciones distintas de conexión (pyodbc directo, `create_engine` con y sin credenciales, `Trusted_Connection`), con servidores y credenciales duplicados.

## Decisión
`config.py` define las 3 bases (`dw_raw`, `rcc`, `slc`); `db.py` es el único que abre conexiones. Los reportes piden por alias.

## Consecuencias
Cambiar un servidor o credencial es editar `.env`. La regla `conexion-solo-en-db` lo hace cumplir. Las bases accesibles por nombre de 3 partes (`dbriesgos`, `INTCOM`, `DWH`, `csd`) no son conexiones propias.
