# Procedimientos manuales heredados (NOTAS.docx)

Transcripción de las notas de traspaso del legado. Sirven como especificación para automatizar cada reporte. Origen: `docs/LEGADO/02 TAREAS MENSUALES/`.


---

## 01 DESEMBOLSOS POR CANAL

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/01 DESEMBOLSOS POR CANAL/NOTAS.docx`_

1. REPORTE "DESEMBOLSOS POR CANAL"

Qué contiene: Detalla los desembolsos realizados en el mes, especificando qué se hizo por "Contratación electrónica" (App/Agencia - Código: CT) y qué por "Agencia física" (Código: BT).

Solicitantes/Destinatarios: Sergio, Sebastián, Abigail (copia), Michel (copia). Nota: Ya no se envía a Merly.

Procedimiento:

Abrir la query (consulta SQL).

Cambiar la fecha en el código al último día del mes a reportar (Ej: 20260731 para julio).

IMPORTANTE: Si no tienes acceso al servidor de producción, debes enviarle esta query por chat/correo a Abigail (Abi) y pedirle: "Abi, por favor ejecuta esta query y mándame el resultado". (Es mejor hacer esto que pedirle que sincronice múltiples tablas).

Copiar el resultado con cabeceras.

Pegar en un Excel nuevo y guardarlo con el nombre: Desembolso por canal_YYYYMMDD (ej. 20260731).

Redactar el correo, adjuntar el archivo y enviarlo.


---

## 02 ESTADÍSTICA DE TRAMO - FONDEO ESTABLE

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/02 ESTADÍSTICA DE TRAMO - FONDEO ESTABLE/Documento sin título.docx`_

2. REPORTE "ESTADÍSTICA DE TRAMO / FONDEO ESTABLE"

Solicitantes/Destinatarios: Eddy Martínez (se lo envías directamente), con copia a Michael y Abigail.

Frecuencia: Inicio de cada mes (ej. día 3).

Características Especiales: Extrae información de una tabla tipo WAS (datos de fechas puntuales), acumulando información de cortes pasados.

Procedimiento:

Cambiar la fecha al cierre del mes (ej. 7 y 31).

Ejecutar la consulta. (No debería haber problema de falta de data si lo haces el día 3, ya que jala datos del cierre).

Copiar el resultado que arroje el sistema.

Abrir el formato Excel establecido, pegar los datos.

Guardar y enviar por correo.


---

## 03 HEREDADOS PDM (Heredado de Michael)

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/03 HEREDADOS PDM (Heredado de Michael)/NOTAS.docx`_

3. REPORTE "HEREDADOS PDM" (Heredado de Michael)

Solicitantes/Destinatarios: Carla Campo (Gerente de Riesgos), Ricardo Lazo, Álvaro Calderón, con copia a Michael.

Condición Crítica antes de ejecutar: No puedes hacer este reporte a ciegas. Antes de ejecutarlo, debes validar que el Cubo y las tablas de PDM (vistas en la capacitación del día anterior) estén llenos y actualizados a la fecha de corte. Si faltan datos en el cubo, el reporte saldrá mal.

Procedimiento:

Validar que la información del Cubo y PDM esté completa.

Conectarte al Servidor 213 (debes tener acceso habilitado por Abi).

Cambiar la fecha de la consulta al cierre del mes.

Ejecutar la consulta SQL.

Abrir el formato Excel de Michael.

Borrar toda la información del mes anterior (las columnas con datos).

Copiar el nuevo resultado de la base de datos y pegarlo.

Guardar el archivo con el nombre indicando el mes y año (Ej: PDM Julio 2026).

Redactar correo, adjuntar Excel y enviar a la lista mencionada.


---

## 04 RATIO CE, clientes Nuevos y Migrantes ( manuel  siccha)

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/04 RATIO CE, clientes Nuevos y Migrantes ( manuel  siccha)/NOTAS.docx`_

📆 REPORTES DE CIERRE / INICIO DE MES

1. Contratación Electrónica (Cliente Nuevo y Migrante)

Destinatario: Manuel (y Michel).

Pasos: Cambiar el rango de fechas en la query (ej. del 07 al 31). Ejecutar.

Envío: Mandar correo adjuntando el reporte. En el cuerpo del correo detallar: Número de operaciones y Monto desembolsado.

2. Clientes Rurales

Pasos: Cambiar fechas y ejecutar. Pegar los resultados con cabecera en un Excel.

Procesamiento: Crear una Tabla Dinámica. Filas: Fecha. Columnas: Migrante/Peruano y Rural. Valores: Suma.

Envío: Ocultar las filas anteriores, tomar captura de pantalla solo del último mes y enviarla pegada en el cuerpo del correo.

3. Reporte Seguros (Multirriesgo)

Frecuencia: Lunes a primera hora (para tener el cierre del domingo).

Pasos: Ir a la página (Actividad diaria -> Seguros -> Reporte Seguro). Filtrar por sector "Multirriesgo".

Datos a extraer: Operaciones, Seguros Multirriesgo y Porcentaje de Penetración. Copiar y pegar esos 3 datos.


---

## 2. Reporte Seguros

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/05 Reportes para Giovanni/2. Reporte Seguros/NOTAS.docx`_

2. Reporte Seguros:

Cambiar fechas y ejecutar.

Usar la plantilla/formato establecido: eliminar registros antiguos, copiar la nueva data sin cabeceras y pegar.

Dato clave: A los valores que salgan en cero (0), colocarles la etiqueta "sin asignar".


---

## 3. Cartera Vigente Agro

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/05 Reportes para Giovanni/3. Cartera Vigente Agro/Documento sin título.docx`_

3. Cartera Vigente Agro:

Requiere dos fechas: El cierre del mes actual (ej. 7/31) y el cierre del mes anterior (ej. 6/30). Ojo: Si el fin de mes cae feriado, se usa el día hábil anterior.

Ejecutar en dos partes: La primera va a la hoja "Saldo vigente" (contiene 2 resultados: cierre actual y cierre pasado) y la segunda va a la hoja "Clientes".


---

## 06 Saca tu garra

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/06 Saca tu garra/NOTAS.docx`_

A. Reporte "Saca tu garra"

Solicitante: Giancarlos.

Condición: Es muy especial con la hora. Lo quiere a primera hora (8:00 - 8:30 AM) apenas llegues.

Procedimiento: La query está optimizada. Solo cambias la fecha, ejecutas, limpias el formato Excel, pegas la nueva data y lo envías (por correo o chat). No tienes que esperar los reportes de cierre pesados para esto.


---

## 07 Saldo Medio Vigente - DIANA

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/07 Saldo Medio Vigente - DIANA/NOTAS.docx`_

C. Reporte "Saldo Medio Vigente"

Solicitante: Diana García (trabaja con Víctor Blast).

Procedimiento: Existen 2 consultas (queries) para este reporte para evitar errores por asesores duplicados.

Regla del Saldo Medio: Es la suma de todos los saldos diarios dividida entre el número de días del mes. Importante: Si hay domingos o feriados (días sin data), se debe repetir el saldo del día hábil anterior.

Validación: Ejecutar ambas consultas. Si hay diferencias entre los resultados, confía siempre en la segunda consulta (la de abajo), ya que la primera puede fallar si Abi no ha corregido los duplicados en la base de datos al inicio del día.


---

## 08 TAPP stock TPP MES SALDO MEDIO VIGENTE TERRITORIO

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/08 TAPP stock TPP MES SALDO MEDIO VIGENTE TERRITORIO/NOTAS.docx`_

D. Reporte para Edy

Procedimiento: Ejecutar la parte 1 (histórico) y agregar el mes actual. Luego, ejecutar la parte 2, copiar el bloque que le pertenece al mes evaluado, pegarlo en su Excel y enviárselo (a veces lo pide por chat).


---

## 09 REPORTE MENSUAL MICHAEL PALACIOS

_Fuente: `docs/LEGADO/02 TAREAS MENSUALES/01 - HEREDADO DE PIERO/09 REPORTE MENSUAL MICHAEL PALACIOS/NOTAS.docx`_

E. Reporte Mensual de Michael (Captaciones y Castigos)

Solicitante: Michael / Riesgos / Manuel / Giovanni.

Procedimiento:

Cambiar fechas: Fec 1 (cierre mes anterior) y Fec 2 (cierre mes actual).

Ejecutar consultas de Captaciones y Castigos a la par.

Limpiar el formato Excel y pegar los resultados de Castigos, Captaciones y Clientes.

Nota: No te asustes si "Castigos" sale vacío; hay meses donde simplemente no hay castigos. Captaciones sí debe tener data siempre.
