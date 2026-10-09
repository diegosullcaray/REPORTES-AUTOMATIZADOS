"""Imagen JPG del resumen jerárquico (el `Reporte_Temporal.jpg` que el legado pegaba en el cuerpo del correo).

Replica el aspecto de la imagen del legado: encabezado azul marino, fila de total oscura, niveles con sangría y «- » en los
niveles agrupadores, negrita en los niveles superiores, valores en soles alineados a la derecha, bordes finos.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from .excel import AZUL_ENCABEZADO, AZUL_NIVEL_1, AZUL_NIVEL_2, AZUL_TOTAL, Resumen, filas_jerarquicas

ANCHO_ETIQUETA, ANCHO_VALOR, ALTO_FILA, TAM_FUENTE = 640, 360, 38, 20
SANGRIA, MARGEN = 18, 14
_FUENTES = {
    False: ["segoeui.ttf", "arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"],
    True: ["segoeuib.ttf", "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
}


def _fuente(negrita: bool) -> ImageFont.ImageFont:
    for nombre in _FUENTES[negrita]:
        try:
            return ImageFont.truetype(nombre, TAM_FUENTE)
        except OSError:
            continue
    return ImageFont.load_default()


def moneda(valor: float) -> str:
    return f"S/ {valor:,.2f}"


def _hex(color: str) -> tuple[int, int, int]:
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def render_resumen_jpg(df: pd.DataFrame, resumen: Resumen, ruta: Path) -> Path:
    """Dibuja el resumen jerárquico de `df` en un JPG y devuelve la ruta."""
    filas = filas_jerarquicas(df, resumen.niveles, resumen.valor)
    total = float(pd.to_numeric(df[resumen.valor], errors="coerce").fillna(0.0).sum())
    ultimo = len(resumen.niveles) - 1
    ancho, alto = ANCHO_ETIQUETA + ANCHO_VALOR, ALTO_FILA * (len(filas) + 2) + 2
    img = Image.new("RGB", (ancho, alto), "white")
    d = ImageDraw.Draw(img)
    normal, negrita = _fuente(False), _fuente(True)
    negro, texto = (0, 0, 0), (38, 38, 38)

    def fila(i: int, etiqueta: str, valor: str, fondo: tuple, color: tuple, bold: bool, sangria: int = 0, centrado: bool = False) -> None:
        y = i * ALTO_FILA
        d.rectangle([0, y, ANCHO_ETIQUETA, y + ALTO_FILA], fill=fondo, outline=negro)
        d.rectangle([ANCHO_ETIQUETA, y, ancho - 1, y + ALTO_FILA], fill=fondo, outline=negro)
        f = negrita if bold else normal
        ty = y + (ALTO_FILA - TAM_FUENTE) // 2 - 2
        if centrado:
            d.text((ANCHO_ETIQUETA / 2, ty), etiqueta, font=f, fill=color, anchor="ma")
            d.text((ANCHO_ETIQUETA + ANCHO_VALOR / 2, ty), valor, font=f, fill=color, anchor="ma")
        else:
            d.text((MARGEN + sangria * SANGRIA, ty), etiqueta, font=f, fill=color)
            d.text((ancho - MARGEN * 2, ty), valor, font=f, fill=color, anchor="ra")

    fila(0, resumen.titulo_filas, resumen.titulo_valor, _hex(AZUL_ENCABEZADO), (255, 255, 255), True, centrado=True)
    fila(1, resumen.titulo_filas, moneda(total), _hex(AZUL_TOTAL), (255, 255, 255), True, sangria=2)
    for i, (nivel, etiqueta, suma) in enumerate(filas, start=2):
        es_hoja = nivel == ultimo
        fondo = _hex(AZUL_NIVEL_1) if nivel <= 1 else (255, 255, 255) if es_hoja else _hex(AZUL_NIVEL_2)
        texto_etiqueta = etiqueta if nivel == 0 or es_hoja else f"- {etiqueta}"
        fila(i, texto_etiqueta, moneda(suma), fondo, texto, bold=not es_hoja, sangria=nivel + 2)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    img.save(ruta, "JPEG", quality=92)
    return ruta
