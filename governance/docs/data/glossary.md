# Glosario

| Término | Significado |
|---|---|
| **MIS** | Información de gestión: área consumidora de la mayoría de reportes |
| **Fecha de corte** | Último día del periodo reportado. Fin de mes, o el día hábil anterior si cae feriado |
| **Saldo medio vigente** | Suma de saldos diarios ÷ días del mes; domingos/feriados repiten el saldo del día hábil anterior |
| **Saldo puntual** | Saldo a una fecha concreta |
| **CMG Mora** | Reporte diario de recaudo y provisiones de mora; lunes toma el sábado |
| **SBTVRIE001** | Tabla destino `[storage].[com_act]` (servidor MISH) de los INSERTs de CMG Mora; el TXT se carga allí fuera de este proyecto |
| **TER-GRU-COR** | Llave territorio-grupo-corredor para asignar `SCODREL` |
| **RCC** | Registro consolidado de créditos (deuda en el sistema financiero) |
| **Cliente exclusivo / bancarizado** | Cliente cuya deuda en RCC está 100 % en Financiera Confianza |
| **CE** | Contratación electrónica (canal CT) frente a agencia física (BT) |
| **PDM** | Cartera heredada (reporte Heredados PDM) |
| **TAPP / TPP** | Stock y saldo medio vigente por territorio |
| **Linked server `rcc_cd`** | Acceso desde `slc` a RCC sin conexión directa |
| **Línea base** | Deuda de gobernanza congelada ([ADR-0003](../architecture/adr/ADR-0003-linea-base-de-gobernanza.md)) |
| **RCODREP** | Código de un reporte del MIS en el catálogo (p. ej. `SEL_EFEC_01`); lo ejecuta un procedimiento almacenado |
| **SP** | Procedimiento almacenado de SQL Server que ejecuta un reporte del MIS |
| **Diccionario** | Repo `DICCIONARIO`: para cada RCODREP, qué SP ejecuta, qué tablas usa y qué columnas ([contrato](./diccionario.md)) |
| **Fecha por confirmar** | Tabla registrada con `confianza = por_confirmar`: su columna de fecha no está validada, así que no se comprueba si llegó al corte |
| **Marca «Creado desde la web»** | Texto del docstring de un reporte creado desde la web; solo esos se pueden borrar desde ahí ([ADR-0018](../architecture/adr/ADR-0018-reportes-desde-la-web.md)) |
