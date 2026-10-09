# Inventario de módulos

> **Generado** por `governance/scripts/generar_inventario.py`. No editar a mano: `python governance/scripts/generar_inventario.py`.

## Conexiones (3 servidores)

El `.env` define **servidores**; la **base de datos la elige cada reporte** (`base=` en su `ReporteLote`, o su propio `USE` / nombres de 3 partes).

| Conexión | Servidor (defecto) | Autenticación | Variables `.env` |
|---|---|---|---|
| `mish` | MISHWBDDES01 | Windows (o SQL si hay USER/PASSWORD) | `MISH_SERVER`, `MISH_USER`, `MISH_PASSWORD` |
| `slc` | 172.24.2.213 | Windows (o SQL si hay USER/PASSWORD) | `SLC_SERVER`, `SLC_USER`, `SLC_PASSWORD` |
| `rcc` | 172.20.0.70 | SQL (USER/PASSWORD) | `RCC_SERVER`, `RCC_USER`, `RCC_PASSWORD` |

## Reportes ejecutables (21)

| Responsable / Nº | Comando | Frecuencia | Servidor | Base de datos | Módulo | Qué hace |
|---|---|---|---|---|---|---|
| Diarias 02 | `cartera-sin-asignar` | diaria | mish | storage | `reportes.diarios.r02_cartera_sin_asignar` | Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación |
| Diarias 04.1 | `cmg-mora` | diaria | rcc | propia (ver módulo) | `reportes.diarios.r04_1_cmg_mora` | Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0) |
| Piero 01 | `desembolsos-por-canal` | mensual | mish | storage | `reportes.mensuales.piero.r01_desembolsos_por_canal` | Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT) |
| Piero 02 | `fondeo-estable` | mensual | mish | storage | `reportes.mensuales.piero.r02_fondeo_estable` | Estadística de tramo / Fondeo estable (Eddy Martínez) |
| Piero 03 | `heredados-pdm` | mensual | slc | slc | `reportes.mensuales.piero.r03_heredados_pdm` | Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar |
| Piero 04.1 | `contratacion-electronica` | mensual | mish | storage | `reportes.mensuales.piero.r04_1_contratacion_electronica` | Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto) |
| Piero 04.2 | `clientes-rurales-migrantes` | mensual | mish | storage | `reportes.mensuales.piero.r04_2_clientes_rurales_migrantes` | Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres |
| Piero 05.1 | `giovanni-captaciones` | mensual | mish | storage | `reportes.mensuales.piero.r05_1_giovanni_captaciones` | Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones |
| Piero 05.2 | `giovanni-seguros` | mensual | mish | storage | `reportes.mensuales.piero.r05_2_giovanni_seguros` | Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar» |
| Piero 05.3 | `giovanni-cartera-agro` | mensual | mish | storage | `reportes.mensuales.piero.r05_3_giovanni_cartera_agro` | Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior) |
| Piero 06 | `saca-tu-garra` | mensual | mish | storage | `reportes.mensuales.piero.r06_saca_tu_garra` | Saca tu garra (Giancarlos): entregar 8:00–8:30 AM |
| Piero 07 | `saldo-medio-vigente` | mensual | mish | storage | `reportes.mensuales.piero.r07_saldo_medio_vigente` | Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios |
| Piero 08 | `tapp-saldo-medio-territorio` | mensual | mish | storage | `reportes.mensuales.piero.r08_tapp_saldo_medio_territorio` | TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy) |
| Piero 09.1 | `michael-captaciones` | mensual | mish | storage | `reportes.mensuales.piero.r09_1_michael_captaciones` | Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos) |
| Piero 09.2 | `michael-castigos` | mensual | mish | storage | `reportes.mensuales.piero.r09_2_michael_castigos` | Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos) |
| Erick 01 | `productos-verdes` | mensual | slc | slc | `reportes.mensuales.erick.r01_productos_verdes` | Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas |
| Erick 02 | `clientes-jovenes` | mensual | slc | slc | `reportes.mensuales.erick.r02_clientes_jovenes` | Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años |
| Erick 03.1 | `bancarizados` | mensual | rcc, slc | propia (ver módulo) | `reportes.mensuales.erick.r03_1_bancarizados` | Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio |
| Erick 03.2 | `bancarizados-producto` | mensual | slc | propia (ver módulo) | `reportes.mensuales.erick.r03_2_bancarizados_producto` | Bancarizados por producto (clientes nuevos con desembolso) |
| Erick 03.3 | `clientes-extranjeros` | mensual | slc, rcc | propia (ver módulo) | `reportes.mensuales.erick.r03_3_clientes_extranjeros` | Clientes por nacionalidad: créditos, pasivos y seguros |
| Erick 03.4 | `indicadores-clientes` | mensual | slc | propia (ver módulo) | `reportes.mensuales.erick.r03_4_indicadores_clientes` | Indicadores de clientes para el Directorio |

## Pruebas (26 archivos)

- `tests/test_app.py`
- `tests/test_cli_tablas.py`
- `tests/test_config.py`
- `tests/test_correo.py`
- `tests/test_db.py`
- `tests/test_ejecuciones.py`
- `tests/test_ejecutor.py`
- `tests/test_entorno.py`
- `tests/test_entrega_correo.py`
- `tests/test_esquemas.py`
- `tests/test_excel.py`
- `tests/test_fechas_corte.py`
- `tests/test_formatos_reportes.py`
- `tests/test_imagen.py`
- `tests/test_notificaciones.py`
- `tests/test_r04_1_cmg_mora.py`
- `tests/test_registro.py`
- `tests/test_reglas_fecha.py`
- `tests/test_reportes_lote.py`
- `tests/test_servicios.py`
- `tests/test_servidores_bases.py`
- `tests/test_sesion.py`
- `tests/test_tablas.py`
- `tests/test_validacion_masiva.py`
- `tests/test_validar_gobernanza.py`
- `tests/test_verificacion.py`
