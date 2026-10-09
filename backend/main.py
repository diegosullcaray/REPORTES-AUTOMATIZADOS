"""Punto de entrada único.

    python main.py listar
    python main.py probar-conexiones
    python main.py tablas <reporte> --fecha-corte 2026-10-31 --verificar
    python main.py solicitud-actualizacion <reporte> --fecha-corte 2026-10-31 --verificar
    python main.py <reporte> [argumentos del reporte]
        ej.: python main.py bancarizados --fecha-corte 2026-06-30
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from reportes.registro import GRUPOS, REPORTES, TITULOS_GRUPO, ordenados  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help", "listar"}:
        print("Reportes disponibles (python main.py <reporte> --help):\n")
        for grupo in GRUPOS:
            print(f"{TITULOS_GRUPO[grupo]}")
            for r in (x for x in ordenados() if x.grupo == grupo):
                print(f"  {r.orden:<5} {r.nombre:<28} servidor={','.join(r.servidores):<8} {r.descripcion}")
            print()
        print("\n  probar-conexiones        verifica los 3 servidores (mish, slc, rcc)")
        print("  tablas <reporte>         tablas que usa; con --fecha-corte X --verificar: ¿están al día?")
        print("  columnas-fecha [reporte] [--csv [ARCHIVO]]   columna que controla la fecha de corte por tabla (para Producción)")
        print("  solicitud-actualizacion <reporte> --fecha-corte X [--verificar]   mensaje para Producción")
        return 0
    if argv[0] == "probar-conexiones":
        from reportes.db import probar_conexiones

        estado = probar_conexiones()
        for nombre, resultado in estado.items():
            print(f"  {nombre:<8} {resultado}")
        return 0 if all(v == "OK" for v in estado.values()) else 1
    if argv[0] == "tablas":
        from reportes.cli_tablas import cmd_tablas

        return cmd_tablas(argv[1:])
    if argv[0] == "columnas-fecha":
        from reportes.cli_tablas import cmd_columnas_fecha

        return cmd_columnas_fecha(argv[1:])
    if argv[0] == "solicitud-actualizacion":
        from reportes.cli_tablas import cmd_solicitud

        return cmd_solicitud(argv[1:])
    reporte = REPORTES.get(argv[0])
    if reporte is None:
        print(f"Reporte desconocido '{argv[0]}'. Usa: python main.py listar", file=sys.stderr)
        return 2
    return import_module(reporte.modulo).main(argv[1:]) or 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
