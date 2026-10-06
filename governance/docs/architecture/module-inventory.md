# Inventario de módulos

> **Generado** por `governance/scripts/generar_inventario.py`. No editar a mano: `python governance/scripts/generar_inventario.py`.

## Bases de datos

| Alias | Servidor (defecto) | Base (defecto) | Variables |
|---|---|---|---|
| `dw_raw` | 172.20.0.70 | DW_Raw_v2 | `DW_RAW_SERVER/DATABASE/USER/PASSWORD` |
| `rcc` | 172.20.0.70 | DBRCC | `RCC_SERVER/DATABASE/USER/PASSWORD` |
| `slc` | 172.24.2.213 | slc | `SLC_SERVER/DATABASE/USER/PASSWORD` |

## Reportes automatizados (5)

| Comando | Frecuencia | Bases | Módulo |
|---|---|---|---|
| `cmg-mora` | diaria | dw_raw | `reportes.diarios.cmg_mora` |
| `bancarizados` | mensual | rcc, slc | `reportes.mensuales.bancarizados` |
| `bancarizados-producto` | mensual | slc | `reportes.mensuales.bancarizados_producto` |
| `clientes-extranjeros` | mensual | slc, rcc | `reportes.mensuales.clientes_extranjeros` |
| `indicadores-clientes` | mensual | slc | `reportes.mensuales.indicadores_clientes` |

## SQL versionado (27)

| Archivo | Estado |
|---|---|
| `sql/diarias/cartera_sin_asignar/p001_01_cartera_sin_asignar.sql` | pendiente de automatizar |
| `sql/diarias/cmg_mora/p002_01_recaudo.sql` | pendiente de automatizar |
| `sql/diarias/cmg_mora/p002_02_provisiones.sql` | pendiente de automatizar |
| `sql/diarias/cmg_mora/p002_03_inserts.sql` | pendiente de automatizar |
| `sql/diarias/cmg_mora/p002_castigos.sql` | pendiente de automatizar |
| `sql/mensuales/clientes_jovenes/jovenes.sql` | consumido por código |
| `sql/mensuales/desembolsos_por_canal/desembolsos_canal.sql` | pendiente de automatizar |
| `sql/mensuales/finanzas_bancarizados/bancarizados.sql` | consumido por código |
| `sql/mensuales/finanzas_extranjeros/clientes_extranjeros_tipodoc.sql` | pendiente de automatizar |
| `sql/mensuales/finanzas_info_general/consulta_anterior.sql` | pendiente de automatizar |
| `sql/mensuales/finanzas_info_general/creditosql.sql` | consumido por código |
| `sql/mensuales/finanzas_info_general/pasivos.sql` | consumido por código |
| `sql/mensuales/finanzas_info_general/seguros.sql` | consumido por código |
| `sql/mensuales/fondeo_estable/fondeo_estable.sql` | consumido por código |
| `sql/mensuales/heredados_pdm/heredados_pdm.sql` | consumido por código |
| `sql/mensuales/productos_verdes/info_prod_verdes_slc.sql` | pendiente de automatizar |
| `sql/mensuales/ratio_ce_nuevos_migrantes/clientes_rurales_migrantes.sql` | pendiente de automatizar |
| `sql/mensuales/ratio_ce_nuevos_migrantes/contratacion_electronica.sql` | pendiente de automatizar |
| `sql/mensuales/reporte_michael_palacios/captaciones.sql` | pendiente de automatizar |
| `sql/mensuales/reporte_michael_palacios/castigos.sql` | pendiente de automatizar |
| `sql/mensuales/reportes_giovanni/cartera_vigente_agro.sql` | pendiente de automatizar |
| `sql/mensuales/reportes_giovanni/saldo_medio_puntual_captaciones.sql` | pendiente de automatizar |
| `sql/mensuales/reportes_giovanni/seguros_original.sql` | pendiente de automatizar |
| `sql/mensuales/reportes_giovanni/seguros_remasterizado.sql` | pendiente de automatizar |
| `sql/mensuales/saca_tu_garra/saca_tu_garra.sql` | consumido por código |
| `sql/mensuales/saldo_medio_vigente/saldo_medio_vigente.sql` | consumido por código |
| `sql/mensuales/tapp_saldo_medio_territorio/tapp_stock_tppmes_salmediovigente_territorio.sql` | pendiente de automatizar |

## Pruebas (7 archivos)

- `tests/test_cli_tablas.py`
- `tests/test_config.py`
- `tests/test_db.py`
- `tests/test_registro.py`
- `tests/test_tablas.py`
- `tests/test_validar_gobernanza.py`
- `tests/test_verificacion.py`
