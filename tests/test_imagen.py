import pandas as pd
from PIL import Image

from reportes.comun.excel import Resumen
from reportes.comun.imagen import ALTO_FILA, moneda, render_resumen_jpg

RESUMEN = Resumen("RESUMEN_v2", ("NIVEL", "Grupo", "Territorio", "Corredor", "Agencia_Cli"), "Saldo_Capital", "TERRITORIO POR CLIENTE", "SALDO CARTERA - MIS")


def test_moneda_como_en_el_legado():
    assert moneda(310688.37) == "S/ 310,688.37" and moneda(0.73) == "S/ 0.73"


def test_la_imagen_se_genera_con_una_fila_por_nivel_mas_encabezado_y_total(tmp_path):
    df = pd.DataFrame({"NIVEL": ["FC", "FC"], "Grupo": ["GRUPAL", "GRUPAL"], "Territorio": ["LIMA", "LIMA"],
                       "Corredor": ["LIMA ESTE", "LIMA ESTE"], "Agencia_Cli": ["AG A", "AG B"], "Saldo_Capital": [10.0, 5.0]})
    ruta = render_resumen_jpg(df, RESUMEN, tmp_path / "sub" / "Reporte_Temporal.jpg")
    img = Image.open(ruta)
    assert img.format == "JPEG" and img.size[0] > 800
    # encabezado + fila de total + 6 filas jerárquicas (FC, GRUPAL, LIMA, LIMA ESTE, AG A, AG B)
    assert img.size[1] == ALTO_FILA * (6 + 2) + 2
    # el encabezado es azul marino (colores del legado)
    r, g, b = img.getpixel((5, 5))
    assert b > r and b > g and r < 60
