# ADR-0003: Línea base de gobernanza en lugar de "cero hallazgos"

- Estado: Vigente · Fecha: 2026-10-06

## Contexto
La primera corrida del validador sobre el código migrado arrojó avisos preexistentes (módulos sin prueba vecina, SQL aún sin consumir). Exigir cero obliga a pagar la deuda de golpe; ser informativo la deja crecer.

## Decisión
La deuda conocida se congela en `governance/gobernanza.linea-base.json`; el criterio es **cero hallazgos nuevos**.

```bash
python governance/scripts/validar_gobernanza.py --guardar-linea-base   # congelar (deliberado)
python governance/scripts/validar_gobernanza.py --linea-base --check   # exigir cero nuevos
python governance/scripts/validar_gobernanza.py --sin-linea-base       # pasivo completo
```

La clave de cada hallazgo es `regla|archivo|detalle`.

## Consecuencias
- Regenerarla para destrabar un pipeline es esconder deuda; solo se regenera al reducirla (el diff debe mostrar entradas que salen).
- Debe encoger: al automatizar un SQL o añadir un test, su entrada desaparece.
- Lo congelado no es precedente.
