---
name: reportes-secretos-y-salidas
description: Manejo de credenciales y de archivos con datos de clientes. Usar al tocar .env, config.py, salidas/ o al compartir resultados.
---

# Secretos y salidas

1. Credenciales **solo** en `.env` (copiado de `.env.example`); jamás en código, SQL, docs, issues o commits.
2. Si encuentras un literal en el legado, no lo copies: regístralo en [findings](../../docs/security/findings.md).
3. `salidas/*`, `*.pkl`, `*.xlsx` están en `.gitignore`; no se versionan datos de clientes.
4. Salidas con `TIPO_DOC`/`NUM_DOC` o saldos por cliente: clasificación [restringido/confidencial](../../docs/data/classification.md).
5. Tras un `git add -A`, revisa `git status` por archivos de `salidas/` antes de commitear.
6. `python governance/scripts/validar_gobernanza.py --regla=secretos-en-codigo` antes del PR.
