# Pedir a Producción que actualice una tabla

Escenario típico: es cierre de mes, ejecutas `python main.py tablas <reporte> --verificar` y alguna tabla sale `DESACTUALIZADA` o `NO EXISTE`.

## 1. Identifica exactamente qué pedir
```bash
python main.py solicitud-actualizacion <reporte> --verificar
```
El mensaje lista **solo** las tablas con problema, con su conexión, columna de fecha y última fecha cargada. Se guarda en `data/outputs/solicitudes/`.

Para varias tablas o reportes a la vez, repite por reporte y junta los mensajes, o consulta el [inventario por tabla](../../data/tables-inventory.md) (sección 2) para ver **qué otros reportes** dependen de la tabla que vas a pedir: así una sola solicitud destraba varios reportes.

## 2. Envía el mensaje
Al responsable de carga en Producción (administración de BD). Incluye siempre: tabla completa (`base.esquema.tabla`), fecha de corte requerida, y el estado actual (última fecha). Plantilla: [solicitud de actualización](../../templates/solicitud-actualizacion-tablas.md).

## 3. Espera la confirmación y reverifica
No asumas que «ya cargó»: repite `tablas … --verificar`. Solo con todo `OK` se ejecuta el reporte.

## 4. Si no se puede actualizar
| Situación | Qué hacer |
|---|---|
| Producción no puede cargar hoy | acordar fecha/hora y avisar a los destinatarios del retraso |
| No tienes acceso a producción | pedir que **ejecuten el reporte por ti** (el T-SQL está dentro del módulo `src/reportes/…`, constante `SQL`; `python main.py <reporte>`) y te envíen el Excel; es preferible a pedir sincronizar muchas tablas |
| El cierre cae en feriado | el corte es el día hábil anterior; verifica con ese corte |
| La columna de fecha marcada como `convencion` no existe | el verificador devuelve `ERROR`: confirma el nombre real con el DBA y corrígelo en `src/reportes/tablas.py` (confianza → `confirmada`) |

## 5. Mejora continua
Cada vez que una tabla falle, anótalo en [incidentes](../../evidence/quality/incidents.md). Si descubres una tabla que el reporte usa y no estaba en el inventario, regístrala en `src/reportes/tablas.py` (la regla `tabla-sin-registrar` te lo exige).
