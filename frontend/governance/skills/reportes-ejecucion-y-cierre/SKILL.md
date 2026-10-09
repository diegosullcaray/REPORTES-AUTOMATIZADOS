---
name: reportes-ejecucion-y-cierre
description: Cómo ejecutar un reporte y el cierre de mes: verificar que las tablas estén al corte, pedir actualización a Producción, ejecutar, validar y entregar. Usar antes de correr cualquier reporte o al armar el cierre.
---

# Ejecución y cierre de mes

```bash
# .env: FECHA_CORTE_MENSUAL=AAAA-MM-DD (y FECHA_CORTE_DIARIA); --fecha-corte la cambia solo esa vez
python main.py probar-conexiones
python main.py tablas <reporte> --verificar                     # ¿al día?
python main.py solicitud-actualizacion <reporte> --verificar    # mensaje para Producción
python main.py <reporte>                                        # lo ejecutas tú, solo con todo OK
```

1. **Nunca** ejecutes con tablas `DESACTUALIZADA` o `NO EXISTE`: el resultado es plausible y equivocado.
2. Para saber qué tabla usa un reporte, o qué reportes se afectan al actualizar una tabla: [inventario de tablas](../../docs/data/tables-inventory.md).
3. Registra toda tabla nueva en `src/reportes/tablas.py` (la regla `tabla-sin-registrar` bloquea si falta).
4. Una columna de fecha con confianza `convencion` hay que validarla con el DBA y subirla a `confirmada`.
5. Guías completas: [runbooks](../../docs/development/runbooks/README.md) (proceso estándar, cierre de mes, solicitud, y una por reporte).
