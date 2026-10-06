# GOBIERNO DEL PROYECTO — REPORTES-AUTOMATIZADOS

Documento rector del entorno Python que automatiza los reportes de Financiera Confianza (Finanzas / Riesgos / MIS).
Se actualiza con cada cambio estructural. Última actualización: 2026-10-06.

## 1. Objetivo
Reemplazar el flujo manual heredado (queries SQL + copiar/pegar en Excel + correo) por reportes reproducibles ejecutados desde una única línea de comandos: `python main.py <reporte> ...`.

## 2. Estructura del repositorio
```
main.py                     Punto de entrada único (listar | probar-conexiones | <reporte>)
.env.example                Plantilla de secretos/conexiones (el .env real NO se versiona)
requirements.txt            Dependencias
GOBIERNO.md                 Este documento
src/reportes/
  config.py                 Rutas + definición de las 3 bases de datos (lee .env)
  db.py                     ÚNICO acceso a BD: leer_sql, conexion_pyodbc, leer_ultimo_resultado
  registro.py               Catálogo de reportes (nombre, módulo, frecuencia, bases)
  comun/                    Utilidades compartidas (reservado: fechas, excel)
  diarios/                  Reportes diarios (cmg_mora)
  mensuales/                Reportes mensuales automatizados (4 migrados)
sql/
  diarias/<reporte>/        SQL de tareas diarias (cmg_mora, cartera_sin_asignar)
  mensuales/<reporte>/      SQL de tareas mensuales (heredados de Piero y de Erick)
plantillas/                 Formatos Excel base (p. ej. cartera_sin_asignar_base.xlsm)
salidas/                    Resultados generados (ignorado por git)
docs/
  procedimientos/           NOTAS.docx del legado transcritas a Markdown
  LEGADO/                   Archivo histórico INTACTO (solo lectura, no se edita)
```

## 3. Las 3 bases de datos
Todas las conexiones se definen en `src/reportes/config.py` y se configuran por `.env`. Ningún script abre conexiones por su cuenta.

| Alias | Servidor | Base | Autenticación | También accesible (3 partes) | Usada por |
|---|---|---|---|---|---|
| `dw_raw` | 172.20.0.70 | DW_Raw_v2 | SQL (`DW_RAW_USER/PASSWORD`) | `dbriesgos` | CMG Mora (diario) |
| `rcc` | 172.20.0.70 | DBRCC | SQL (`RCC_USER/PASSWORD`) | linked server `rcc_cd` desde slc | Bancarizados, Extranjeros (`--pasivos-directo`) |
| `slc` | 172.24.2.213 | slc | Windows (o `SLC_USER/PASSWORD`) | `INTCOM`, `DWH`, `csd`, `DMA`, `storage` | Resto de reportes mensuales |

> Supuesto a validar: los 3 alias se infirieron del legado (servidores 172.20.0.70 y 172.24.2.213 y las bases que consultan los scripts). Si la tercera base prevista es otra (p. ej. INTCOM/DWH como conexión propia), basta añadir una entrada en `BASES` de `config.py`.

Verificación: `python main.py probar-conexiones`.

## 4. Catálogo de reportes

### 4.1 Automatizados (`python main.py listar`)
| Comando | Frecuencia | Bases | Código | SQL embebido/origen |
|---|---|---|---|---|
| `cmg-mora` | Diaria (lunes toma el sábado) | dw_raw | `diarios/cmg_mora.py` | `sql/diarias/cmg_mora/` |
| `bancarizados` | Mensual | rcc, slc | `mensuales/bancarizados.py` | `sql/mensuales/finanzas_bancarizados/` |
| `bancarizados-producto` | Mensual | slc | `mensuales/bancarizados_producto.py` | idem |
| `clientes-extranjeros` | Mensual | slc, rcc | `mensuales/clientes_extranjeros.py` | `sql/mensuales/finanzas_extranjeros/` |
| `indicadores-clientes` | Mensual | slc | `mensuales/indicadores_clientes.py` | `sql/mensuales/finanzas_info_general/` |

### 4.2 Pendientes de automatizar (solo SQL migrado a `sql/`)
Procedimiento manual en `docs/procedimientos/procedimientos_manuales_legado.md`.

| Carpeta en `sql/mensuales/` | Origen legado | Solicitante / nota clave |
|---|---|---|
| `desembolsos_por_canal` | Piero 01 | Cambiar fecha a fin de mes; canales CT/BT |
| `fondeo_estable` | Piero 02 | Eddy Martínez; inicio de mes |
| `heredados_pdm` | Piero 03 | Validar Cubo/PDM completos antes de ejecutar |
| `ratio_ce_nuevos_migrantes` | Piero 04 | Manuel Siccha; CE + clientes rurales/migrantes |
| `reportes_giovanni` | Piero 05 | Captaciones, Seguros (0 → "sin asignar"), Cartera Agro (2 cierres) |
| `saca_tu_garra` | Piero 06 | Entregar 8:00–8:30 AM |
| `saldo_medio_vigente` | Piero 07 | Si difieren las 2 queries, vale la 2.ª |
| `tapp_saldo_medio_territorio` | Piero 08 | Parte 1 histórico + parte 2 mes evaluado |
| `reporte_michael_palacios` | Piero 09 | Captaciones siempre con datos; Castigos puede ir vacío |
| `clientes_jovenes`, `productos_verdes` | Erick 01/02 | Manuel Siccha |
| `finanzas_*` | Erick Reporte_finanzas | SQL base de los 3 reportes ya automatizados |
| `sql/diarias/cartera_sin_asignar` | Diarias 02 | Plantilla en `plantillas/diarias/` |

## 5. Decisiones de la reorganización (2026-10-06)
1. **Legado intacto**: `docs/LEGADO/` se conserva como archivo; el código nuevo vive en `src/` y `sql/` (copias normalizadas, nombres en snake_case sin espacios).
2. **Duplicados detectados** en `HEREDADO DE ERICK`: `Reporte_finanzas/` (versión parcial) y `Reportes Finanzas-2026...-001/` (versión completa, incluye `bancarizados_producto.py` e `indicadores_clientes.py`), además de copias de `jovenes.sql` y `Info_prod_verdes_slc.sql`. Se usó la versión completa; el resto es redundante y puede archivarse.
3. **Una sola capa de conexión** (`db.py`): se eliminaron 5 implementaciones divergentes de `crear_engine`/`conectar`.
4. **Salidas** centralizadas en `salidas/<reporte>/` (configurable con `REPORTES_DIR_SALIDAS`), en lugar de rutas `D:\...` fijas.
5. **Cachés `.pkl` y TXT de salida históricos** (CMG Mora, bancarizados) siguen solo en `docs/LEGADO/`; no se migran por ser datos generados.

## 6. Seguridad — hallazgos y reglas
- **Hallazgo crítico**: el legado contenía credenciales en texto plano (usuario `master` en `cmg_mora`/`script.py` y un usuario de lectura en los scripts de Bancarizados/Extranjeros), y tales credenciales **siguen en el historial de git y en `docs/LEGADO/`**. No se copiaron al código nuevo. **Acción requerida**: rotar esas contraseñas y, si el repositorio es compartido, purgar el historial.
- Regla: ningún secreto en código ni en el repositorio; solo `.env` (ignorado por git).
- `cmg_mora` usa un usuario con permisos de escritura (`TRUNCATE`/`INSERT`/`UPDATE` en `DW_Raw_v2`). Recomendado: usuario dedicado con permisos mínimos, distinto del de lectura.
- Los reportes de lectura (`rcc`, `slc`) deben usar cuentas de solo lectura.
- Las salidas contienen datos de clientes: `salidas/` no se versiona.

## 7. Operación
```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt          # requiere ODBC Driver 17 for SQL Server
copy .env.example .env                   # completar credenciales
python main.py probar-conexiones
python main.py cmg-mora
python main.py bancarizados --fecha-corte 2026-06-30
```

## 8. Convenciones para nuevos reportes
1. SQL en `sql/<frecuencia>/<reporte>/`, cargado con `db.cargar_sql()`; sin credenciales ni rutas absolutas.
2. Código en `src/reportes/<frecuencia>/<reporte>.py` con `main(argv) -> int`.
3. Acceso a datos solo vía `reportes.db` indicando el alias (`dw_raw`/`rcc`/`slc`).
4. Registrar el reporte en `registro.py` y en la tabla 4.1 de este documento.
5. Parámetros de fecha por CLI (`--fecha-corte`, `--mes`), nunca editando el SQL a mano.

## 9. Backlog sugerido
1. Rotar credenciales expuestas (prioridad máxima).
2. Automatizar los reportes de 4.2 empezando por los de mayor frecuencia (Saca tu garra, Desembolsos por canal, Saldo medio).
3. Extraer a `comun/` las utilidades repetidas en los scripts (`Periodo`/`Mes`, `cronometro`, `exportar_excel`, caché).
4. Mover el SQL embebido en los `.py` a `sql/` y cargarlo con `cargar_sql`.
5. Pruebas unitarias de reglas de fecha (lunes → sábado; fin de mes feriado → día hábil anterior).
6. Programar ejecución diaria (Programador de tareas de Windows).
