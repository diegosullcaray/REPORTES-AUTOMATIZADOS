"""Ejecutor común de reportes: conexión -> validación de tablas y fechas -> consulta -> validación de datos -> Excel.

Un reporte es un módulo pequeño con un `ReporteLote` (el T-SQL del reporte con tokens de fecha `@@F@@`…, qué conexión
usa y cómo se llaman las hojas). Este ejecutor hace todo lo demás, igual para todos:

1. Conexión (alias dw_raw | rcc | slc) — falla con un mensaje claro si falta configuración.
2. **Tablas al corte**: por cada tabla del reporte compara MAX(fecha) con el corte. Si falta alguna, NO ejecuta,
   dice cuáles son y deja listo el mensaje para Producción (`data/outputs/solicitudes/`). Código de salida 3.
3. Ejecuta el lote en una sola sesión (tablas temporales) y recoge todos los resultados.
4. Valida los datos: vacío ≠ error; todo vacío ⇒ error que nombra las tablas a revisar; fecha dentro del resultado.
5. Exporta a Excel (`data/outputs/<reporte>/`) con una hoja de control (corte, filas, tablas verificadas).

Códigos de salida: 0 ok · 1 error de datos/ejecución · 2 configuración/argumentos · 3 tablas desactualizadas.
"""

from __future__ import annotations

import argparse
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from ..config import DIR_OUTPUTS, ConfiguracionError
from ..db import ejecutar_lote
from ..tablas import tablas_de
from ..verificacion import Estado, Resultado, mensaje_solicitud, nombre_resuelto, verificar_reporte
from .fechas import Cortes, dia_anterior_habil_simple, fecha_iso

log = logging.getLogger("reportes")

SALIDA_OK, SALIDA_ERROR, SALIDA_CONFIG, SALIDA_TABLAS = 0, 1, 2, 3


@dataclass(frozen=True)
class Hoja:
    """Un resultado del lote, en el orden en que el SQL lo devuelve."""

    nombre: str
    permite_vacio: bool = False
    columna_fecha: str | None = None  # si se indica, MAX(columna) del resultado debe ser >= corte


@dataclass(frozen=True)
class ReporteLote:
    comando: str                      # nombre en main.py (= clave en tablas.USO)
    descripcion: str
    frecuencia: str                   # diaria | mensual
    alias: str                        # conexión: dw_raw | rcc | slc
    sql: str                          # T-SQL (puede traer GO) con tokens @@F@@, @@F_ISO@@, @@F_ANT@@…
    hojas: tuple[Hoja, ...] = ()
    archivo: str = ""                 # prefijo del Excel (defecto: comando en CamelCase)
    vacio_valido: bool = False        # True si un resultado totalmente vacío es legítimo (p. ej. Castigos sin castigos en el mes)
    escribe_en_bd: bool = False       # True si el lote crea/borra tablas permanentes: exige --confirmar-escritura
    avisos: tuple[str, ...] = field(default_factory=tuple)  # notas que se muestran antes de ejecutar


class ErrorDatos(RuntimeError):
    """Resultado inválido (todo vacío, fecha fuera de corte…): nunca se presenta como vacío válido."""


def _nombre_archivo(r: ReporteLote) -> str:
    return r.archivo or "".join(p.capitalize() for p in r.comando.split("-"))


def _limpiar_nombre_hoja(nombre: str, usados: set[str]) -> str:
    base = re.sub(r"[\[\]\*\?/\\:]", "_", nombre)[:31] or "Hoja"
    cand, n = base, 2
    while cand in usados:
        cand = f"{base[:28]}_{n}"
        n += 1
    usados.add(cand)
    return cand


def validar_resultados(r: ReporteLote, resultados: list[pd.DataFrame], cortes: Cortes) -> list[str]:
    """Devuelve avisos; lanza ErrorDatos si el resultado no es utilizable."""
    avisos: list[str] = []
    if not resultados:
        raise ErrorDatos("El lote no devolvió ningún resultado. Revisa que las tablas del reporte tengan datos al corte.")
    if all(df.empty for df in resultados) and not r.vacio_valido:
        raise ErrorDatos(
            "Todos los resultados vinieron vacíos: casi seguro falta cargar alguna tabla al corte "
            f"{cortes.corte:%Y-%m-%d}. Ejecuta `python main.py tablas {r.comando} --fecha-corte {cortes.corte:%Y-%m-%d} --verificar`."
        )
    for i, df in enumerate(resultados):
        hoja = r.hojas[i] if i < len(r.hojas) else Hoja(f"Resultado_{i + 1}")
        if df.empty and not hoja.permite_vacio and not r.vacio_valido:
            avisos.append(f"Hoja «{hoja.nombre}» vacía (revisar si es esperado).")
        if hoja.columna_fecha and not df.empty:
            if hoja.columna_fecha not in df.columns:
                raise ErrorDatos(f"La hoja «{hoja.nombre}» no trae la columna de fecha '{hoja.columna_fecha}'.")
            ultima = pd.to_datetime(df[hoja.columna_fecha]).max().date()
            if ultima < cortes.corte:
                raise ErrorDatos(
                    f"La hoja «{hoja.nombre}» llega solo hasta {ultima:%Y-%m-%d}, antes del corte {cortes.corte:%Y-%m-%d}: tabla desactualizada."
                )
    if r.hojas and len(resultados) < len(r.hojas):
        avisos.append(f"Se esperaban {len(r.hojas)} resultados y llegaron {len(resultados)}.")
    return avisos


def exportar_excel(r: ReporteLote, resultados: list[pd.DataFrame], cortes: Cortes, verificacion: list[Resultado],
                   avisos: list[str], carpeta: Path) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{_nombre_archivo(r)}_{cortes.corte:%Y%m%d}.xlsx"
    usados: set[str] = set()
    with pd.ExcelWriter(ruta, engine="openpyxl") as xl:
        for i, df in enumerate(resultados):
            hoja = r.hojas[i] if i < len(r.hojas) else Hoja(f"Resultado_{i + 1}")
            df.to_excel(xl, sheet_name=_limpiar_nombre_hoja(hoja.nombre, usados), index=False)
        control = [("Reporte", r.comando), ("Corte", f"{cortes.corte:%Y-%m-%d}"),
                   ("Generado", f"{datetime.now():%Y-%m-%d %H:%M}"), ("Conexión", r.alias)]
        control += [(f"Filas · {(r.hojas[i].nombre if i < len(r.hojas) else f'Resultado_{i + 1}')}", len(df)) for i, df in enumerate(resultados)]
        control += [(f"Tabla · {nombre_resuelto(v.tabla, cortes.corte)}", f"{v.estado.value}" + (f" ({v.ultima_fecha:%Y-%m-%d})" if v.ultima_fecha else ""))
                    for v in verificacion]
        control += [("Aviso", a) for a in avisos]
        pd.DataFrame(control, columns=["Concepto", "Valor"]).to_excel(xl, sheet_name=_limpiar_nombre_hoja("Control", usados), index=False)
        for ws in xl.book.worksheets:
            for col in ws.columns:
                ancho = max((len(str(c.value)) for c in col[:200] if c.value is not None), default=8)
                ws.column_dimensions[col[0].column_letter].width = min(max(10, ancho + 2), 60)
    return ruta


def _parser(r: ReporteLote) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=f"main.py {r.comando}", description=r.descripcion)
    if r.frecuencia == "mensual":
        p.add_argument("--fecha-corte", type=fecha_iso, required=True, help="Fin de mes AAAA-MM-DD (feriado: día hábil anterior)")
    else:
        p.add_argument("--fecha-corte", type=fecha_iso, help="AAAA-MM-DD (defecto: día anterior; lunes = sábado)")
    p.add_argument("--salida", type=Path, default=None, help="Carpeta de salida (defecto: data/outputs/<reporte>)")
    p.add_argument("--sin-verificar", action="store_true", help="No validar tablas antes de ejecutar (no recomendado)")
    p.add_argument("--forzar", action="store_true", help="Ejecutar aunque haya tablas desactualizadas (queda anotado en la hoja Control)")
    p.add_argument("--confirmar-escritura", action="store_true", help="Requerido si el reporte crea/borra tablas permanentes")
    p.add_argument("--solo-verificar", action="store_true", help="Solo validar tablas y generar la solicitud; no ejecuta el reporte")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def _imprimir_verificacion(r: ReporteLote, cortes: Cortes, v: list[Resultado]) -> None:
    for x in v:
        ult = f" última={x.ultima_fecha:%Y-%m-%d}" if x.ultima_fecha else ""
        print(f"  {x.estado.value:<15} {nombre_resuelto(x.tabla, cortes.corte)}{ult} {x.detalle}")


def _guardar_solicitud(r: ReporteLote, cortes: Cortes, v: list[Resultado]) -> Path:
    destino = DIR_OUTPUTS / "solicitudes"
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / f"solicitud_{r.comando}_{cortes.corte:%Y%m%d}.txt"
    ruta.write_text(mensaje_solicitud(r.comando, cortes.corte, v) + "\n", encoding="utf-8")
    return ruta


def correr(r: ReporteLote, argv: list[str] | None = None) -> int:
    a = _parser(r).parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        corte = a.fecha_corte or dia_anterior_habil_simple()
        cortes = Cortes.mensual(corte) if r.frecuencia == "mensual" else Cortes(corte)
        sql = cortes.aplicar(r.sql)
        if r.escribe_en_bd and not a.confirmar_escritura and not a.solo_verificar:
            raise ConfiguracionError(
                f"«{r.comando}» crea/borra tablas permanentes en la base de datos. Repite con --confirmar-escritura si estás seguro."
            )
        for aviso in r.avisos:
            print(f"AVISO: {aviso}")

        # ---- 2. tablas al corte
        verificacion: list[Resultado] = []
        if not a.sin_verificar:
            print(f"▶ Verificando tablas de «{r.comando}» al corte {cortes.corte:%Y-%m-%d}…")
            verificacion = verificar_reporte(r.comando, cortes.corte)
            _imprimir_verificacion(r, cortes, verificacion)
            controlables = [x for x in verificacion if x.estado is not Estado.SIN_CONTROL]
            if controlables and all(x.estado is Estado.ERROR for x in controlables):
                raise ConfiguracionError(
                    f"No pude verificar ninguna tabla ({controlables[0].detalle}). Revisa la conexión «{r.alias}» con "
                    "`python main.py probar-conexiones` (o usa --sin-verificar bajo tu responsabilidad)."
                )
            malas = [x for x in verificacion if x.estado in {Estado.DESACTUALIZADA, Estado.NO_EXISTE}]
            dudosas = [x for x in verificacion if x.estado is Estado.ERROR]
            for x in dudosas:
                print(f"AVISO: no pude verificar {x.tabla.nombre} ({x.detalle}); confirma su columna de fecha en src/reportes/tablas.py")
            if malas:
                ruta = _guardar_solicitud(r, cortes, verificacion)
                print(f"\n✗ {len(malas)} tabla(s) sin actualizar al corte. Falta que Producción las cargue:")
                for x in malas:
                    print(f"   - {nombre_resuelto(x.tabla, cortes.corte)}  [{x.tabla.alias}]")
                print(f"\nMensaje listo para enviar: {ruta}")
                if not a.forzar:
                    print("No se ejecutó el reporte. Cuando confirmen la carga, repite el comando (o usa --forzar bajo tu responsabilidad).")
                    return SALIDA_TABLAS
                print("--forzar: se continúa a pesar de todo.")
        if a.solo_verificar:
            return SALIDA_OK

        # ---- 3. ejecución
        print(f"▶ Ejecutando «{r.comando}» en {r.alias}…")
        resultados = ejecutar_lote(r.alias, sql)

        # ---- 4. validación de datos
        avisos = validar_resultados(r, resultados, cortes)
        if a.forzar and verificacion:
            avisos.append("Ejecutado con --forzar: había tablas desactualizadas.")
        for av in avisos:
            print(f"AVISO: {av}")

        # ---- 5. exportación
        ruta = exportar_excel(r, resultados, cortes, verificacion, avisos, a.salida or DIR_OUTPUTS / r.comando.replace("-", "_"))
        print(f"\n✓ {r.comando}: {sum(len(d) for d in resultados)} filas en {len(resultados)} hoja(s) → {ruta}")
        return SALIDA_OK
    except ConfiguracionError as exc:
        print(f"✗ Configuración: {exc}")
        return SALIDA_CONFIG
    except ErrorDatos as exc:
        print(f"✗ Datos: {exc}")
        return SALIDA_ERROR
    except (OSError, ValueError) as exc:  # OSError: p. ej. Excel abierto
        print(f"✗ {exc}")
        return SALIDA_ERROR
    except Exception as exc:  # noqa: BLE001 - error de conexión/SQL: mensaje claro, traza solo con -v
        log.debug("detalle", exc_info=True)
        print(f"✗ Error de base de datos al ejecutar «{r.comando}» ({type(exc).__name__}): {str(exc)[:300]}")
        return SALIDA_ERROR
