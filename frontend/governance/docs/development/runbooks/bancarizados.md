# Runbook: `bancarizados` (mensual)

**Conexiones**: `rcc` (deuda en el sistema) + `slc` (productos). **Salida**: `data/outputs/bancarizados/Bancarizados_<AAAAMMDD>.xlsx` con 4 hojas: `exclusivos_total`, `productos_total`, `productos_nuevos`, `territorio`.

## Antes
```bash
python main.py tablas bancarizados --verificar
```
Críticas: `rccdet{yyyymmdd}`, `rcccab{yyyymmdd}` (RCC del cierre), `ccd{yyyymmdd}` y `intcom.dbo.ccd` (Fecha_Cierre).

## Ejecutar
```bash
python main.py bancarizados                       # corte = FECHA_CORTE_MENSUAL del .env
python main.py bancarizados --fecha-corte 2026-09-30   # o una fecha puntual
python main.py bancarizados --sin-cache      # fuerza reconsulta
python main.py bancarizados --copiar productos_nuevos
```
`--fecha-corte` debe ser **fin de mes** (si no, error). Las extracciones se cachean en `data/outputs/bancarizados/cache/*.pkl`: si corregiste datos en origen, usa `--sin-cache`.

## Validar
Revisa el diagnóstico de cruce RCC↔SLC en el log (clientes sin match); conteo de exclusivos coherente con el mes anterior.
