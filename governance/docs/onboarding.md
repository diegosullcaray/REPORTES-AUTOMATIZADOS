# Onboarding

1. Lee el [readme de gobernanza](../readme.md) y la [visión](./business/product-vision.md).
2. Configura el entorno: [setup](./development/setup-guide.md) (`backend/.env` desde `backend/.env.example`).
3. En el `.env` escribe la fecha de corte (`FECHA_CORTE_MENSUAL`, `FECHA_CORTE_DIARIA`) y ejecuta (dentro de `backend/`) `python main.py probar-conexiones` — deben responder los 3 servidores (`mish`, `slc`, `rcc`).
4. `python governance/scripts/verificar.py` (desde la raíz) — todo en verde antes de tocar nada.
5. Lee el [contrato de conexiones](./data/contracts/conexiones-bd.md) y el [linaje](./data/lineage.md).
6. Practica el [proceso estándar de ejecución](./development/runbooks/ejecutar-un-reporte.md): `python main.py tablas <reporte> --fecha-corte <corte> --verificar`.
7. Elige un reporte del [catálogo](./business/domain-catalog.md) (o un procedimiento manual del legado) y sigue la [guía de nuevo reporte](./development/report-creation-guide.md).

Regla de oro: **nunca** pongas credenciales en el código; **nunca** abras conexiones fuera de `backend/src/reportes/db.py`.
