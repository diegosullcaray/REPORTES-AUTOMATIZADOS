# Inventario de módulos

> **Generado** por `governance/scripts/generar_inventario.py`. No editar a mano: `python governance/scripts/generar_inventario.py`.

## Conexiones (3 servidores)

El `.env` define **servidores**; la **base de datos la elige cada reporte** (`base=` en su `ReporteLote`, o su propio `USE` / nombres de 3 partes).

| Conexión | Servidor (defecto) | Autenticación | Variables `.env` |
|---|---|---|---|
| `mish` | MISHWBDDES01 | Windows (o SQL si hay USER/PASSWORD) | `MISH_SERVER`, `MISH_USER`, `MISH_PASSWORD` |
| `slc` | 172.24.2.213 | Windows (o SQL si hay USER/PASSWORD) | `SLC_SERVER`, `SLC_USER`, `SLC_PASSWORD` |
| `rcc` | 172.20.0.70 | SQL (USER/PASSWORD) | `RCC_SERVER`, `RCC_USER`, `RCC_PASSWORD` |

## Reportes ejecutables (22)

| Comando | Frecuencia | Servidor | Base de datos | Módulo | Qué hace |
|---|---|---|---|---|---|
| `cmg-mora` | diaria | rcc | propia (ver módulo) | `reportes.diarios.cmg_mora` | Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0) |
| `bancarizados` | mensual | rcc, slc | propia (ver módulo) | `reportes.mensuales.bancarizados` | Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio |
| `bancarizados-producto` | mensual | slc | propia (ver módulo) | `reportes.mensuales.bancarizados_producto` | Bancarizados por producto (clientes nuevos con desembolso) |
| `clientes-extranjeros` | mensual | slc, rcc | propia (ver módulo) | `reportes.mensuales.clientes_extranjeros` | Clientes por nacionalidad: créditos, pasivos y seguros |
| `indicadores-clientes` | mensual | slc | propia (ver módulo) | `reportes.mensuales.indicadores_clientes` | Indicadores de clientes para el Directorio |
| `cartera-sin-asignar` | diaria | slc | storage | `reportes.diarios.cartera_sin_asignar` | Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación |
| `cmg-castigos` | diaria | slc | storage | `reportes.diarios.cmg_castigos` | CMG Mora · recuperación de castigos 12M (SRECCAST12M): suma de SDAS005 en los últimos 11 cierres |
| `clientes-jovenes` | mensual | slc | slc | `reportes.mensuales.clientes_jovenes` | Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años |
| `desembolsos-por-canal` | mensual | slc | storage | `reportes.mensuales.desembolsos_por_canal` | Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT) |
| `fondeo-estable` | mensual | slc | slc | `reportes.mensuales.fondeo_estable` | Estadística de tramo / Fondeo estable (Eddy Martínez) |
| `heredados-pdm` | mensual | slc | slc | `reportes.mensuales.heredados_pdm` | Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar |
| `productos-verdes` | mensual | slc | slc | `reportes.mensuales.productos_verdes` | Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas |
| `contratacion-electronica` | mensual | slc | slc | `reportes.mensuales.contratacion_electronica` | Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto) |
| `clientes-rurales-migrantes` | mensual | slc | storage | `reportes.mensuales.clientes_rurales_migrantes` | Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres |
| `michael-captaciones` | mensual | slc | slc | `reportes.mensuales.michael_captaciones` | Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos) |
| `michael-castigos` | mensual | slc | slc | `reportes.mensuales.michael_castigos` | Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos) |
| `giovanni-captaciones` | mensual | slc | storage | `reportes.mensuales.giovanni_captaciones` | Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones |
| `giovanni-seguros` | mensual | slc | slc | `reportes.mensuales.giovanni_seguros` | Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar» |
| `giovanni-cartera-agro` | mensual | slc | storage | `reportes.mensuales.giovanni_cartera_agro` | Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior) |
| `saca-tu-garra` | mensual | slc | storage | `reportes.mensuales.saca_tu_garra` | Saca tu garra (Giancarlos): entregar 8:00–8:30 AM |
| `saldo-medio-vigente` | mensual | slc | slc | `reportes.mensuales.saldo_medio_vigente` | Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios |
| `tapp-saldo-medio-territorio` | mensual | slc | storage | `reportes.mensuales.tapp_saldo_medio_territorio` | TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy) |

## Pruebas (10 archivos)

- `tests/test_cli_tablas.py`
- `tests/test_config.py`
- `tests/test_db.py`
- `tests/test_ejecutor.py`
- `tests/test_fechas_corte.py`
- `tests/test_registro.py`
- `tests/test_reportes_lote.py`
- `tests/test_tablas.py`
- `tests/test_validar_gobernanza.py`
- `tests/test_verificacion.py`
