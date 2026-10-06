# Registro de decisiones (ADR)

| ADR | Decisión | Estado |
|---|---|---|
| [0001](./adr/ADR-0001-conexiones-centralizadas.md) | Una sola capa de conexión (ajustada por 0006) | Vigente |
| [0002](./adr/ADR-0002-secretos-solo-en-env.md) | Secretos solo en `.env` | Vigente |
| [0003](./adr/ADR-0003-linea-base-de-gobernanza.md) | Línea base en vez de "cero hallazgos" | Vigente |
| [0008](./adr/ADR-0008-mapa-bases-servidores.md) | Mapa base → servidor (`storage` en MISH, `dwh` en 213, `dbriesgos` en 70); cada reporte usa el servidor de sus bases | Vigente |
| [0007](./adr/ADR-0007-ejecucion-manual-fecha-en-env.md) | Ejecución manual bajo demanda; fecha de corte en el `.env` | Vigente |
| [0006](./adr/ADR-0006-conexion-es-servidor-base-por-reporte.md) | La conexión es un servidor (`mish`/`slc`/`rcc`); la base de datos la elige cada reporte | Vigente |
| [0005](./adr/ADR-0005-reportes-como-modulos-py.md) | Reportes como módulos `.py` con ejecutor común; sin carpeta `sql/` | Vigente |
| [0004](./adr/ADR-0004-legado-intacto.md) | `docs/LEGADO` se conserva intacto; el código nuevo es copia normalizada | Vigente |
