# Interfaz web

Gestiona los reportes desde el navegador con el mismo procedimiento que la consola. Decisión: [ADR-0011](../../architecture/adr/ADR-0011-interfaz-web.md).

## Arrancar (dos terminales)

```bat
:: 1) API (desde backend\, entorno activado, .env completo)
cd backend
env\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.app:app --app-dir src --host 127.0.0.1 --port 8000

:: 2) Web (Node 20+, desde la raíz del repo)
cd frontend
npm install
npm run build && npm start        :: o `npm run dev` mientras desarrollas
```

Abre http://localhost:3000 e **inicia sesión con `WEB_USUARIO` y `WEB_CLAVE` del `.env`** (si falta alguno, nadie entra). La sesión dura 8 h,
firmada con `SESION_SECRETO`, y 5 fallos bloquean al usuario 5 min.
Toda la API exige esa sesión (401 sin ella). Si la API corre en otro puerto: `set REPORTES_API_URL=http://127.0.0.1:PUERTO` antes de `npm start`.
Si cambias el `.env`, reinicia la API (lo lee al arrancar).

## Secciones

| Sección | Qué muestra |
|---|---|
| **Inicio** | Cortes vigentes del `.env`, métricas de los últimos 7 días (ejecuciones, % de éxito, estados), **avance del cierre de mes** (mensuales con una ejecución correcta para `FECHA_CORTE_MENSUAL` y cuáles faltan) y ejecuciones recientes con acceso al log |
| **Reportes** | Tabla del catálogo (Nº del legado, tipo, responsable, servidor, última ejecución) con buscador, filtro y orden |
| **Ejecuciones** | Historial completo: filtros por estado y tipo, orden por columna, columnas a elección, paginación; por fila: **Detalle** en un diálogo (datos, log en vivo y archivos con vista previa), ir al reporte, copiar el comando. Se refresca cada 5 s |
| **Perfil** (menú de usuario, `/perfil`) | Dos tarjetas como la página *Profile* de Dokploy. **Cuenta**: cambiar el usuario y/o la contraseña con que entras (siempre con la contraseña actual; mínimo 8 caracteres, sin `#` ni comillas); se guarda en `WEB_USUARIO`/`WEB_CLAVE` del `.env` y rige ya, sin reiniciar. **Sesión**: equipo y usuario con que corre la API, y *Cerrar sesión* |
| **Validación de tablas** (`/validacion`) | Validación **masiva** de las tablas de los reportes mensuales, en dos secciones: *Heredados de Piero* y *Heredados de Erick*. Una fecha de corte (fin de mes) y un botón por sección: cada tabla distinta se consulta una sola vez (solo SELECT), se ve qué reportes quedan al día o con tablas pendientes y se obtiene **un único mensaje para Producción** (Copiar / Guardar en `data/outputs/solicitudes/`). Reemplaza a la pestaña de validación que había en cada reporte |
| **Configuración** (`/configuracion`) | **Editable**: cortes mensual (fin de mes) y diario, carpetas de entradas y salidas, driver ODBC. *Guardar* escribe solo esas claves en el `.env` de la API y valida antes (fecha válida y no futura, rutas completas, sin `#` ni comillas). Los cortes rigen desde la próxima ejecución; carpetas y driver, al reiniciar la API (la pantalla lo avisa). Contraseñas y demás variables no se muestran ni se tocan |
| **Notificaciones** (`/configuracion/notificaciones`) | Lista de proveedores como en Dokploy: **Correo (SMTP)** (servidor, puerto, cuenta, contraseña de aplicación, remitente, correo de prueba) y **Google Chat** (webhook). Cada uno se configura en un diálogo, con **Probar** y **Guardar** en el `.env`. La contraseña y el webhook son de solo escritura (no se muestran; vacío = no se tocan, el botón de papelera los quita). La prueba de correo llega solo a `CORREO_PRUEBA`; la de Google Chat pide confirmación porque publica en el espacio. Rigen desde el próximo envío, sin reiniciar |
| **Bases de datos** (`/servidores`) | Tabla de los 3 servidores (autenticación, estado de credenciales en el `.env`, bases) con buscador, **Test de conexión** por fila y **Probar todas**. No muestra contraseñas |

Navegación (como Dokploy): el sidebar principal (Inicio · Reportes · Ejecuciones) se pliega a íconos con el botón del
encabezado o **Ctrl+B**. **Reportes** es un menú plegable con el árbol del legado: Diarios · Heredados de Piero · Heredados de
Erick, y dentro las carpetas con sub-reportes (04 → 04.1, 04.2; 09 → 09.1, 09.2…). Al pie va el menú de usuario (iniciales,
estado de la API y ejecuciones en curso) con Perfil y Cerrar sesión. Los ajustes son un grupo propio del sidebar, **Configuración** (como «Settings» en Dokploy), con una página por ajuste: General, Notificaciones y Bases de datos. El botón de tema (sol/luna, claro/oscuro) está en el encabezado y en el login. Las migas muestran dónde estás
(`Reportes > Diarios > Cartera sin asignar`) y el encabezado la hora de Lima.

## Procedimiento por reporte

El encabezado del reporte muestra el ícono con el estado de la última ejecución, la descripción, la última ejecución y las
insignias (tipo, servidor, responsable · Nº). La pestaña abierta queda en la URL (`?tab=ejecuciones`).

| Pestaña | Qué hace | Equivale a |
|---|---|---|
| General | La **fecha de corte** (una sola vez, encima de las pestañas); tarjeta **Ejecución** (Ejecutar, Copiar comando y el **log en vivo**) y tarjeta **Parámetros** (correo, confirmaciones y estado de las tablas) | `python main.py <r> --fecha-corte …` |
| Ejecuciones | Las últimas 20, numeradas, con estado, corte, duración, **Ver detalle** (diálogo con log y archivos) | — |
| Archivos | Excel, imagen y textos de la carpeta del reporte, con **vista previa** (200 filas por hoja) y descarga | `data/outputs/<…>/` |
| Correo (solo `cartera-sin-asignar`) | Estado de la prueba; **Enviar a toda la lista** exige marcar «Revisé el correo de prueba» | `--correo todos --conforme` |

Reglas que la API exige (aunque la web ya las avise):

- Mensual = fin de mes; ninguna fecha de corte en el futuro.
- `tapp-saldo-medio-territorio` exige confirmar la escritura en BD.
- `--forzar` solo aparece si la última ejecución terminó con tablas desactualizadas, y queda escrito en el historial.
- Enviar a todos exige una prueba previa del mismo corte y el conforme; no reenvía si ya se envió.
- Un reporte a la vez: los demás esperan **En cola**.

## Estados de una ejecución

| Estado | Código | Qué hacer |
|---|---|---|
| Correcto | 0 | Revisa los archivos generados (vista previa en la misma página) y entrégalos |
| Error | 1 | Lee la salida: datos vacíos, Excel abierto, error SQL |
| Configuración | 2 | Fecha, `.env`, driver o confirmación faltante |
| Tablas desactualizadas | 3 | En Validación de tablas, pide la carga a Producción y vuelve a verificar |

Si la API se reinicia con una ejecución en curso, queda en **Error** con la nota «Interrumpida».

## Estructura

```text
src/api/            app.py (rutas) · esquemas.py (contratos) · servicios.py (casos de uso) · ejecuciones.py (cola)
frontend/src/app/        rutas: / · /reportes · /reportes/[nombre] · /ejecuciones · /ejecuciones/[id] · /perfil; tokens.css (copia de MIS)
frontend/src/lib/        api.ts (transporte) · tipos.ts (espejo de esquemas.py) · formato.ts (funciones puras)
frontend/src/features/   orquestación por pantalla (inicio, reportes, ejecuciones, perfil)
frontend/src/components/ presentación compartida: app-sidebar, encabezado (migas), pagina, terminal, estados, confirmar; ui/ = shadcn
```

API usada por Perfil: `GET /api/perfil` (sin contraseñas ni webhook), `GET /api/configuracion`, `GET /api/servidores` (sin secretos) y `POST /api/servidores/{nombre}/prueba` (`SELECT 1`).
El historial admite `GET /api/ejecuciones?reporte=…&limite=…` (1–2000, por defecto 200), de la más reciente a la más antigua.
