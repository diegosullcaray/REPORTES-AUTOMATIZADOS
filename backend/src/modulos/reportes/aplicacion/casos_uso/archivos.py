"""Archivos generados por cada reporte: listado, descarga segura y vista previa (Excel y texto)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.reportes.aplicacion.rutas import carpeta_salida
from modulos.reportes.dominio.archivos import TIPOS, es_generado

from modulos.reportes.aplicacion.casos_uso.catalogo import reporte
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion.puertos import puertos

MAX_TEXTO = 200_000
FILAS_VISTA_PREVIA = 200


# ---------------------------------------------------------------- archivos generados y vista previa

def carpeta_de(nombre: str) -> Path:
    reporte(nombre)
    return carpeta_salida(nombre)


def _ruta_segura(nombre: str, archivo: str) -> Path:
    """Solo archivos directamente dentro de la carpeta de salida del reporte (sin rutas relativas)."""
    carpeta = carpeta_de(nombre).resolve()
    ruta = (carpeta / archivo).resolve()
    if ruta.parent != carpeta or not ruta.is_file():
        raise NoEncontrado(f"No existe el archivo {archivo}")
    return ruta


def archivos(nombre: str) -> list[dto_reportes.Archivo]:
    carpeta = carpeta_de(nombre)
    if not carpeta.is_dir():
        return []
    salida = [
        dto_reportes.Archivo(nombre=f.name, tipo=TIPOS.get(f.suffix.lower(), "otro"), tamano=f.stat().st_size,
                  modificado=datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds"))
        for f in carpeta.iterdir() if f.is_file() and es_generado(f.name)
    ]
    return sorted(salida, key=lambda a: a.modificado, reverse=True)


def ruta_descarga(nombre: str, archivo: str) -> Path:
    return _ruta_segura(nombre, archivo)


def vista_previa(nombre: str, archivo: str) -> dto_reportes.VistaPrevia:
    ruta = _ruta_segura(nombre, archivo)
    tipo = TIPOS.get(ruta.suffix.lower())
    if tipo == "texto":
        return dto_reportes.VistaPrevia(archivo=ruta.name, tipo="texto", texto=ruta.read_text(encoding="utf-8", errors="replace")[:MAX_TEXTO])
    if tipo != "excel":
        raise PeticionInvalida("Solo hay vista previa de Excel y texto; las imágenes se abren directamente.")
    return dto_reportes.VistaPrevia(archivo=ruta.name, tipo="excel", hojas=puertos().lector_archivos.hojas_excel(ruta, FILAS_VISTA_PREVIA))
