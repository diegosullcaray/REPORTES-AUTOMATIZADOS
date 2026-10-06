"""Extrae del SQL versionado y de los módulos las tablas que consulta cada reporte.

Es la fuente de la regla `tabla-sin-registrar`: lo que el código usa debe estar en `reportes/tablas.py`.

    python governance/scripts/extraer_tablas.py            # imprime reporte -> tablas
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BASES_CONOCIDAS = {"dwh", "intcom", "csd", "storage", "dma", "appj", "slc", "dbriesgos", "dw_raw_v2", "dw_raw",
                   "dbrcc", "dw_metadata", "rcc_cd"}
RX = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE|TRUNCATE\s+TABLE|EXEC(?:UTE)?)\s+(\[?[A-Za-z_{][\w$#.{}\[\]]*)", re.I)

# módulo Python -> id de reporte (los SQL se identifican por su carpeta)
MODULOS = {
    "diarios/cmg_mora.py": "cmg-mora",
    "mensuales/bancarizados.py": "bancarizados",
    "mensuales/bancarizados_producto.py": "bancarizados-producto",
    "mensuales/clientes_extranjeros.py": "clientes-extranjeros",
    "mensuales/indicadores_clientes.py": "indicadores-clientes",
}


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


def extraer_texto(texto: str) -> set[str]:
    texto = re.sub(r"--[^\n]*", "", texto)
    salida = set()
    for m in RX.finditer(texto):
        n = normalizar(m.group(1))
        if n:
            salida.add(n)
    return salida


def por_reporte() -> dict[str, set[str]]:
    res: dict[str, set[str]] = {}
    for rel, rid in MODULOS.items():
        res[rid] = extraer_texto((RAIZ / "src" / "reportes" / rel).read_text(encoding="utf-8"))
    for p in sorted((RAIZ / "sql").rglob("*.sql")):
        rid = p.parent.name
        res.setdefault(rid, set()).update(extraer_texto(p.read_text(encoding="utf-8", errors="ignore")))
    return res


if __name__ == "__main__":
    for rid, ts in sorted(por_reporte().items()):
        print(f"{rid}: {len(ts)}")
        for t in sorted(ts):
            print("   ", t)
