# Interfaz web

Gestiona los reportes desde el navegador con el mismo procedimiento que la consola. Decisión: [ADR-0011](../../architecture/adr/ADR-0011-interfaz-web.md).

## Arrancar (dos terminales)

```bat
:: 1) API (entorno activado, .env completo)
env\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.app:app --app-dir src --host 127.0.0.1 --port 8000

:: 2) Web (Node 20+)
cd web
npm install
npm run build && npm start        :: o `npm run dev` mientras desarrollas
```

Abre http://localhost:3000. Si la API corre en otro puerto: `set REPORTES_API_URL=http://127.0.0.1:PUERTO` antes de `npm start`.
Si cambias el `.env`, reinicia la API (lo lee al arrancar).

## Secciones

| Sección | Qué muestra |
|---|---|
| **Inicio** | Cortes vigentes del `.env`, métricas de los últimos 7 días (ejecuciones, % de éxito, estados), **avance del cierre de mes** (mensuales con una ejecución correcta para `FECHA_CORTE_MENSUAL` y cuáles faltan) y ejecuciones recientes con acceso al log |
| **Reportes** | Tabla del catálogo (Nº del legado, tipo, responsable, servidor, última ejecución) con buscador, filtro y orden; la lista lateral para entrar a cada reporte |
| **Ejecuciones** | Historial completo: filtros por estado y tipo, orden por columna, columnas a elección, paginación; por fila: **Log** en panel lateral, detalle, ir al reporte, copiar el comando. Se refresca cada 5 s |
| **Configuración** | *General*: cortes, carpetas de entrada/salida y driver que leyó la API. *Bases de datos*: los 3 servidores con **Test de conexión** (uno o todos) |

El pie del sidebar indica si la API responde y cuántas ejecuciones hay en curso; el encabezado muestra la hora de Lima.

## Procedimiento por reporte

Navegación: el sidebar principal (Inicio · Reportes · Ejecuciones · Configuración) se pliega a íconos con el botón del encabezado
o **Ctrl+B**. La pestaña abierta queda en la URL (`?tab=historial`), así se puede compartir o recargar. Dentro de Reportes, la lista (Diarios · Mensuales › Heredados de Piero / Erick, con buscador) se pliega con su
propio botón y recuerda la preferencia. En el celular el sidebar principal se abre desde el encabezado y la lista de reportes
es la pantalla inicial. Las migas muestran dónde estás (`Reportes > Diarios > Cartera sin asignar`).

| Pestaña | Qué hace | Equivale a |
|---|---|---|
| Ejecución | Parámetros (fecha de corte, correo, confirmaciones) → **Ejecutar reporte** → confirmación → **log en vivo** tipo consola | `python main.py <r> --fecha-corte …` |
| Validación de tablas | **Verificar tablas** (solo SELECT). Si falta alguna: mensaje para Producción, **Copiar** o **Guardar** en `data/outputs/solicitudes/` | `tablas <r> --verificar` · `solicitud-actualizacion` |
| Archivos | Excel, imagen y textos de la carpeta del reporte, con **vista previa** (200 filas por hoja) y descarga | `data/outputs/<…>/` |
| Correo (solo `cartera-sin-asignar`) | Estado de la prueba; **Enviar a toda la lista** exige marcar «Revisé el correo de prueba» | `--correo todos --conforme` |
| Historial | Ejecuciones del reporte con su log | — |

**Configuración › Bases de datos**: los 3 servidores (host, autenticación, si hay credenciales en el `.env`, bases) y un
**Test de conexión** por servidor que responde con un aviso de éxito o error. Las credenciales nunca se muestran.

Reglas que la API exige (aunque la web ya las avise):

- Mensual = fin de mes; ninguna fecha de corte en el futuro.
- `tapp-saldo-medio-territorio` exige confirmar la escritura en BD.
- `--forzar` solo aparece si la verificación encontró tablas desactualizadas, y queda escrito en el historial.
- Enviar a todos exige una prueba previa del mismo corte y el conforme; no reenvía si ya se envió.
- Un reporte a la vez: los demás esperan **En cola**.

## Estados de una ejecución

| Estado | Código | Qué hacer |
|---|---|---|
| Correcto | 0 | Revisa los archivos generados (vista previa en la misma página) y entrégalos |
| Error | 1 | Lee la salida: datos vacíos, Excel abierto, error SQL |
| Configuración | 2 | Fecha, `.env`, driver o confirmación faltante |
| Tablas desactualizadas | 3 | Validación de tablas: pide la carga a Producción y vuelve a verificar |

Si la API se reinicia con una ejecución en curso, queda en **Error** con la nota «Interrumpida».

## Estructura

```text
src/api/            app.py (rutas) · esquemas.py (contratos) · servicios.py (casos de uso) · ejecuciones.py (cola)
web/src/app/        rutas: /reportes (layout con el sidebar secundario) · /reportes/[nombre] · /ejecuciones · /ejecuciones/[id] · /configuracion; tokens.css (copia de MIS)
web/src/lib/        api.ts (transporte) · tipos.ts (espejo de esquemas.py) · formato.ts (funciones puras)
web/src/features/   orquestación por pantalla (reportes, ejecuciones, configuracion)
web/src/components/ presentación compartida: app-sidebar, encabezado (migas), pagina, terminal, estados, confirmar; ui/ = shadcn
```

API usada por Configuración: `GET /api/configuracion`, `GET /api/servidores` (sin secretos) y `POST /api/servidores/{nombre}/prueba` (`SELECT 1`).
El historial admite `GET /api/ejecuciones?reporte=…&limite=…` (1–2000, por defecto 200), de la más reciente a la más antigua.
