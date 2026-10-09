"""`python governance/scripts/verificar.py` — equivalente a `npm run verify`: todas las compuertas sin tocar las bases de datos."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
S = RAIZ / "governance" / "scripts"
FASES = [
    ("gobernanza (cero hallazgos nuevos)", [sys.executable, str(S / "validar_gobernanza.py"), "--linea-base", "--check"]),
    ("inventario al día", [sys.executable, str(S / "generar_inventario.py"), "--check"]),
    ("pruebas unitarias", [sys.executable, "-m", "pytest", "-q", str(RAIZ / "tests")]),
]

if __name__ == "__main__":
    fallo = 0
    for nombre, cmd in FASES:
        print(f"▶ {nombre}")
        rc = subprocess.run(cmd, cwd=RAIZ).returncode
        print(f"{'✓' if rc == 0 else '✗'} {nombre}\n")
        fallo |= rc != 0
    raise SystemExit(1 if fallo else 0)
