# Registro de decisiones (ADR)

| ADR | Decisión | Estado |
|---|---|---|
| [0001](./adr/ADR-0001-conexiones-centralizadas.md) | Una sola capa de conexión (ajustada por 0006) | Vigente |
| [0002](./adr/ADR-0002-secretos-solo-en-env.md) | Secretos solo en `.env` | Vigente |
| [0003](./adr/ADR-0003-linea-base-de-gobernanza.md) | Línea base en vez de "cero hallazgos" | Vigente |
| [0013](./adr/ADR-0013-repositorio-en-backend-y-frontend.md) | Repositorio dividido en `backend/` (Python) y `frontend/` (Next.js); `governance/` común en la raíz | Vigente |
| [0012](./adr/ADR-0012-acceso-a-la-web-y-ajustes-editables.md) | Login con `WEB_USUARIO`/`WEB_CLAVE` del `.env`, cookie firmada; ajustes (cortes, carpetas, SMTP, webhook, cuenta) editables con escritura acotada del `.env`; validación masiva de tablas | Vigente |
| [0011](./adr/ADR-0011-interfaz-web.md) | Interfaz web (FastAPI + Next.js/shadcn con tokens de MIS) sobre el mismo motor: ejecuciones como subproceso de `main.py` en cola de uno | Vigente |
| [0010](./adr/ADR-0010-orden-del-legado-y-entrega-por-correo.md) | Orden y responsable (Piero/Erick) del legado en código y salidas; correo del resumen diario (prueba → conforme → todos) | Vigente |
| [0009](./adr/ADR-0009-formato-excel-del-legado.md) | Salidas con el formato Excel del legado; sin hoja de control | Vigente |
| [0008](./adr/ADR-0008-mapa-bases-servidores.md) | Mapa base → servidor (`storage` en MISH, `dwh` en 213, `dbriesgos` en 70); cada reporte usa el servidor de sus bases | Vigente |
| [0007](./adr/ADR-0007-ejecucion-manual-fecha-en-env.md) | Ejecución manual bajo demanda; fecha de corte en el `.env` | Vigente |
| [0006](./adr/ADR-0006-conexion-es-servidor-base-por-reporte.md) | La conexión es un servidor (`mish`/`slc`/`rcc`); la base de datos la elige cada reporte | Vigente |
| [0005](./adr/ADR-0005-reportes-como-modulos-py.md) | Reportes como módulos `.py` con ejecutor común; sin carpeta `sql/` | Vigente |
| [0004](./adr/ADR-0004-legado-intacto.md) | `docs/LEGADO` se conserva intacto; el código nuevo es copia normalizada | Vigente |
