# Onboarding

1. Lee el [readme de gobernanza](../readme.md) y la [visión](./business/product-vision.md).
2. Configura el entorno: [setup](./development/setup-guide.md) (`.env` desde `.env.example`).
3. `python main.py probar-conexiones` — deben responder las 3 bases.
4. `python governance/scripts/verificar.py` — todo en verde antes de tocar nada.
5. Lee el [contrato de conexiones](./data/contracts/conexiones-bd.md) y el [linaje](./data/lineage.md).
6. Elige un SQL pendiente en el [catálogo de reportes](./business/domain-catalog.md) y sigue la [guía de nuevo reporte](./development/report-creation-guide.md).

Regla de oro: **nunca** pongas credenciales en el código; **nunca** abras conexiones fuera de `src/reportes/db.py`.
