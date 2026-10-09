# ADR-0011: Interfaz web sobre el mismo motor de la consola

- Estado: Vigente
- Fecha: 2026-10-07

## Contexto

Los reportes se ejecutaban solo con `python main.py …`. Se pidió gestionarlos desde una interfaz web (validación de
tablas, ejecución, vista previa de las salidas y envío de correo) con el estilo de MIS Host.

## Decisión

1. **API Python (FastAPI) en `backend/src/api/`, sin reglas propias.** Capas: `app.py` (HTTP) → `esquemas.py` (contratos) →
   `servicios.py` (casos de uso que llaman a `reportes.*`) → `ejecuciones.py` (cola). El dominio `backend/src/reportes/` no cambia.
2. **Las ejecuciones son subprocesos de `main.py`**, en una cola de **un solo trabajador**. Así la web y la consola dan
   los mismos códigos de salida (0/1/2/3), mensajes y archivos, y dos reportes que escriben en BD no se pisan.
   Estado y log quedan en `backend/data/outputs/ejecuciones/` (no versionado).
3. **Las reglas se validan en el servidor antes de encolar** (fin de mes, corte no futuro, `--confirmar-escritura`,
   prueba previa + conforme para enviar a todos). La web solo anticipa los mensajes; la API decide.
4. **Web Next.js + shadcn/ui en `frontend/`**, que consume la API por proxy (`/api`, mismo origen, sin CORS).
5. **Estética Dokploy con la paleta de MIS** (tarea `governance/tasks/tareasdiarias.md`, 2026-10-07): interfaz plana con el
   `Sidebar` de shadcn (retráctil a íconos, con «Reportes» como menú plegable del árbol del legado, **Validación de tablas**,
   un grupo **Configuración** con una página por ajuste —General, Notificaciones, Bases de datos— como «Settings» en Dokploy y,
   al pie, el menú de usuario con Perfil y Cerrar sesión; el sidebar secundario se retiró el 2026-10-07), encabezado con
   `SidebarTrigger`, migas y botón de tema, vista de reporte limpia (título, tipo, parámetros, botón y log tipo terminal) y
   Bases de datos con test de conexión por servidor. Sin wallpaper ni vidrio. Los colores siguen saliendo de
   `frontend/src/app/tokens.css` (copia de `MIS-angular-front/src/app/theme/tokens.css`): las variables de shadcn solo reexportan
   tokens `--mis-*`; los únicos valores propios son los de la terminal, definidos una vez en `globals.css`.
6. **Patrones de Dokploy** (análisis de su código, 2026-10-07): sidebar flotante con grupos y pie de estado, tarjeta
   enmarcada (`Marco`) para cada sección, tablas con TanStack Table v8 (buscador, filtros, orden, columnas visibles,
   paginación, acciones por fila), inicio con métricas y ejecuciones recientes, detalle y log de una ejecución en un
   diálogo, pestañas en la URL y refresco automático. Se agregan `GET /api/configuracion` y el parámetro `limite` de `GET /api/ejecuciones`.
7. **Solo local**: la API escucha en `127.0.0.1`. El acceso exige sesión ([ADR-0012](./ADR-0012-acceso-a-la-web-y-ajustes-editables.md)); exponerla en red requiere otro ADR.

## Consecuencias

- Un reporte nuevo aparece en la web sin tocarla (sale de `registro.py`).
- Los reportes con lógica propia (sin `ReporteLote`) se ejecutan, pero no admiten `--forzar`, confirmación de escritura ni correo; sus advertencias (p. ej. `cmg-mora` trunca y recarga `CMGMora_Recaudo`) salen de `AVISOS_PROPIOS` en `servicios.py`.
- La vista previa lee las primeras 200 filas de cada hoja; el Excel completo se descarga.
- Si cambia un contrato de `esquemas.py`, se actualiza `frontend/src/lib/tipos.ts`.
