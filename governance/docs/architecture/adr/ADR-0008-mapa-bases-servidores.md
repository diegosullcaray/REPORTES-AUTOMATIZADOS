# ADR-0008: Mapa base → servidor; cada reporte se conecta al servidor de sus bases

- Estado: Vigente · Fecha: 2026-10-06 · Ajusta: [ADR-0006](./ADR-0006-conexion-es-servidor-base-por-reporte.md)

## Contexto
Una consulta T-SQL con nombres de 3 partes (`base.esquema.tabla`) solo resuelve bases del **mismo servidor**. Hasta ahora todos los reportes de lote se conectaban a `172.24.2.213`, pero según el explorador de SSMS de cada servidor (capturas de 2026-10):

| Servidor | Bases |
|---|---|
| `MISHWBDDES01` | app, gitea, government, inme, junk, metadata, mide, mod_app, mod_gpa, mod_rep, mod_sec, mod_sys_admin, mod_sys_login, staging, **storage**, strategos |
| `172.24.2.213` | abp, aud, crs, **csd**, DBEstudios, DBS70, dga, **dma**, dsa, **dwh**, etl, **INTCOM**, mds, mla, sla, slb, **slc**, sld, sle, slf, slg, tdj, test_temp, tmp, wks |
| `172.20.0.70` | DB202511…DB202610, DBEstudios, DBFinanzas, DBFSH, **DBRCC**, **dbriesgos**, DW_Application, DW_Metadata, DW_Raw, **DW_Raw_v2**, DW_Recycle, DW_Staging(_v2), DW_Summary(_v2), gerencia_riesgos_bd, ReportServer(TempDB) |

## Decisión
- `config.BASES_DE` es el único mapa base → servidor; `servidor_de_base()` / `servidor_de_tabla()` lo consultan. Las tablas ya no llevan servidor escrito: se **deriva** de su base.
- Cada reporte se conecta al servidor de las bases que usa: 14 reportes con `storage` → `mish`; los de `dwh`/`dma`/`csd`/`intcom` → `slc`; `dbriesgos`/`DW_Raw_v2`/`DBRCC` → `rcc`.
- La verificación de tablas al corte consulta cada tabla en **su** servidor.
- Regla de gobernanza `servidor-coherente`: las tablas y la base de un reporte deben vivir en el servidor que declara.

## Puntos por confirmar
- **`DW_Raw_v2`**: se pidió conectarlo a `172.24.2.213`, pero aparece en la lista de `172.20.0.70` (junto a `DBRCC` y `dbriesgos`) y el script heredado de CMG Mora lo consultaba allí; **se mantiene en `rcc`**. Si de verdad vive en `213`, es un cambio de una línea en `BASES_DE`.
- **`appj`** no aparece en ninguna captura; se asume en MISH porque `tapp-saldo-medio-territorio` lo escribe en la misma sesión que lee `storage`.
- **`DBEstudios`** existe en `213` y en `70`: no se usa y no se mapea.

## Consecuencias
- Un reporte no puede mezclar servidores en una sola consulta; si lo necesita, se divide (como `bancarizados`).
- Una base nueva exige añadirla a `BASES_DE` (si no, error claro).
