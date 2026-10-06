# Marco de Gobernanza — Reportes Automatizados

Centro de gobernanza, automatización y estándares técnicos de los **reportes automatizados de Financiera Confianza** (Finanzas / Riesgos / MIS): entorno **Python** que consulta **3 bases de datos SQL Server** (`dw_raw`, `rcc`, `slc`) y genera archivos de salida (Excel/TXT).

```text
governance/
  ├── scripts/                      automatización: verificación, inventario
  ├── skills/                       guías operativas para desarrolladores y agentes
  ├── agents/                       pipeline de 5 agentes + 2 transversales
  ├── docs/                         documentación canónica
  ├── tasks/                        especificaciones de trabajo en curso
  ├── gobernanza.linea-base.json    deuda congelada (ver ADR-0003)
  └── readme.md
```

**Regla que gobierna todo lo demás: cuando la documentación y el código discrepan, gana el código.** El documento se corrige o se borra.

---

## 1. Verificación

Un solo comando antes de cada commit (no se conecta a ninguna base de datos):

```bash
python governance/scripts/verificar.py   # gobernanza + inventario + pruebas
```

Qué verifica cada compuerta y cómo se maneja la deuda heredada: [compuertas de calidad](./docs/development/quality-gates.md).

## 2. Scripts (`governance/scripts/`)

| Script | Para qué |
|---|---|
| [`verificar.py`](./scripts/verificar.py) | cadena única de compuertas |
| [`validar_gobernanza.py`](./scripts/validar_gobernanza.py) | motor de 10 reglas (secretos, conexiones, rutas, registro, nombres, pruebas…) con línea base |
| [`generar_inventario.py`](./scripts/generar_inventario.py) | deriva del código el inventario de reportes/SQL **y el de tablas** |
| [`extraer_tablas.py`](./scripts/extraer_tablas.py) | extrae las tablas que consulta cada SQL/módulo (base de la regla `tabla-sin-registrar`) |

Manual: [`scripts/README.md`](./scripts/README.md).

## 3. Skills (`governance/skills/`)

| Skill | Qué resuelve |
|---|---|
| [`reportes-arquitectura-modulos`](./skills/reportes-arquitectura-modulos/SKILL.md) | dónde va cada archivo y cómo se registra un reporte |
| [`reportes-conexiones-bd`](./skills/reportes-conexiones-bd/SKILL.md) | las 3 bases: alias, `.env`, `db.py`; nunca conexiones propias |
| [`reportes-sql`](./skills/reportes-sql/SKILL.md) | cómo se escribe, parametriza y versiona el SQL |
| [`reportes-secretos-y-salidas`](./skills/reportes-secretos-y-salidas/SKILL.md) | credenciales, datos de clientes y carpeta `data/outputs/` |
| [`reportes-ejecucion-y-cierre`](./skills/reportes-ejecucion-y-cierre/SKILL.md) | cómo ejecutar un reporte: verificar tablas, pedir actualización, ejecutar, validar |
| [`reportes-testing`](./skills/reportes-testing/SKILL.md) | pytest sin tocar las bases reales |
| [`reportes-migrar-legado`](./skills/reportes-migrar-legado/SKILL.md) | cómo pasar un reporte manual de `docs/LEGADO` a automatizado |

## 4. Agentes (`governance/agents/`)

Pipeline de cinco fases, cada una con criterio de rechazo explícito:

1. [Investigador de requerimientos](./agents/01-investigador-requerimientos.md) — especificación técnica
2. [Desarrollador Python](./agents/02-desarrollador-python.md) — implementa
3. [QA y pruebas](./agents/03-tester-qa.md) — dictamina con evidencia
4. [Auditor de datos y contratos](./agents/04-auditor-datos-contratos.md) — verifica que la cifra signifique lo documentado
5. [Seguridad y rendimiento](./agents/05-revisor-seguridad-rendimiento.md) — última compuerta

Transversales:

- [Curador de gobernanza](./agents/06-curador-de-gobernanza.md) — persigue la deriva entre código y documentación
- [Migrador del legado](./agents/07-migrador-legado.md) — usa `docs/LEGADO` como especificación, no la memoria

Detalle: [`agents/README.md`](./agents/README.md).

## 5. Documentación (`governance/docs/`)

| Área | Qué contiene |
|---|---|
| [`data/`](./docs/data/README.md) | **eje**: glosario, catálogo, **inventario de tablas**, contratos (las 3 BD), linaje, calidad, clasificación, responsabilidades |
| [`architecture/`](./docs/architecture/README.md) | capas, flujo de datos, inventario generado, ADR |
| [`business/`](./docs/business/README.md) | catálogo de reportes, solicitantes, procedimientos manuales heredados, roadmap |
| [`development/`](./docs/development/README.md) | setup, convenciones, cómo crear un reporte, **runbooks (ejecución y cierre de mes)**, pruebas y compuertas |
| [`security/`](./docs/security/README.md) | amenazas, hallazgos (credenciales expuestas) y remediación |
| [`templates/`](./docs/templates/README.md) | ficha de reporte, feature, PR, bug, ADR, evidencia |
| [`evidence/`](./docs/evidence/README.md) | auditorías e incidentes |

Entradas frecuentes: [runbooks](./docs/development/runbooks/README.md) · [inventario de tablas](./docs/data/tables-inventory.md) · [índice general](./docs/README.md) · [onboarding](./docs/onboarding.md) · [contrato de conexiones](./docs/data/contracts/conexiones-bd.md) · [linaje](./docs/data/lineage.md) · [compuertas](./docs/development/quality-gates.md)
