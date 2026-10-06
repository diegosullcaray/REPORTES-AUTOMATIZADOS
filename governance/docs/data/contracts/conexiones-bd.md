# Contrato: conexiones (servidores) y bases de datos

El `.env` define **3 conexiones = 3 servidores**. La **base de datos no se fija en el `.env`: la elige cada reporte**, porque en un mismo servidor viven varias bases y cada reporte usa las suyas (por `base=`, por su propio `USE` o por nombres de 3 partes).

Se definen en `src/reportes/config.py` (`SERVIDORES`); el único código autorizado a abrirlas es `src/reportes/db.py` (regla `conexion-solo-en-db`).

| Conexión | Servidor | Autenticación | Variables `.env` | Bases que usan los reportes |
|---|---|---|---|---|
| `mish` | `MISHWBDDES01` | Windows | `MISH_SERVER`, `MISH_USER`, `MISH_PASSWORD` | — (reservada; ningún reporte la usa aún) |
| `slc` | `172.24.2.213` | Windows (o SQL si hay USER/PASSWORD) | `SLC_SERVER`, `SLC_USER`, `SLC_PASSWORD` | `slc`, `storage`, `dwh`, `intcom`, `csd`, `dma`, `appj`; linked server `rcc_cd` |
| `rcc` | `172.20.0.70` | SQL (usuario `master`) | `RCC_SERVER`, `RCC_USER`, `RCC_PASSWORD` | `DBRCC`, `DW_Raw_v2`, `dbriesgos`, `DW_Metadata` |

USER/PASSWORD vacíos ⇒ autenticación de Windows (solo si el servidor la admite por defecto: `mish`, `slc`). Usuario sin contraseña (o al revés) es error de configuración.

## ¿Qué base usa cada reporte?
Cada reporte lo declara en su código:

```python
REPORTE = ReporteLote(comando="saca-tu-garra", servidor="slc", base="storage", sql=SQL, ...)   # reportes de lote
leer_sql("rcc", consulta, params, base="DBRCC")                                                  # consulta puntual
conexion_pyodbc("rcc", base="DW_Raw_v2")                                                         # escritura (CMG Mora)
```

Orden de prioridad del catálogo inicial: `base=` del reporte → `<PREFIJO>_DATABASE` del `.env` (opcional) → la base por defecto del login. Con nombres de 3 partes (`dwh.dbo.tabla`) la base inicial es indiferente.

## Uso desde código
- `leer_sql(servidor, sql, params, base=None)`: SELECT parametrizado → DataFrame.
- `ejecutar_lote(servidor, tsql, base=None)`: script T-SQL completo (GO, `USE`, `#temp`, `EXEC`) en una sesión → todos los resultados.
- `leer_ultimo_resultado(servidor, sql, params, base=None)`: lote con tabla temporal / SP en una sesión.
- `conexion_pyodbc(servidor, base=None)`: escrituras y control transaccional (CMG Mora).

## Reglas
1. Un servidor desconocido lanza `ConfiguracionError`; no hay credenciales por defecto.
2. Verificación: `python main.py probar-conexiones` (los 3 servidores).
3. Permisos: `rcc` se usa hoy con `master` para **todo** (lectura y escritura en `DW_Raw_v2`): ver [SEC-002](../../security/findings.md).
4. Agregar un servidor nuevo requiere una entrada en `config.SERVIDORES`, su bloque en `.env.example` y un ADR; agregar una **base** nueva no requiere nada en el `.env`.
