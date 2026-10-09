# Contrato: conexiones (servidores) y bases de datos

El `.env` define **3 conexiones = 3 servidores**. La **base de datos no se fija en el `.env`: la elige cada reporte**, porque en un mismo servidor viven varias bases y cada reporte usa las suyas (por `base=`, por su propio `USE` o por nombres de 3 partes).

Se definen en `src/reportes/config.py` (`SERVIDORES`); el único código autorizado a abrirlas es `src/reportes/db.py` (regla `conexion-solo-en-db`).

| Conexión | Servidor | Autenticación | Variables `.env` | Bases que usan los reportes |
|---|---|---|---|---|
| `mish` | `MISHWBDDES01` | Windows | `MISH_SERVER`, `MISH_USER`, `MISH_PASSWORD` | `storage` (+ `staging`, `mod_rep`, …) y `appj` |
| `slc` | `172.24.2.213` | Windows (o SQL si hay USER/PASSWORD) | `SLC_SERVER`, `SLC_USER`, `SLC_PASSWORD` | `dwh`, `dma`, `csd`, `intcom`, `slc`; linked server `rcc_cd` → 172.20.0.70 |
| `rcc` | `172.20.0.70` | SQL (usuario `master`) | `RCC_SERVER`, `RCC_USER`, `RCC_PASSWORD` | `dbriesgos`, `DBRCC`, `DW_Raw_v2`, `DW_Metadata`, `DB<AAAAMM>` |

USER/PASSWORD vacíos ⇒ autenticación de Windows (solo si el servidor la admite por defecto: `mish`, `slc`). Usuario sin contraseña (o al revés) es error de configuración.

## Una consulta solo ve las bases de su servidor
SQL Server no cruza servidores con nombres de 3 partes: `storage.com_act.X` solo funciona conectado a MISH, `dwh.dbo.X` solo en `172.24.2.213`, `dbriesgos.dbo.X` solo en `172.20.0.70`. Por eso cada reporte se conecta al servidor de **sus** bases. El mapa base→servidor es `config.BASES_DE` ([servidores y bases](../servidores-y-bases.md)); la regla `servidor-coherente` falla si un reporte mezcla servidores o declara una base de otro. Un reporte que necesite datos de dos servidores se divide en dos consultas (como `bancarizados`: `rcc` + `slc`).

## ¿Qué base usa cada reporte?
Cada reporte lo declara en su código:

```python
REPORTE = ReporteLote(comando="saca-tu-garra", servidor="mish", base="storage", sql=SQL, ...)   # reportes de lote
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
4. Una **base nueva** se añade a `config.BASES_DE` (si no, `No sé en qué servidor vive la base …`); un servidor nuevo requiere una entrada en `config.SERVIDORES`, su bloque en `.env.example` y un ADR; no requiere nada en el `.env`.
