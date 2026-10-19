# Interfaz web

Gestiona los reportes desde el navegador con el mismo procedimiento que la consola. Decisión: [ADR-0011](../../architecture/adr/ADR-0011-interfaz-web.md).

## Arrancar

Lo más rápido: **`python iniciar.py`** desde la raíz del repo (API + web, Ctrl+C detiene las dos; opciones `--prod`, `--sin-navegador`, `--puerto-api`, `--puerto-web`). Antes de arrancar compara lo instalado con `backend/requirements.txt` (cada `paquete==versión`) y `frontend/package.json` (cada paquete en `node_modules`, y que `package-lock.json` no sea más nuevo que lo instalado) y, si falta algo, instala solo (`pip install` / `npm install`) y dice qué faltaba. A mano, en dos terminales:

```bat
:: 1) API (desde backend\, entorno activado, .env completo)
cd backend
env\Scripts\activate
pip install -r requirements.txt
python manage.py runserver 127.0.0.1:8000 --noreload

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
| **Ejecuciones** | **Agrupadas por reporte y fecha de corte** (un proceso por fila, no una fila por ejecución): estado del proceso (completo, incompleto, con fallas, en curso), pasos en línea y última actividad; filtros por estado y tipo. **Ver proceso** muestra los pasos: Cartera sin asignar → 1. Excel generado, 2. Correo de prueba, 3. Envío a la lista; los demás → Generación. ✓ hecho · **X** falta · el paso que falló se resalta en rojo; cada paso abre el log de su último intento e indica cuántos intentos hubo. Se refresca cada 5 s **Eliminar**: la papelera de cada fila quita el proceso completo (todas sus ejecuciones); en «Ver proceso» cada ejecución repetida o fallida tiene su propia papelera. Borra el estado y el log del historial (`POST /api/ejecuciones/eliminar`), nunca los archivos generados; las que están en cola o corriendo no se pueden eliminar |
| **Perfil** (menú de usuario, `/perfil`) | Dos tarjetas como la página *Profile* de Dokploy. **Cuenta**: cambiar el usuario y/o la contraseña con que entras (siempre con la contraseña actual; mínimo 8 caracteres, sin `#` ni comillas); se guarda en `WEB_USUARIO`/`WEB_CLAVE` del `.env` y rige ya, sin reiniciar. **Sesión**: equipo y usuario con que corre la API, y *Cerrar sesión* |
| **Validación de tablas** (`/validacion`) | Como Reportes: **la raíz es una tabla** con los reportes mensuales de Piero y Erick y su estado en la **última validación** (al día, esperando carga, sin verificar, sin tablas, sin validar); el sidebar tiene un submenú por responsable (`/validacion/piero`, `/validacion/erick`) y cada uno tiene tres pestañas: **Validación**, **Historial** y **Mensaje**. **Validación**: usa la *fecha de cierre* de la cabecera y un botón; cada tabla distinta se consulta una sola vez (solo SELECT, los servidores a la vez; si uno no responde sus demás tablas se marcan sin reintentar, hasta un minuto), con cifras, problemas de conexión agrupados por causa y detalle **por reporte** y **por tabla**. **Historial**: cada verificación queda guardada (fecha, corte, reportes y tablas al día, sin actualizar, sin verificar y si se pidió por Chat) en `data/outputs/validaciones/<grupo>/` (hasta 200). **Mensaje**: el mensaje único para Producción de la última verificación (Copiar / Guardar en `data/outputs/solicitudes/`) y **Pedirlo por Google Chat**: correo(s) del compañero (se guardan en el `.env` como `ENTREGA_CHAT_VALIDACION_<GRUPO>`) y envío con la cuenta de Google autorizada en MCP, con confirmación; queda anotado a quién y cuándo | `POST /api/validacion/<grupo>/chat/enviar` |
| **Diccionario** (`/diccionario`, grupo propio del menú) | Lee el `diccionario.json` del repo DICCIONARIO (carpeta hermana, o `DICCIONARIO_DIR` en el `.env`). **Resumen**, solo gráficos (ECharts, `components/grafico.tsx`, colores de los tokens `--mis-*` y cada gráfico con su tabla de datos): avance de la documentación por base (validados · extraídos · pendientes), calidad (errores y avisos por regla) y, en «Lo que aporta a tus reportes», cuántas de tus tablas están en el diccionario, las fechas por confirmar (solo si hay) y las tablas que más reportes del MIS leen y los tuyos no (se pulsa la barra para abrirla). **Reportes del MIS**: por niveles (`?base=`): una tarjeta por base de datos (la de los procedimientos y la que guarda tablas) y, al entrar, dos secciones en pestañas (`?seccion=`): **Procedimientos** de la base (con los reportes que los ejecutan) y **Tablas** que ocupa (las que guarda y las que sus procedimientos leen de otras bases, con filtro). Cada reporte y cada tabla abre su detalle (procedimiento, parámetros, tablas y columnas, pantallas del front, quién la lee); no hay una lista plana de tablas. **Procesos** (tarjetas por proceso y pestaña Historial; cada proceso tiene su detalle con General, Ejecuciones, Script y Archivos): lanza `generar`, `verificar` y `test` del repo DICCIONARIO y la validación de las bases (lista cerrada, de a uno, con entorno mínimo, historial de 50 y log en vivo); `generar` reescribe archivos de ese repo. |
| **Configuración** (`/configuracion`) | **Editable**: cortes mensual (fin de mes) y diario, carpetas de entradas y salidas, driver ODBC. *Guardar* escribe solo esas claves en el `.env` de la API y valida antes (fecha válida y no futura, rutas completas, sin `#` ni comillas). Los cortes rigen desde la próxima ejecución; carpetas y driver, al reiniciar la API (la pantalla lo avisa). Contraseñas y demás variables no se muestran ni se tocan |
| **Notificaciones** (`/configuracion/notificaciones`) | Lista de proveedores como en Dokploy: **Correo (SMTP)** (servidor, puerto, cuenta, contraseña de aplicación, remitente, correo de prueba) y **Google Chat** (webhook). Cada uno se configura en un diálogo, con **Probar** y **Guardar** en el `.env`. La contraseña y el webhook son de solo escritura (no se muestran; vacío = no se tocan, el botón de papelera los quita). La prueba de correo llega solo a `CORREO_PRUEBA`; la de Google Chat pide confirmación porque publica en el espacio. Rigen desde el próximo envío, sin reiniciar |
| **MCP** (`/configuracion/mcp`) | Por pestañas (`?tab=`), como el detalle de un reporte. **Cuenta**: cliente OAuth (Client ID, Client secret de solo escritura, cuenta, URI de redirección), servidores activos (`GOOGLE_MCP_SERVICIOS`) y **Autorizar** (vuelve con `?code=` y se conecta solo, o se pega el código / la URL completa; **Desconectar** revoca). Una pestaña por servidor MCP oficial de Google (`https://<servicio>mcp.googleapis.com/mcp/v1`: Drive, Gmail, Docs, Sheets, Slides, Chat) con **Probar conexión** (sesión MCP real: lista las herramientas y permite ejecutar una con argumentos JSON). Gmail y Chat suman **envío directo** (correo; mensaje a un contacto o espacio, no el webhook) con el servidor propio `google-envio` (`backend/src/modulos/integraciones/interfaces/mcp/servidor.py`), porque el MCP oficial de Gmail solo crea borradores. **Conectar**: el `mcpServers` para el cliente (sin el Client secret: va como marcador). Credenciales y token solo en el `.env` |

Páginas de error (como en Dokploy): **404** para rutas inexistentes y **500** para fallos inesperados, con «Reintentar» e «Ir al inicio». Dentro del panel el error conserva el sidebar y el encabezado; si falla el layout raíz, `global-error`. (Los errores de la API —sin conexión, 422— se siguen mostrando dentro de cada pantalla.)

Navegación (como Dokploy): el sidebar principal (Inicio · Reportes · Ejecuciones) se pliega a íconos con el botón del
encabezado o **Ctrl+B**. **Reportes** es un menú plegable con el árbol del legado: Diarios · Heredados de Piero · Heredados de
Erick, y dentro las carpetas con sub-reportes (04 → 04.1, 04.2; 09 → 09.1, 09.2…). Al pie va el menú de usuario (iniciales,
estado de la API y ejecuciones en curso) con Perfil y Cerrar sesión. Los ajustes son un grupo propio del sidebar, **Configuración** (como «Settings» en Dokploy), con una página por ajuste: General, Notificaciones, MCP y Bases de datos. El botón de tema (sol/luna, claro/oscuro) está en el encabezado y en el login. Las migas muestran dónde estás
(`Reportes > Diarios > Cartera sin asignar`) y el encabezado la hora de Lima.

## Procedimiento por reporte

El encabezado del reporte muestra el ícono con el estado de la última ejecución, la descripción, la última ejecución y las
insignias (tipo, servidor, responsable · Nº). La pestaña abierta queda en la URL (`?tab=ejecuciones`).

| Pestaña | Qué hace | Equivale a |
|---|---|---|
| General | Tarjeta **Ejecución** (Ejecutar, Copiar comando y el **log en vivo**) y tarjeta **Parámetros** (correo, confirmaciones y estado de las tablas) | `python main.py <r> --fecha-corte …` |
| General (CMG Mora) | Bloque **Google Chat**: casilla «Enviar el archivo generado por Chat» (marcada si hay destinatario) y a quién (`ENTREGA_CHAT_CMG_MORA` en el `.env`, editable aquí). Ejecuta con `--chat`: tras el TXT, mensaje directo con el archivo adjunto usando la cuenta de Google autorizada en MCP. Si el envío falla, el TXT queda en Archivos y la ejecución termina en error | `python main.py cmg-mora --fecha-corte … --chat` |
| Ejecuciones | Agrupadas por fecha de corte; la más reciente abierta con su proceso paso a paso (✓ / X falta / falla resaltada) y **Ver log** por paso | — |
| Archivos | Excel, imagen y textos de la carpeta del reporte, agrupados **por ejecución** (se abre cada una para ver sus archivos; los que no son de ninguna van en «Sin ejecución registrada»), con **vista previa** (200 filas por hoja) y descarga | `data/outputs/<…>/` |
| Correo (solo `cartera-sin-asignar`) | Estado de la prueba; **Enviar a toda la lista** exige marcar «Revisé el correo de prueba» | `--correo todos --conforme` |
| Correo (todos los reportes) | **Enviar archivos por correo** con la cuenta de Google autorizada en MCP (API de Gmail, no el MCP oficial): Para y CC (se guardan en el `.env` como `ENTREGA_CORREO_PARA_<REPORTE>` / `ENTREGA_CORREO_CC_<REPORTE>`), asunto, mensaje, archivos generados a adjuntar (hasta 10 y 25 MB) y **tu firma de Gmail** (se lee de Gmail, `sendAs`, y se muestra en vista previa). **Enviarme una prueba** va solo a `CORREO_PRUEBA` y sin copia; **Enviar a la lista** pide confirmar «Revisé la prueba» | `POST /api/reportes/<r>/correo/enviar` |

Reglas que la API exige (aunque la web ya las avise):

- **Fecha de cierre** en la cabecera de todas las páginas: botón de calendario (tooltip «Fecha de cierre») que despliega **Filtros** con la fecha de cierre de los mensuales y el corte diario. Rige para todos los reportes y la validación de tablas; vacío = el del `.env`; se recuerda en la pestaña del navegador.
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
config/                        Django: settings, urls, middleware, wsgi y composicion.py
src/modulos/<módulo>/interfaces/web/   vistas y rutas de cada módulo (sistema: sesión, perfil, ajustes · reportes · notificaciones · integraciones)
src/modulos/<módulo>/aplicacion/       casos_uso/ (reglas de cada pantalla) · dto.py (contratos) · puertos.py
src/core/                      http.py (JSON y validación) · bd.py · entorno.py
src/modulos/reportes/infraestructura/  cola_ejecuciones.py · excel.py · … ; src/modulos/integraciones/infraestructura/google/
frontend/src/app/        rutas: / · /reportes · /reportes/[nombre] · /ejecuciones · /ejecuciones/[id] · /perfil; tokens.css (copia de MIS)
frontend/src/lib/        api.ts (transporte) · tipos.ts (espejo de <módulo>/aplicacion/dto.py) · formato.ts (funciones puras)
frontend/src/features/   orquestación por pantalla (inicio, reportes, ejecuciones, perfil)
frontend/src/components/ presentación compartida: app-sidebar, encabezado (migas), pagina, terminal, estados, confirmar; ui/ = shadcn
```

API usada por Perfil: `GET /api/perfil` (sin contraseñas ni webhook), y `GET /api/configuracion`. El test de conexión a los servidores vive en el [Diccionario › Procesos](./diccionario.md) (proceso «Validar las bases de datos»); la página «Bases de datos» de Configuración y sus rutas `/api/servidores` se retiraron el 2026-10-18.
El historial admite `GET /api/ejecuciones?reporte=…&limite=…` (1–2000, por defecto 200), de la más reciente a la más antigua.
