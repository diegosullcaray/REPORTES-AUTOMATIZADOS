# Roadmap

1. **Inmediato**: rotar credenciales expuestas ([remediación](../security/remediation-plan.md)).
2. **Primera ejecución real** de cada reporte de lote comparando contra la salida manual del mes anterior; fijar nombres de hoja y obligatorias.
2b. Automatizar el envío por correo de los Excel (hoy se entregan a mano).
3. Extraer a `comun/` `Periodo`/`Mes`, `cronometro`, `exportar_excel`, caché.
4. Dar nombre descriptivo a las hojas de cada reporte tras la primera ejecución real (hoy `Resultado_N`) y marcar cuáles son obligatorias.
5. Programar ejecución diaria (Programador de tareas de Windows).
6. Pruebas de reglas de fecha (lunes→sábado, feriado→hábil anterior).
