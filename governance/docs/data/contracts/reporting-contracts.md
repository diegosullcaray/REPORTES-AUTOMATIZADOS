# Contrato: reportes

| Aspecto | Regla |
|---|---|
| Entrada | Fecha por CLI (`--fecha-corte AAAA-MM-DD` fin de mes, `--mes AAAA-MM`); jamás editando el SQL a mano |
| Salida | `salidas/<reporte>/…` (Excel/TXT); configurable con `REPORTES_DIR_SALIDAS` |
| Aborto | Variable crítica en 0 / tabla fuente inexistente / sin filas ⇒ se detiene y avisa; no genera archivo parcial |
| Vacío vs error | Resultado vacío válido se informa como tal; excepción SQL nunca se presenta como vacío |
| Reglas de fecha | Lunes ⇒ sábado; fin de mes feriado ⇒ día hábil anterior; saldo medio repite saldo en días sin data |
| Código de salida | `main(argv) -> int`: 0 éxito, ≠0 fallo |

## Reglas por reporte (heredadas)

| Reporte | Regla crítica |
|---|---|
| CMG Mora | abortar si `SSTKPROV` o `SGASPROVCART` = 0; constantes `SRECCAST12M`, `SGASPROVBRUTO12M` fijas del periodo |
| Saldo medio vigente | si las 2 consultas difieren, vale la 2.ª (duplicados de asesores) |
| Heredados PDM | validar que Cubo y PDM estén completos a la fecha antes de ejecutar |
| Seguros (Giovanni) | valores en 0 se etiquetan `sin asignar` |
| Castigos / Michael Palacios | `Castigos` vacío puede ser válido; `Captaciones` siempre debe traer datos |
| Cartera Agro | requiere dos cortes: mes actual y mes anterior |
