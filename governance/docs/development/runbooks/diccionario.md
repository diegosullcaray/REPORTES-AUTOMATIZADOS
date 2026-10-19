# Diccionario — cómo usarlo y mantenerlo al día

Decisión y alcance: [ADR-0017](../../architecture/adr/ADR-0017-modulo-diccionario.md). Contrato del archivo que lee: [diccionario de datos](../../data/diccionario.md).

## Antes de empezar

1. El repo `DICCIONARIO` clonado **junto a este** (`…/DD/DICCIONARIO` y `…/DD/REPORTES-AUTOMATIZADOS`), o `DICCIONARIO_DIR` en `backend/.env` con su ruta. Sin él la web responde «No encontré el diccionario en …».
2. Para los procesos: `node` y `npm` en el `PATH` de quien arranca la API (Node 20+). Si falta, el log del proceso dice «No encuentro npm».

## Las pantallas (menú lateral › Diccionario)

| Pantalla | Para qué |
|---|---|
| **Resumen** (`/diccionario`) | Tres gráficos: *avance de la documentación* por base (validados · extraídos · pendientes), *calidad* (errores y avisos por regla) y *lo que aporta a tus reportes*: cuántas de tus tablas tienen ficha, las columnas de fecha por confirmar y las tablas que más reportes del MIS leen y los tuyos no (pulsa una barra para abrirla). Cada gráfico trae «Ver como tabla» |
| **Reportes del MIS** (`/diccionario/reportes`) | Una tarjeta por base de datos. Al entrar (`?base=`): pestaña **Procedimientos** (con los reportes que los ejecutan) y pestaña **Tablas** que ocupa (las que guarda y las que sus procedimientos leen de otras bases; filtro «viven en esta base» / «de otras») |
| Detalle de un reporte | Procedimiento, parámetros, tablas con las columnas que usa (las de fecha resaltadas), pantallas del front y hallazgos |
| Detalle de una tabla | Columnas, qué reportes del MIS la leen y **cómo la registran tus reportes** (`tablas.py`: tipo, columna de fecha, confianza) |
| **Procesos** (`/diccionario/procesos`) | Lanza los comandos del otro repo, con historial y log en vivo |

## Los procesos

| Proceso | Comando (en el repo `DICCIONARIO`) | Qué toca | Cuándo |
|---|---|---|---|
| Regenerar el diccionario | `npm run generar` | reescribe `diccionario/`, `errores/`, `extraccion/sql/` y `.claude/` | después de cambiar la fuente (`extraccion/fuente/`, procedimientos extraídos) |
| Verificar la calidad | `npm run verificar` | nada | antes de commitear allá; falla ante errores nuevos o algo roto |
| Probar el analizador T-SQL | `npm test` | nada | tras tocar el analizador |

Solo se corre uno a la vez; los demás botones se deshabilitan y, si dos peticiones llegan juntas, la segunda recibe «Ya hay un proceso del diccionario en curso». Después de `generar`, el Resumen se actualiza solo (la API relee el archivo cuando cambia su fecha). **Revisa el `git diff` de `DICCIONARIO` después de `generar`.**

La **extracción desde SQL Server** (`python extraccion/herramientas/bd.py …`) no se lanza desde la web: se hace en una consola, siguiendo la guía de ese repo.

## Qué hacer con lo que muestra

- **Fecha por confirmar** (Resumen › lo que aporta): abre la tabla, mira la columna candidata y confírmala en `src/modulos/reportes/dominio/tablas.py` (`confianza` → `confirmada`); luego `python governance/scripts/generar_inventario.py`.
- **Tablas que el MIS usa y tú no**: candidatas para un reporte nuevo; su detalle trae las fechas disponibles para el corte.
- **Errores «nuevos»** de calidad: son del repo `DICCIONARIO` (SP o tablas que cambiaron en producción); se corrigen allá (su carpeta `errores/` dice dónde), no aquí.

## Problemas conocidos

| Síntoma | Causa | Qué hacer |
|---|---|---|
| El proceso termina con código 134 y `Assertion failed: ncrypto::CSPRNG` | `node` no arranca en Windows sin `SYSTEMROOT` | ya cubierto: el lanzador la conserva (en mayúsculas). Si reaparece, revisa `_ENTORNO_MINIMO` de `infraestructura/lanzador.py` |
| `Verificar` termina «Con error» | el repo `DICCIONARIO` tiene enlaces rotos (p. ej. `modificaciones/nueva tarea/variables.md`) | corregir esos enlaces en ese repo; no es un fallo de esta app |
| Gráficos vacíos o 404 | no está la carpeta `DICCIONARIO` | ver «Antes de empezar» |
