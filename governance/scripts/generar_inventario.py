"""Deriva del código el inventario de reportes y de SQL (un inventario escrito a mano miente al primer commit).

    python governance/scripts/generar_inventario.py          # reescribe governance/docs/architecture/module-inventory.md
    python governance/scripts/generar_inventario.py --check  # falla si el archivo está desactualizado
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
SALIDA = RAIZ / "governance" / "docs" / "architecture" / "module-inventory.md"


def generar() -> str:
    from reportes.config import BASES
    from reportes.registro import REPORTES

    sqls = sorted((RAIZ / "sql").rglob("*.sql"))
    codigo = "\n".join(p.read_text(encoding="utf-8") for p in (RAIZ / "src").rglob("*.py"))
    tests = sorted(p.name for p in (RAIZ / "tests").glob("test_*.py"))
    L = ["# Inventario de módulos", "",
         "> **Generado** por `governance/scripts/generar_inventario.py`. No editar a mano: `python governance/scripts/generar_inventario.py`.", "",
         "## Bases de datos", "", "| Alias | Servidor (defecto) | Base (defecto) | Variables |", "|---|---|---|---|"]
    for b in BASES.values():
        L.append(f"| `{b.nombre}` | {b.servidor_defecto} | {b.base_defecto} | `{b.prefijo}_SERVER/DATABASE/USER/PASSWORD` |")
    L += ["", f"## Reportes automatizados ({len(REPORTES)})", "", "| Comando | Frecuencia | Bases | Módulo |", "|---|---|---|---|"]
    for r in REPORTES.values():
        L.append(f"| `{r.nombre}` | {r.frecuencia} | {', '.join(r.bases)} | `{r.modulo}` |")
    L += ["", f"## SQL versionado ({len(sqls)})", "", "| Archivo | Estado |", "|---|---|"]
    for p in sqls:
        usado = p.stem in codigo or p.relative_to(RAIZ / "sql").as_posix() in codigo
        L.append(f"| `{p.relative_to(RAIZ).as_posix()}` | {'consumido por código' if usado else 'pendiente de automatizar'} |")
    L += ["", f"## Pruebas ({len(tests)} archivos)", ""] + [f"- `tests/{t}`" for t in tests]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    nuevo = generar()
    if a.check:
        if not SALIDA.exists() or SALIDA.read_text(encoding="utf-8") != nuevo:
            print("module-inventory.md desactualizado: ejecuta generar_inventario.py")
            return 1
        return 0
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(nuevo, encoding="utf-8")
    print(f"Escrito {SALIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
