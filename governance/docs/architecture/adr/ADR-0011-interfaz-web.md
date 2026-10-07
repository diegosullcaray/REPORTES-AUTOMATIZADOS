# ADR-0011: Interfaz web sobre el mismo motor de la consola

- Estado: Vigente
- Fecha: 2026-10-07

## Contexto

Los reportes se ejecutaban solo con `python main.py …`. Se pidió gestionarlos desde una interfaz web (validación de
tablas, ejecución, vista previa de las salidas y envío de correo) con el estilo de MIS Host.

## Decisión

1. **API Python (FastAPI) en `src/api/`, sin reglas propias.** Capas: `app.py` (HTTP) → `esquemas.py` (contratos) →
   `servicios.py` (casos de uso que llaman a `reportes.*`) → `ejecuciones.py` (cola). El dominio `src/reportes/` no cambia.
2. **Las ejecuciones son subprocesos de `main.py`**, en una cola de **un solo trabajador**. Así la web y la consola dan
   los mismos códigos de salida (0/1/2/3), mensajes y archivos, y dos reportes que escriben en BD no se pisan.
   Estado y log quedan en `data/outputs/ejecuciones/` (no versionado).
3. **Las reglas se validan en el servidor antes de encolar** (fin de mes, corte no futuro, `--confirmar-escritura`,
   prueba previa + conforme para enviar a todos). La web solo anticipa los mensajes; la API decide.
4. **Web Next.js + shadcn/ui en `web/`**, que consume la API por proxy (`/api`, mismo origen, sin CORS).
5. **Estilo de MIS**: `web/src/app/tokens.css` es copia de `MIS-angular-front/src/app/theme/tokens.css`; las variables de
   shadcn solo reexportan tokens `--mis-*` (ADR-0002 de MIS: color por token, sin hex en componentes).
6. **Solo local**: la API escucha en `127.0.0.1`. No hay login; exponerla en red requiere otro ADR.

## Consecuencias

- Un reporte nuevo aparece en la web sin tocarla (sale de `registro.py`).
- Los reportes con lógica propia (sin `ReporteLote`) se ejecutan, pero no admiten `--forzar`, confirmación de escritura ni correo.
- La vista previa lee las primeras 200 filas de cada hoja; el Excel completo se descarga.
- Si cambia un contrato de `esquemas.py`, se actualiza `web/src/lib/tipos.ts`.
