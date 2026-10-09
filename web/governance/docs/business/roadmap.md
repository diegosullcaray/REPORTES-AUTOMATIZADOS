# Roadmap

1. **Inmediato**: rotar credenciales expuestas ([remediación](../security/remediation-plan.md)).
2. **Primera ejecución real** de cada reporte de lote comparando contra la salida manual del mes anterior; fijar nombres de hoja y obligatorias.
2b. Automatizar el envío por correo de los Excel (hoy se entregan a mano).
3. Extraer a `comun/` `Periodo`/`Mes`, `cronometro`, `exportar_excel`, caché.
4. Dar nombre descriptivo a las hojas de cada reporte tras la primera ejecución real (hoy `Resultado_N`) y marcar cuáles son obligatorias.
5. (Descartado) Programar ejecución automática: los reportes los ejecuta una persona bajo demanda.
6. Pruebas de reglas de fecha (lunes→sábado, feriado→hábil anterior).

## Pendientes abiertos (tarea de gobernanza)
- `heredados-pdm` (Piero 03): definir su formato de salida.
- `cmg-mora` (diaria 04.1): la tarea indica que «no se puede ejecutar manualmente»; falta aclarar a qué se refiere (¿quién lo ejecuta, cuándo, con qué permisos?) antes de cambiar su flujo.
- Rotar las credenciales del correo MIS y del webhook de Google Chat ([SEC-004](../security/findings.md)).
