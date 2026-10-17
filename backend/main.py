"""Punto de entrada único de la consola (la lógica está en `src/modulos/reportes/interfaces/cli/principal.py`).

    python main.py listar
    python main.py <reporte> [argumentos del reporte]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from modulos.reportes.interfaces.cli.principal import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
