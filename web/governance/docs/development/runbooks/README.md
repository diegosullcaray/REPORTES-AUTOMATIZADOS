# Runbooks — cómo ejecutar los reportes

Guías operativas paso a paso. Úsalas **dentro del entorno** (`.venv` activado, `.env` completo).

| Guía | Cuándo |
|---|---|
| [Proceso de cierre de mes](./proceso-cierre-de-mes.md) | inicio de mes: qué reporte primero, qué tablas deben estar cargadas |
| [Ejecutar un reporte (proceso estándar)](./ejecutar-un-reporte.md) | **cualquier** reporte: pre-vuelo → tablas → ejecución → validación → entrega |
| [Interfaz web](./interfaz-web.md) | el mismo procedimiento desde el navegador, con vista previa de las salidas |
| [Pedir actualización de tablas a Producción](./solicitud-actualizacion-tablas.md) | una tabla no llegó al corte |
| [**Catálogo de comandos**](./comandos.md) | los 22 comandos: tablas críticas, salida, avisos (generado) |
| [`cartera-sin-asignar`](./cartera-sin-asignar.md) | diario: Excel + imagen + **correo (prueba → conforme → todos)** |
| [`cmg-mora`](./cmg-mora.md) | diario |
| [`bancarizados`](./bancarizados.md) | mensual |
| [`bancarizados-producto`](./bancarizados-producto.md) | mensual |
| [`clientes-extranjeros`](./clientes-extranjeros.md) | mensual |
| [`indicadores-clientes`](./indicadores-clientes.md) | mensual |

Todos los reportes comparten el mismo flujo (conexión → tablas al corte → datos → Excel); el [procedimiento manual heredado](../../business/procedimientos_manuales_legado.md) queda como referencia de destinatarios y formato de entrega.
Qué tabla usa cada reporte: [inventario de tablas](../../data/tables-inventory.md).
