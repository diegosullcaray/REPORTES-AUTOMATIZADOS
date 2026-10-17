"""Dónde deja cada reporte sus archivos."""

from __future__ import annotations

from pathlib import Path

from modulos.reportes.dominio.reportes import REPORTES
from core.puertos import nucleo



def carpeta_salida(comando: str) -> Path:
    """Carpeta de salida por defecto de un reporte: data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>."""
    return nucleo().entorno.dir_outputs() / REPORTES[comando].carpeta
