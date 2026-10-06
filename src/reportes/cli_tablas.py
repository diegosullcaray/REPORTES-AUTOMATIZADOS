"""Subcomandos de `main.py`: tablas, solicitud-actualizacion."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from .config import DIR_OUTPUTS, ConfiguracionError
from .registro import frecuencia_de
from .tablas import USO, tablas_de
from .verificacion import Estado, fecha_esperada, mensaje_solicitud, nombre_resuelto, verificar_reporte


def _fecha(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Fecha inválida '{valor}', usa AAAA-MM-DD") from exc


def _parser(prog: str, desc: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=prog, description=desc)
    p.add_argument("reporte", nargs="?", help="nombre del reporte (sin argumento: lista los disponibles)")
    p.add_argument("--fecha-corte", type=_fecha, help="AAAA-MM-DD (obligatoria en mensuales; diarias: día anterior)")
    p.add_argument("--verificar", action="store_true", help="consulta las bases (solo SELECT) para saber si están al día")
    return p


def _listar() -> int:
    print("Reportes con tablas registradas:")
    for r in sorted(USO):
        print(f"  {r:<30} [{frecuencia_de(r):<7}] {len(USO[r])} tablas")
    return 0


def cmd_tablas(argv: list[str]) -> int:
    a = _parser("main.py tablas", "Tablas que usa un reporte y, con --verificar, si están al día al corte.").parse_args(argv)
    if not a.reporte:
        return _listar()
    try:
        frecuencia = frecuencia_de(a.reporte)
        fecha = fecha_esperada(frecuencia, fecha_corte=a.fecha_corte) if (a.verificar or a.fecha_corte) else date.today()
        if not a.verificar:
            for t in tablas_de(a.reporte):
                col = t.col_fecha or "-"
                print(f"  {nombre_resuelto(t, fecha):<58} {t.alias:<7} {t.tipo:<13} fecha:{col:<14} ({t.confianza})")
            return 0
        resultados = verificar_reporte(a.reporte, fecha)
    except (KeyError, ConfiguracionError) as exc:
        print(exc.args[0] if exc.args else exc)
        return 2
    print(f"Reporte {a.reporte} — corte esperado {fecha:%Y-%m-%d}\n")
    for r in resultados:
        ult = f" última={r.ultima_fecha:%Y-%m-%d}" if r.ultima_fecha else ""
        print(f"  {r.estado.value:<15} {nombre_resuelto(r.tabla, fecha):<58} {r.tabla.alias}{ult} {r.detalle}")
    malas = [r for r in resultados if r.estado in {Estado.DESACTUALIZADA, Estado.NO_EXISTE, Estado.ERROR}]
    print(f"\n{len(malas)} tablas con problema de {len(resultados)}.")
    if any(r.estado in {Estado.DESACTUALIZADA, Estado.NO_EXISTE} for r in resultados):
        print("Siguiente paso: python main.py solicitud-actualizacion", a.reporte, "--fecha-corte", f"{fecha:%Y-%m-%d}", "--verificar")
    return 1 if malas else 0


def cmd_solicitud(argv: list[str]) -> int:
    a = _parser("main.py solicitud-actualizacion",
                "Genera el mensaje para pedir a Producción que actualice las tablas del reporte.").parse_args(argv)
    if not a.reporte:
        return _listar()
    try:
        fecha = fecha_esperada(frecuencia_de(a.reporte), fecha_corte=a.fecha_corte)
        resultados = verificar_reporte(a.reporte, fecha) if a.verificar else None
    except (KeyError, ConfiguracionError) as exc:
        print(exc.args[0] if exc.args else exc)
        return 2
    texto = mensaje_solicitud(a.reporte, fecha, resultados)
    destino = Path(DIR_OUTPUTS) / "solicitudes"
    destino.mkdir(parents=True, exist_ok=True)
    archivo = destino / f"solicitud_{a.reporte}_{fecha:%Y%m%d}.txt"
    archivo.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    print(f"\n(Guardado en {archivo})")
    return 0
