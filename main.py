"""Punto de entrada único.

    python main.py listar
    python main.py probar-conexiones
    python main.py <reporte> [argumentos del reporte]
        ej.: python main.py bancarizados --fecha-corte 2026-06-30
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from reportes.registro import REPORTES  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help", "listar"}:
        print("Reportes disponibles (python main.py <reporte> --help):\n")
        for r in REPORTES.values():
            print(f"  {r.nombre:<24} [{r.frecuencia:<7}] bases={','.join(r.bases):<8} {r.descripcion}")
        print("\n  probar-conexiones        verifica las 3 conexiones (dw_raw, rcc, slc)")
        return 0
    if argv[0] == "probar-conexiones":
        from reportes.db import probar_conexiones

        estado = probar_conexiones()
        for nombre, resultado in estado.items():
            print(f"  {nombre:<8} {resultado}")
        return 0 if all(v == "OK" for v in estado.values()) else 1
    reporte = REPORTES.get(argv[0])
    if reporte is None:
        print(f"Reporte desconocido '{argv[0]}'. Usa: python main.py listar", file=sys.stderr)
        return 2
    return import_module(reporte.modulo).main(argv[1:]) or 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
