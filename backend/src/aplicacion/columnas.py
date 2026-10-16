"""Aplica el formato de columnas de un reporte (orden, encabezados y reemplazo de 0/nulos) a un resultado."""

from __future__ import annotations

import pandas as pd

from dominio.formato_excel import Columna, ColumnaFaltante


def aplicar_columnas(df: pd.DataFrame, columnas: tuple[Columna, ...]) -> pd.DataFrame:
    """Deja solo las columnas del formato, en su orden y con sus encabezados; aplica los reemplazos de 0 y nulos."""
    por_nombre = {str(c).casefold(): c for c in df.columns}
    salida: dict[str, pd.Series] = {}
    formatos: dict[str, str] = {}
    for col in columnas:
        candidatas = (col.origen,) if isinstance(col.origen, str) else col.origen
        real = next((por_nombre[c.casefold()] for c in candidatas if c.casefold() in por_nombre), None)
        if real is None:
            raise ColumnaFaltante(f"El resultado no trae la columna {' / '.join(candidatas)}; trae: {', '.join(map(str, df.columns))}")
        serie = df[real]
        if col.si_cero is not None or col.si_nulo is not None:
            serie = serie.astype(object).copy()
            if col.si_cero is not None:
                es_cero = pd.to_numeric(serie, errors="coerce") == 0
                serie[es_cero.fillna(False)] = col.si_cero
            if col.si_nulo is not None:
                serie[serie.isna()] = col.si_nulo
        salida[col.titulo] = serie
        if col.formato:
            formatos[col.titulo] = col.formato
    nuevo = pd.DataFrame(salida)
    nuevo.attrs["formatos"] = formatos
    return nuevo
