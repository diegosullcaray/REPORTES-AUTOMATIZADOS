"""Extrae de cada módulo de reporte (el SQL va incrustado) las tablas que consulta.

Es la fuente de la regla `tabla-sin-registrar`: lo que el código usa debe estar en `reportes/tablas.py`.

    python governance/scripts/extraer_tablas.py            # imprime reporte -> tablas
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BACK = RAIZ / "backend"  # el motor Python vive en backend/; governance/ queda en la raíz
BASES_CONOCIDAS = {"dwh", "intcom", "csd", "storage", "dma", "appj", "slc", "dbriesgos", "dw_raw_v2", "dw_raw",
                   "dbrcc", "dw_metadata", "rcc_cd"}
RX = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE|TRUNCATE\s+TABLE|EXEC(?:UTE)?)\s+(\[?[A-Za-z_{][\w$#.{}\[\]]*)", re.I)

def normalizar(nombre: str) -> str | None:
    n = nombre.replace("[", "").replace("]", "").rstrip(".").lower()
    n = re.sub(r"\{p\.(yyyymmdd|yyyymm)\}", r"{\1}", n)
    n = re.sub(r"\{fec_tabla\}", "{yyyymmdd}", n)
    n = re.sub(r"\bdb\d{6}\b", "db{yyyymm}", n)
    n = re.sub(r"(?<=[a-z])\d{8}\b", "{yyyymmdd}", n)
    partes = n.split(".")
    if partes[0] == "ref":                      # tapp: ref.FJERCOR02 -> storage.ref.*
        n = "storage." + n
        partes = n.split(".")
    if partes[0] == "bt":                       # consulta_anterior: bt.fsd002 -> intcom.bt.*
        n = "intcom." + n
        partes = n.split(".")
    if partes[0] == "db{yyyymm}" or partes[0] in BASES_CONOCIDAS:
        return n if len(partes) >= 3 else None
    return None


RX_DINAMICA = re.compile(r"\bdb\{p\.yyyymm\}\.dbo\.([a-z]+)\{p\.yyyymmdd\}", re.I)


def extraer_texto(texto: str) -> set[str]:
    texto = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)   # comentarios de bloque: una tabla citada solo en un comentario no cuenta
    texto = re.sub(r"--[^\n]*", "", texto)
    salida = set()
    # Tablas cuyo nombre se arma en un f-string (p. ej. pasivos de clientes_extranjeros): directa en rcc y, si el
    # módulo usa el linked server rcc_cd, también por ese linked server desde slc.
    for m in RX_DINAMICA.finditer(texto):
        salida.add(f"db{{yyyymm}}.dbo.{m.group(1).lower()}{{yyyymmdd}}")
        if "LINKED_SERVER_RCC" in texto or "rcc_cd" in texto:
            salida.add(f"rcc_cd.db{{yyyymm}}.dbo.{m.group(1).lower()}{{yyyymmdd}}")
    for m in RX.finditer(texto):
        n = normalizar(m.group(1))
        if n:
            salida.add(n)
    return salida


def por_reporte() -> dict[str, set[str]]:
    """comando -> tablas que aparecen en el módulo del reporte (el SQL va incrustado en cada módulo)."""
    import sys

    sys.path.insert(0, str(BACK / "src"))
    from reportes.registro import REPORTES

    res: dict[str, set[str]] = {}
    for r in REPORTES.values():
        ruta = BACK / "src" / (r.modulo.replace(".", "/") + ".py")
        res[r.comando if hasattr(r, "comando") else r.nombre] = extraer_texto(ruta.read_text(encoding="utf-8"))
    return res


if __name__ == "__main__":
    for rid, ts in sorted(por_reporte().items()):
        print(f"{rid}: {len(ts)}")
        for t in sorted(ts):
            print("   ", t)
