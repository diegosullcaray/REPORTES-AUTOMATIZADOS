# ADR-0010: Orden y responsable del legado en el código y en las salidas; entrega por correo del resumen diario

- Estado: Vigente · Fecha: 2026-10-06 · Origen: `governance/tasks/tarea.md` y `tareasdiarias.md`

## Contexto
El legado se heredó de dos personas (Piero y Erick) y sus carpetas están **numeradas** (`01 DESEMBOLSOS POR CANAL`, `02 …`). Los reportes mensuales estaban todos mezclados en `src/reportes/mensuales/` y las salidas en carpetas sueltas por comando, sin saber de quién era cada uno ni en qué orden. Además, el reporte diario «Cartera sin asignar» se entregaba con una macro de Excel que enviaba correo, con la contraseña de la cuenta de correo y el webhook escritos en la macro.

## Decisión
1. **Estructura por responsable y número del legado**: `src/reportes/mensuales/piero/r01_…` a `r09_…`, `src/reportes/mensuales/erick/r01_…` a `r03_…` y `src/reportes/diarios/r02_…`, `r04_…`. Un número con punto (`04.1`, `04.2`) son sub-reportes de la misma carpeta del legado. `registro.py` guarda grupo, número y carpeta de salida; la regla `registro-sincronizado` exige que módulo y carpeta empiecen por ese número.
2. **Salidas** bajo `data/outputs/`: `mensuales/piero/<NN_nombre>/`, `mensuales/erick/<NN_nombre>/` y `diarias/<NN_nombre>/` (el `.env` fija solo `REPORTES_DIR_OUTPUTS`).
3. **Formato de columnas por reporte** (`Columna`: encabezado, reemplazo de 0/nulos, formato de fecha): `saca-tu-garra` y `fondeo-estable` según la tarea.
4. **Entrega por correo** de `cartera-sin-asignar` (`comun/entrega_correo.py`): primero valida tablas, ejecuta y genera Excel + imagen; envía una **prueba solo a `CORREO_PRUEBA`**; solo con `--correo todos --conforme` envía **la misma prueba aprobada** a la lista y avisa a Google Chat. Credenciales únicamente en `.env`.
5. La fecha por defecto de `cartera-sin-asignar` es siempre ayer (`Date - 1` del legado), sin la regla lunes→sábado de CMG Mora.

## Consecuencias
- Al listar, ejecutar o buscar una salida se sigue la misma secuencia que el legado.
- Renombrar archivos obligó a regenerar la línea base (mismos 38 avisos con rutas nuevas; no hay deuda nueva).
- `heredados-pdm` queda pendiente de formato, y `cmg-mora` tiene una consulta abierta sobre su ejecución manual (ver [roadmap](../../business/roadmap.md)).
- **SEC-004**: las credenciales de la macro habían llegado al repositorio; se ocultaron y deben rotarse.
