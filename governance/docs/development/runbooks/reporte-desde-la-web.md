# Crear, completar y borrar un reporte desde la web

Reglas y motivos: [ADR-0018](../../architecture/adr/ADR-0018-reportes-desde-la-web.md). Para un reporte con lógica propia o que escribe en la base, usa la [guía de nuevo reporte](../report-creation-guide.md) (módulo a mano).

## 1. Crear

1. `Reportes` → entra a un **grupo** (los del legado `diarias`, `piero`, `erick`, o uno propio: botón *Nuevo grupo* en el tablero; los propios son siempre mensuales).
2. **Nuevo reporte**: *Nombre (comando)* en minúsculas con guiones (`cartera-sin-asignar`), *Número del legado* (`10` o `10.1`, único dentro del grupo) y *Descripción*.
3. Al crear te lleva a la pestaña **Script** del reporte nuevo. Se generó con una consulta de plantilla (`use storage;` … `select 1 as pendiente`).

Se escriben, en el repo: el módulo (`catalogo/<grupo>/r<NN>_<nombre>.py`, o `catalogo/grupos/<id>/…` en un grupo propio), su test, y las líneas en `dominio/reportes.py`, `dominio/tablas.py` y `dominio/reglas_fecha.py`. La API lo ve sin reiniciar.

## 2. Completar (pestaña Script)

1. Reemplaza la plantilla por tu T-SQL. Reglas que se validan al guardar:
   - Empieza con `use <base>;` (de ahí salen la base y el servidor).
   - Las fechas **solo** con tokens: `@@F@@`, `@@F_ISO@@`, `@@F_ANT@@`… (nunca `'20260731'`).
   - **Solo lectura**: nada de `INSERT/UPDATE/DELETE/SELECT INTO/DROP/TRUNCATE/ALTER/CREATE/MERGE` salvo sobre tablas temporales `#t` o variables `@v`.
2. Mientras el SQL contenga `select 1 as pendiente`, **Ejecutar** responde «Completa el T-SQL…».
3. Las tablas nuevas quedan como `referencia / por_confirmar`: el ejecutor las usa pero avisa `sin control de fecha`. Confirma su columna de fecha en `dominio/tablas.py` (apóyate en el [Diccionario](./diccionario.md): *Resumen › lo que aporta a tus reportes* sugiere candidatas) y la regla en `reglas_fecha.py`.

## 3. Antes de commitear

```bash
python governance/scripts/generar_inventario.py     # actualiza el inventario con el reporte nuevo
python governance/scripts/verificar.py              # gobernanza + inventario + pruebas
```

## 4. Borrar

Menú «⋯» de la tarjeta del reporte, o la papelera de su detalle: pide escribir el nombre del reporte (como en Dokploy). Solo se borran los creados desde la web (los del legado no) y solo sin ejecuciones en cola o en curso. Se quitan el módulo, su test y sus líneas del registro; las filas de tablas se conservan. Un grupo propio se elimina únicamente vacío, desde su «⋯» en el tablero.

## Si algo no deja guardar

| Mensaje | Causa |
|---|---|
| «El T-SQL debe empezar con `use <base>;`» | falta el `use` |
| «El T-SQL trae una fecha literal» / «no usa ningún token» | fechas sin tokens |
| «El T-SQL escribe en la base (…)» | sentencia de escritura fuera de `#temporales` |
| «Un reporte se conecta a un solo servidor» | tablas de dos servidores en la misma consulta |
| «`Creado desde la web` solo la llevan los reportes creados así» | se intentó agregar la marca a un reporte del legado |
