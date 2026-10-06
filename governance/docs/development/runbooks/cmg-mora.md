# Runbook: `cmg-mora` (diario)

**Conexión**: `dw_raw` (escritura en `DW_Raw_v2.dbo.CMGMora_Recaudo`). **Salida**: `salidas/cmg_mora/inserts_<AAAA-MM-DD>.txt` (INSERTs para `[storage].[com_act].[SBTVRIE001]`).

## Antes
```bash
python main.py tablas cmg-mora --verificar        # corte = día anterior (lunes: sábado)
```
Críticas: `dbriesgos.dbo.recaudo_diario_finanzas` (FECHA_CIERRE), `dbriesgos.dbo.gasto_prov_ope_diaria` (FC_DIA) y la tabla del día `dbriesgos.dbo.prov_proy_<yyyymmdd>_0` (debe **existir**). Si falta alguna: [solicitud](./solicitud-actualizacion-tablas.md) a Producción.

## Ejecutar
```bash
python main.py cmg-mora
```
## Qué hace
1. Calcula la fecha (lunes ⇒ sábado). 2. `TRUNCATE` + carga de `CMGMora_Recaudo` del día. 3. Carga constantes y provisiones. 4. Genera el TXT de INSERTs.

## Aborta (sin generar archivo) si
- no hay datos de recaudo para la fecha; - no existe `PROV_PROY_<fecha>_0`; - `SSTKPROV` o `SGASPROVCART` = 0.
Son controles correctos, **no** los saltes: significa que falta carga. Solicita la actualización y reintenta.

## Después
Revisa que el TXT tenga filas; luego se carga en `SBTVRIE001` según el procedimiento vigente. No ejecutar dos veces a la vez.

> Nota: `castigos` (`sql/diarias/cmg_mora/p002_castigos.sql`) sigue manual.
