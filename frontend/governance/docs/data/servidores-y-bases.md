# Servidores y bases de datos

Qué base vive en qué servidor. Fuente: explorador de objetos de SSMS de cada servidor (capturas de 2026-10). **Fuente de verdad en código:** `config.BASES_DE` ([ADR-0008](../architecture/adr/ADR-0008-mapa-bases-servidores.md)).

> Una consulta con nombres de 3 partes solo ve las bases de **su** servidor. Por eso un reporte se conecta al servidor de las bases que usa.

| Conexión | Servidor | Auth | Bases que usan los reportes | Otras bases del servidor (capturas) |
|---|---|---|---|---|
| `mish` | `MISHWBDDES01` (SQL Server 14.0.3465) | Windows | `storage`, `appj`* | app, gitea, government, inme, junk, metadata, mide, mod_app, mod_gpa, mod_rep, mod_sec, mod_sys_admin, mod_sys_login, staging, strategos |
| `slc` | `172.24.2.213` (SQL Server 14.0.3520) | Windows | `dwh`, `dma`, `csd`, `intcom`, `slc` | abp, aud, crs, DBEstudios, DBS70, dga, dsa, etl, mds, mla, sla, slb, sld, sle, slf, slg, tdj, test_temp, tmp, wks |
| `rcc` | `172.20.0.70` | SQL (`master`) | `dbriesgos`, `DBRCC`, `DW_Raw_v2`, `DW_Metadata`, `DW_Raw`, `DB<AAAAMM>` | DBEstudios, DBFinanzas, DBFSH, DW_Application, DW_Recycle, DW_Staging(_v2), DW_Summary(_v2), gerencia_riesgos_bd, ReportServer(TempDB) |

\* `appj` no aparece en las capturas de MISH ni de 213, y la captura de `172.20.0.70` empieza en `DB202511` (no se ve su parte alfabética inicial, donde estaría `appj`): **podría vivir en `rcc`**. Se asume en MISH (por confirmar). `DBEstudios` está en 213 y en 70: ambigua, ningún reporte la usa.
Las bases mensuales `DB202511 … DB202610` son del servidor `rcc` (una por mes).
`rcc_cd` es un *linked server* definido en `slc` (172.24.2.213) que apunta a `rcc`; se consulta con 4 partes (`rcc_cd.db202607.dbo.ccp20260731`) desde `slc`.

## Qué reporte va a qué servidor
Generado: [inventario de módulos](../architecture/module-inventory.md) (columna Servidor/Base) y [catálogo de comandos](../development/runbooks/comandos.md).

| Servidor | Reportes |
|---|---|
| `mish` (`storage`) | `cartera-sin-asignar`, `cmg-castigos`, `desembolsos-por-canal`, `fondeo-estable`, `giovanni-captaciones`, `giovanni-seguros`, `giovanni-cartera-agro`, `michael-captaciones`, `michael-castigos`, `saca-tu-garra`, `saldo-medio-vigente`, `tapp-saldo-medio-territorio`, `contratacion-electronica`, `clientes-rurales-migrantes` |
| `slc` (`dwh`, `dma`, `csd`, `intcom`) | `bancarizados-producto`, `clientes-jovenes`, `productos-verdes`, `heredados-pdm`, `indicadores-clientes`, `clientes-extranjeros`, `bancarizados` (parte productos) |
| `rcc` (`dbriesgos`, `DW_Raw_v2`, `DBRCC`) | `cmg-mora`, `bancarizados` (parte deuda RCC), `clientes-extranjeros` (solo con `--pasivos-directo`) |

## Puntos por confirmar
1. **`DW_Raw_v2`**: se pidió ubicarlo en `172.24.2.213`; la captura de `172.20.0.70` lo lista y el script heredado de CMG Mora lo usa allí. Se mantiene en `rcc`. Cambiarlo = una línea en `BASES_DE`.
2. `appj` (dónde vive realmente): solo afecta a `tapp-saldo-medio-territorio`, que lee `storage` (MISH) y escribe `appj.dbo.salmediovigente1` en la misma sesión; si `appj` está en otro servidor, ese reporte hay que partirlo en dos.
3. El TXT de INSERTs de `cmg-mora` apunta a `[storage].[com_act].[SBTVRIE001]` (MISH): lo carga quien corresponda fuera de este proyecto.
