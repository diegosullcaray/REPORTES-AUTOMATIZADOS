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
SALIDA_TABLAS = RAIZ / "governance" / "docs" / "data" / "tables-inventory.md"


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


def generar_tablas() -> str:
    from reportes.registro import frecuencia_de
    from reportes.tablas import TABLAS, USO, reportes_que_usan

    L = ["# Inventario de tablas", "",
         "> **Generado** desde `src/reportes/tablas.py` por `governance/scripts/generar_inventario.py`. No editar a mano; "
         "para cambiar algo edita `tablas.py` y regenera.", "",
         "Sirve para el cierre de mes: saber **qué tablas necesita cada reporte** y **a qué reportes afecta una tabla** "
         "antes de pedir a Producción que la actualice. Proceso: [cierre de mes](../development/runbooks/proceso-cierre-de-mes.md).", "",
         f"- Tablas registradas: **{len(TABLAS)}** · Reportes con tablas: **{len(USO)}**",
         "- **Confianza** de la columna de fecha: `confirmada` (aparece en el SQL/código) · `convencion` (inferida por el prefijo H*/S* del core; "
         "**validar con el DBA**) · `por_confirmar`.", "",
         "## 1. Por reporte (¿qué debo tener actualizado?)", ""]
    for rid in sorted(USO):
        L += [f"### `{rid}` ({frecuencia_de(rid)})", "", "| Tabla | Conexión | Tipo | Columna de fecha | Confianza |", "|---|---|---|---|---|"]
        for n in USO[rid]:
            t = TABLAS[n]
            L.append(f"| `{t.nombre}` | `{t.alias}` | {t.tipo} | {('`' + t.col_fecha + '`') if t.col_fecha else '—'} | {t.confianza} |")
        L.append("")
    L += ["## 2. Por tabla (si se actualiza esta, ¿a qué reportes afecta?)", "", "| Tabla | Conexión | Tipo | Reportes |", "|---|---|---|---|"]
    for n in sorted(TABLAS):
        t = TABLAS[n]
        usos = reportes_que_usan(n)
        L.append(f"| `{n}` | `{t.alias}` | {t.tipo} | {', '.join(f'`{u}`' for u in usos) if usos else '— (solo SQL legado)'} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    pares = [(SALIDA, generar()), (SALIDA_TABLAS, generar_tablas())]
    if a.check:
        viejos = [d.name for d, nuevo in pares if not d.exists() or d.read_text(encoding="utf-8") != nuevo]
        if viejos:
            print(f"Desactualizado: {', '.join(viejos)}. Ejecuta generar_inventario.py")
            return 1
        return 0
    for destino, nuevo in pares:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(nuevo, encoding="utf-8")
        print(f"Escrito {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
