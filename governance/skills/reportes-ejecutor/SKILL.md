---
name: reportes-ejecutor
description: Cómo se construye un reporte ejecutable (.py) con el ejecutor común: ReporteLote, tokens de fecha, hojas, validaciones y exportación a Excel. Usar al crear o modificar un reporte.
---

# Reporte ejecutable = un módulo `.py`

No hay carpeta `sql/`: la lógica de cada reporte vive **en su módulo** (`src/reportes/<diarios|mensuales>/<reporte>.py`) y el ejecutor común (`reportes/comun/ejecutor.py`) hace lo demás.

```python
from ..comun.ejecutor import Hoja, ReporteLote, correr

SQL = r"""
declare @fec date = '@@F_ISO@@'          -- tokens, nunca fechas literales
select ... from storage.com_act.hcda001 where HFECPRO = @fec
"""

REPORTE = ReporteLote(
    comando="mi-reporte", descripcion="…", frecuencia="mensual", servidor="mish", base="storage", sql=SQL,
    hojas=(Hoja("Resumen", columna_fecha="HFECPRO"),),   # opcional: nombre de cada resultado y validación de fecha
)

def main(argv=None) -> int:
    return correr(REPORTE, argv)
```

## Qué hace `correr()` (igual para todos)
1. **Conexión** al servidor del reporte (`mish`/`slc`/`rcc`) y a **su** base (`base=`), sin credenciales en código.
2. **Tablas al corte**: compara `MAX(fecha)` de cada tabla del reporte con el corte. Si falta alguna: no ejecuta, lista cuáles, guarda el mensaje para Producción y sale con código 3.
3. Ejecuta el lote en una sesión (tablas `#temp`, `USE`, `GO`, `EXEC`) y recoge **todos** los resultados.
4. **Datos**: todo vacío ⇒ error (salvo `vacio_valido=True`); `columna_fecha` del resultado < corte ⇒ error; hoja vacía ⇒ aviso.
5. **Excel** con el formato del legado ([formato Excel](../../docs/data/formato-excel.md)): una hoja (Tabla de Excel, estilo `TableStyleMedium2`) por resultado + los resúmenes que declare; **sin hoja de control**. El nombre sigue el de los adjuntos históricos (`archivo="Desembolsos_canal_{AAAAMMDD}"`; tokens `{MES}`, `{mes3}`, `{AA}`…). `hojas=(Hoja("Nombre"),)` nombra cada resultado; `resumenes=(Resumen(…),)` añade un resumen jerárquico; `libro_compartido=True` si varios comandos alimentan el mismo archivo.

## Tokens de fecha (se resuelven por `--fecha-corte`)
| Token | Valor |
|---|---|
| `@@F@@` / `@@F_ISO@@` | corte `AAAAMMDD` / `AAAA-MM-DD` |
| `@@F_ANT@@` / `@@F_ANT_ISO@@` | fin del mes anterior |
| `@@F_INI@@` | primer día del mes del corte |
| `@@F_MENOS3@@` | fin de mes, 3 meses antes |

La regla `fechas-fijas-en-sql` bloquea fechas literales en el T-SQL.

## Reglas
- El `servidor` y la `base` deben coincidir con el mapa de [servidores y bases](../../docs/data/servidores-y-bases.md) (`storage` vive en `mish`, no en `slc`); la regla `servidor-coherente` lo exige.
- Un reporte que **crea/borra tablas permanentes** declara `escribe_en_bd=True` (exige `--confirmar-escritura`).
- Un resultado legítimamente vacío (p. ej. Castigos) declara `vacio_valido=True`.
- Toda tabla que consulte va en `src/reportes/tablas.py` (`TABLAS` y `USO`): sin eso no hay verificación de frescura ni mensaje a Producción (regla `tabla-sin-registrar`).
- Reportes con lógica Python propia (CMG Mora, Bancarizados…) siguen el mismo contrato: `main(argv) -> int`, `db.py`, tablas registradas.
