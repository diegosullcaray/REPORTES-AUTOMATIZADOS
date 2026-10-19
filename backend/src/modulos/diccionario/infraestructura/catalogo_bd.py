"""Lee el catálogo de reportes del MIS directo de `mod_rep.rep.RREGREP01`. Solo SELECT, con NOLOCK: esa tabla la usa Ant y un bloqueo la dejaría esperando."""

from __future__ import annotations

import json
import re
import time

from core import bd
from core.servidores import servidor_de_base

FUENTE = "mod_rep.rep.RREGREP01"
CONSULTA = "SELECT RCODREP, RDESREP, RTPREP FROM rep.RREGREP01 WITH (NOLOCK)"
TIMEOUT = 10        # segundos de inicio de sesión: sin VPN la web no debe quedarse esperando
VIGENCIA = 60       # segundos; shortcut: caché por proceso, el catálogo cambia pocas veces al día; subir a evento si se edita en vivo
_cache: tuple[float, list[dict] | Exception] | None = None   # también guarda la falla: sin conexión, cada pantalla no espera otros 10 s


def reporte_de_fila(codigo: object, descripcion: object, rtprep: object) -> dict:
    """Una fila de RREGREP01 en la forma del `diccionario.json`: `RTPREP` es un JSON `{"name": "<base>.<esquema>.<SP>", "params": [{"order": 1, "name": "fec"}…]}`.

    Un RTPREP ilegible no tumba el catálogo: el reporte queda sin procedimiento y se ve así.
    """
    try:
        sp = json.loads(str(rtprep))
        procedimiento = re.sub(r'[\[\]"]', "", str(sp.get("name") or "")).strip()   # [mod_rep].[com].[SP] -> mod_rep.com.SP: la base no se llama «[mod_rep]»
        parametros = [str(p["name"]) for p in sorted(sp.get("params") or [], key=lambda p: p.get("order", 0))]
    except (ValueError, TypeError, KeyError, AttributeError):
        procedimiento, parametros = "", []
    return {"codigo": str(codigo).strip(), "descripcion": str(descripcion or "").strip(), "procedimiento": procedimiento, "parametros": parametros}


def leer(forzar: bool = False) -> list[dict]:
    """Los reportes del catálogo en la forma del diccionario. Si no hay conexión, lanza (quien llama usa el diccionario guardado). `forzar` salta la caché (también la de una falla)."""
    global _cache
    if forzar or _cache is None or time.monotonic() - _cache[0] > VIGENCIA:
        try:
            df = bd.leer_sql(servidor_de_base("mod_rep"), CONSULTA, base="mod_rep", timeout=TIMEOUT)
            filas = [reporte_de_fila(*f) for f in df[["RCODREP", "RDESREP", "RTPREP"]].itertuples(index=False)]
            if filas and sum(not f["procedimiento"] for f in filas) * 2 > len(filas):
                raise ValueError("más de la mitad de los reportes de RREGREP01 no trae procedimiento en RTPREP: ¿cambió el formato?")
            _cache = (time.monotonic(), filas)
        except Exception as exc:  # noqa: BLE001 - cualquier falla de conexión o de esquema se informa, no se propaga como 500
            _cache = (time.monotonic(), exc)
    if isinstance(_cache[1], Exception):
        raise _cache[1]
    return _cache[1]
