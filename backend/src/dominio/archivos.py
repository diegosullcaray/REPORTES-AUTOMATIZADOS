"""Qué archivos de la carpeta de un reporte son entregables y de qué tipo son (para la vista previa y las descargas)."""

from __future__ import annotations

TIPOS = {".xlsx": "excel", ".xlsm": "excel", ".jpg": "imagen", ".jpeg": "imagen", ".png": "imagen", ".txt": "texto", ".csv": "texto"}


def es_generado(nombre: str) -> bool:
    """Archivo entregable del reporte. Fuera: los .json internos (p. ej. estado_envio_*.json del correo) y los temporales de Excel."""
    return not nombre.startswith("~$") and not nombre.lower().endswith(".json")
