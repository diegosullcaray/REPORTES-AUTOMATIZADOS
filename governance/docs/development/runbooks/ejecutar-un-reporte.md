# Ejecutar un reporte — proceso estándar

Los 7 pasos valen para cualquier reporte. Sustituye `<reporte>` por su nombre (`python main.py listar`).

## 0. Una vez por sesión
```bash
.venv\Scripts\activate
python main.py probar-conexiones          # los 3 servidores deben decir OK (mish, slc, rcc)
```
Si alguna falla: revisa `.env` y la VPN/red ([setup](../setup-guide.md)). No sigas.

## 1. Define la fecha de corte (en el `.env`)
Los reportes los ejecutas tú cuando lo necesites; **nada corre solo**. La fecha de corte la escribes en tu `.env`:

```ini
FECHA_CORTE_MENSUAL=2026-09-30     # reportes mensuales: último día del mes (feriado: día hábil anterior)
FECHA_CORTE_DIARIA=2026-10-05      # reportes diarios (opcional)
```
Prioridad: `--fecha-corte AAAA-MM-DD` en el comando **>** `.env` **>** (solo diarios) día anterior, lunes ⇒ sábado. Cada reporte imprime al inicio `Fecha de corte: … (de dónde salió)`; confírmala antes de seguir.
Los reportes por mes (`bancarizados-producto`, `indicadores-clientes`) toman el mes de `FECHA_CORTE_MENSUAL`, o `--mes AAAA-MM`.

## 2. ¿Qué tablas usa y están al día?
```bash
python main.py tablas <reporte>              # lista (no se conecta)
python main.py tablas <reporte> --verificar  # consulta MAX(fecha) por tabla al corte del .env (solo SELECT)
```
Estados: `OK` · `DESACTUALIZADA` (la última fecha cargada es anterior al corte) · `NO EXISTE` (tabla del día/mes aún no creada) · `SIN CONTROL` (catálogos y vistas: no se valida por fecha) · `ERROR` (revisar detalle).

- Todo `OK` ⇒ paso 4.
- Algo `DESACTUALIZADA` / `NO EXISTE` ⇒ paso 3. **No ejecutes el reporte con tablas viejas**: el resultado sale plausible y equivocado.

## 3. Pedir la actualización (si hace falta)
```bash
python main.py solicitud-actualizacion <reporte> --verificar
```
Imprime el mensaje listo para enviar a quien actualiza en Producción (también queda en `data/outputs/solicitudes/`). Detalle: [solicitud de actualización](./solicitud-actualizacion-tablas.md). Cuando confirmen, vuelve al paso 2.

## 4. Ejecuta
```bash
python main.py <reporte>                     # usa la fecha del .env; --fecha-corte AAAA-MM-DD la cambia solo esta vez
python main.py <reporte> --help              # opciones del reporte
```

## 5. Valida antes de entregar
- ¿El log mostró errores o avisos? Un aviso de «sin datos» **no** es un resultado válido salvo que el reporte lo permita (Castigos vacío sí; Captaciones vacío no).
- Conteo de filas y fecha de corte del archivo de `data/outputs/<reporte>/` coinciden con lo esperado.
- Compara 1–2 cifras con el mes/día anterior (orden de magnitud).
- Reglas propias del reporte: ver su guía y el [contrato de reportes](../../data/contracts/reporting-contracts.md).

## 6. Entrega
Según el [catálogo](../../business/domain-catalog.md): destinatarios, formato y texto del correo. Los archivos de `data/outputs/` contienen datos de clientes: solo a los destinatarios autorizados.

## 7. Registro
Anota en la bitácora del equipo: reporte, corte, hora, tablas que estuvieron desactualizadas y a quién se pidió. Si algo falló, usa la [plantilla de bug](../../templates/bug-report.md) y [incidentes](../../evidence/quality/incidents.md).

## Reglas de oro
1. Nunca ejecutar con una tabla `DESACTUALIZADA`.
2. Nunca editar el SQL a mano para cambiar la fecha: se pasa por parámetro.
3. No ejecutar `cmg-mora` dos veces en paralelo (trunca `CMGMora_Recaudo`).
4. Nunca pegar credenciales ni datos de clientes en chats o tickets.
