"""Edición acotada del .env: cambia o quita solo las claves indicadas y deja intacto el resto (secretos incluidos)."""

from __future__ import annotations

import os
import re
from pathlib import Path

_CLAVE = re.compile(r"\s*([A-Z][A-Z0-9_]*)\s*=")


def escribir(ruta: Path, cambios: dict[str, str]) -> None:
    """`cambios[clave] = valor`; valor vacío quita la línea. Los valores ya vienen validados (sin saltos de línea, `#` ni comillas)."""
    pendientes = dict(cambios)
    salida: list[str] = []
    for linea in ruta.read_text(encoding="utf-8").splitlines() if ruta.exists() else []:
        m = _CLAVE.match(linea)
        if m and m.group(1) in pendientes:
            valor = pendientes.pop(m.group(1))
            if valor:
                salida.append(f"{m.group(1)}={valor}")
        else:
            salida.append(linea)
    salida += [f"{k}={v}" for k, v in pendientes.items() if v]
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_text("\n".join(salida) + "\n", encoding="utf-8")
    os.replace(temporal, ruta)  # reemplazo atómico: nunca queda un .env a medias
