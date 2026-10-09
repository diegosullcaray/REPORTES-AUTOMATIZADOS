"""Deriva del código el inventario de reportes y de SQL (un inventario escrito a mano miente al primer commit).

    python governance/scripts/generar_inventario.py          # reescribe governance/docs/architecture/module-inventory.md
    python governance/scripts/generar_inventario.py --check  # falla si el archivo está desactualizado
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BACK = RAIZ / "backend"  # el motor Python vive en backend/; governance/ queda en la raíz
sys.path.insert(0, str(BACK / "src"))
SALIDA = RAIZ / "governance" / "docs" / "architecture" / "module-inventory.md"
SALIDA_TABLAS = RAIZ / "governance" / "docs" / "data" / "tables-inventory.md"
SALIDA_COLUMNAS = RAIZ / "governance" / "docs" / "data" / "columnas-fecha-de-corte.md"
SALIDA_COMANDOS = RAIZ / "governance" / "docs" / "development" / "runbooks" / "comandos.md"


def generar() -> str:
    from importlib import import_module

    from reportes.config import SERVIDORES
    from reportes.registro import REPORTES, ordenados

    tests = sorted(p.name for p in (BACK / "tests").glob("test_*.py"))
    L = ["# Inventario de módulos", "",
         "> **Generado** por `governance/scripts/generar_inventario.py`. No editar a mano: `python governance/scripts/generar_inventario.py`.", "",
         "## Conexiones (3 servidores)", "",
         "El `.env` define **servidores**; la **base de datos la elige cada reporte** (`base=` en su `ReporteLote`, o su propio `USE` / nombres de 3 partes).", "",
         "| Conexión | Servidor (defecto) | Autenticación | Variables `.env` |", "|---|---|---|---|"]
    for b in SERVIDORES.values():
        auth = "Windows (o SQL si hay USER/PASSWORD)" if b.windows_auth_defecto else "SQL (USER/PASSWORD)"
        L.append(f"| `{b.nombre}` | {b.servidor_defecto} | {auth} | `{b.prefijo}_SERVER`, `{b.prefijo}_USER`, `{b.prefijo}_PASSWORD` |")
    L += ["", f"## Reportes ejecutables ({len(REPORTES)})", "", "| Responsable / Nº | Comando | Frecuencia | Servidor | Base de datos | Módulo | Qué hace |", "|---|---|---|---|---|---|---|"]
    for r in ordenados():
        lote = getattr(import_module(r.modulo), "REPORTE", None)
        base = (lote.base or "—") if lote is not None else "propia (ver módulo)"
        L.append(f"| {r.etiqueta} | `{r.nombre}` | {r.frecuencia} | {', '.join(r.servidores)} | {base} | `{r.modulo}` | {r.descripcion} |")
    L += ["", f"## Pruebas ({len(tests)} archivos)", ""] + [f"- `tests/{t}`" for t in tests]
    return "\n".join(L) + "\n"


def generar_tablas() -> str:
    from reportes.registro import REPORTES, frecuencia_de, ordenados
    from reportes.tablas import TABLAS, USO, reportes_que_usan

    L = ["# Inventario de tablas", "",
         "> **Generado** desde `src/reportes/tablas.py` por `governance/scripts/generar_inventario.py`. No editar a mano; "
         "para cambiar algo edita `tablas.py` y regenera.", "",
         "Sirve para el cierre de mes: saber **qué tablas necesita cada reporte** y **a qué reportes afecta una tabla** "
         "antes de pedir a Producción que la actualice. Proceso: [cierre de mes](../development/runbooks/proceso-cierre-de-mes.md).", "",
         f"- Tablas registradas: **{len(TABLAS)}** · Reportes con tablas: **{len(USO)}**",
         "- **Confianza** de la columna de fecha: `confirmada` (aparece en el SQL/código) · `convencion` (inferida por el prefijo H*/S* del core; "
         "**validar con el DBA**) · `por_confirmar`.", "",
         "## 1. Por reporte (¿qué debo tener actualizado?)", ""]
    for rid in [x.nombre for x in ordenados()]:
        L += [f"### {REPORTES[rid].etiqueta} · `{rid}` ({frecuencia_de(rid)})", "", "| Tabla | Conexión | Tipo | Columna de fecha | Confianza |", "|---|---|---|---|---|"]
        for n in USO[rid]:
            t = TABLAS[n]
            L.append(f"| `{t.nombre}` | `{t.servidor}` | {t.tipo} | {('`' + t.col_fecha + '`') if t.col_fecha else '—'} | {t.confianza} |")
        L.append("")
    L += ["## 2. Por tabla (si se actualiza esta, ¿a qué reportes afecta?)", "", "| Tabla | Conexión | Tipo | Reportes |", "|---|---|---|---|"]
    for n in sorted(TABLAS):
        t = TABLAS[n]
        usos = reportes_que_usan(n)
        L.append(f"| `{n}` | `{t.servidor}` | {t.tipo} | {', '.join(f'`{u}`' for u in usos) if usos else '— (solo SQL legado)'} |")
    return "\n".join(L) + "\n"


def generar_columnas_fecha() -> str:
    from reportes.cli_tablas import filas_columnas_fecha
    from reportes.registro import REPORTES, ordenados
    from reportes.tablas import TABLAS

    filas = filas_columnas_fecha()
    L = ["# Columnas que controlan la fecha de corte", "",
         "> **Generado** desde `src/reportes/tablas.py` y `src/reportes/reglas_fecha.py` (leyendo el SQL de cada reporte). No editar a mano; "
         "CSV para Producción: `python main.py columnas-fecha --csv columnas.csv`.", "",
         "Para **Producción**: al cargar el cierre, la columna de la tabla indicada debe quedar con la **fecha de corte**; los reportes validan y filtran por ella. "
         "Notación: D = corte diario · F = corte mensual (fin de mes) · «cierre hábil» = `RCIEBT = 1` en `storage.ref.rcalen001`.", "",
         "## 1. Por tabla (qué columna debe llevar la fecha del cierre)", "", "| Tabla | Conexión | Columna de fecha | Reportes que la usan |", "|---|---|---|---|"]
    por_tabla: dict[str, list[str]] = {}
    for f in filas:
        por_tabla.setdefault(f["tabla"], []).append(f["reporte"])
    for n in sorted(TABLAS):
        t = TABLAS[n]
        if t.col_fecha and n in por_tabla:
            L.append(f"| `{n}` | `{t.servidor}` | `{t.col_fecha}` | {', '.join(f'`{r}`' for r in por_tabla[n])} |")
    sin = sorted(n for n in por_tabla if not TABLAS[n].col_fecha)
    L += ["", f"Sin columna de fecha de corte ({len(sin)}: catálogos, funciones o tablas que genera el reporte): " + ", ".join(f"`{n}`" for n in sin), "",
          "## 2. Por reporte (condición exacta)", ""]
    for r in ordenados():
        L += [f"### {REPORTES[r.nombre].etiqueta} · `{r.nombre}`", "", "| Tabla | Columna | Condición que aplica el reporte |", "|---|---|---|"]
        for f in (x for x in filas if x["reporte"] == r.nombre):
            L.append(f"| `{f['tabla']}` | {('`' + f['columna_fecha'] + '`') if f['columna_fecha'] else '—'} | {f['condicion']} |")
        L.append("")
    return "\n".join(L) + "\n"


def generar_comandos() -> str:
    from importlib import import_module

    from reportes.registro import TITULOS_GRUPO, ordenados
    from reportes.tablas import TABLAS, USO

    L = ["# Catálogo de comandos", "",
         "> **Generado** por `governance/scripts/generar_inventario.py` desde `registro.py`, `tablas.py` y los módulos. No editar a mano.", "",
         "Los reportes **los ejecutas tú, cuando quieras** (no hay tareas programadas): `python main.py <comando>`. La fecha de corte sale de `FECHA_CORTE_MENSUAL` / `FECHA_CORTE_DIARIA` del `.env`, o de `--fecha-corte AAAA-MM-DD` (que manda sobre el `.env`). El ejecutor común valida las tablas al corte "
         "(si falta alguna, **no ejecuta** y deja el mensaje para Producción), consulta, valida los datos y exporta el Excel a `data/outputs/mensuales/<piero|erick>/<NN_nombre>/` (diarios: `data/outputs/diarias/<NN_nombre>/`). La numeración es la de las carpetas del legado. "
         "Proceso completo: [ejecutar un reporte](./ejecutar-un-reporte.md).", "",
         "Opciones comunes de los reportes de lote: `--solo-verificar` · `--forzar` · `--sin-verificar` · `--confirmar-escritura` (solo si escribe en BD) · `--salida DIR` · `-v`.", ""]
    grupo_actual = None
    for r in ordenados():
        if r.grupo != grupo_actual:
            grupo_actual = r.grupo
            L += [f"# {TITULOS_GRUPO[r.grupo]}", ""]
        mod = import_module(r.modulo)
        lote = getattr(mod, "REPORTE", None)
        L += [f"## {r.etiqueta} · `{r.nombre}` — {r.frecuencia}", "", r.descripcion, ""]
        var = "FECHA_CORTE_MENSUAL" if r.frecuencia == "mensual" else "FECHA_CORTE_DIARIA"
        arg = f"[--fecha-corte AAAA-MM-DD]   # sin la opción usa {var} del .env"
        L += ["```bash", f"python main.py tablas {r.nombre} --verificar   # ¿tablas al día? (fecha del .env)", f"python main.py {r.nombre} {arg}", "```", ""]
        criticas = [TABLAS[n] for n in USO[r.nombre] if TABLAS[n].verificable]
        L.append(f"- **Servidor**: `{'`, `'.join(r.servidores)}` · **Tablas**: {len(USO[r.nombre])} ({len(criticas)} verificables por fecha) → [inventario](../../data/tables-inventory.md)")
        if criticas:
            L.append("- **Críticas** (se validan al corte): " + ", ".join(f"`{t.nombre}`" for t in criticas))
        if lote is not None:
            if lote.base:
                L.append(f"- **Base de datos**: `{lote.base}` (editable en el módulo; el servidor lo define el `.env`)")
            patron = lote.archivo or ("".join(x.capitalize() for x in r.nombre.split("-")) + "_{AAAAMMDD}")
            hojas = ", ".join(f"`{h.nombre}`" for h in lote.hojas) or "una hoja por resultado (`Datos`, `Datos_2`…)"
            extra = "".join(f", `{rs.nombre}` (resumen jerárquico)" for rs in lote.resumenes)
            L.append(f"- **Salida**: `data/outputs/{r.carpeta}/{patron}.xlsx` · hojas: {hojas}{extra}" + (" · libro compartido con otro comando" if lote.libro_compartido else ""))
            if lote.vacio_valido:
                L.append("- **Vacío válido**: sí (puede no haber datos en el mes)")
            if lote.escribe_en_bd:
                L.append("- ⚠ **Escribe en BD** (crea/borra tablas permanentes): exige `--confirmar-escritura`")
            for a in lote.avisos:
                L.append(f"- ⚠ {a}")
        else:
            L.append(f"- Guía propia: [runbook](./{r.nombre}.md)")
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    pares = [(SALIDA, generar()), (SALIDA_TABLAS, generar_tablas()), (SALIDA_COLUMNAS, generar_columnas_fecha()), (SALIDA_COMANDOS, generar_comandos())]
    if a.check:
        viejos = [d.name for d, nuevo in pares if not d.exists() or d.read_text(encoding="utf-8") != nuevo]
        if viejos:
            print(f"Desactualizado: {', '.join(viejos)}. Ejecuta generar_inventario.py")
            return 1
        return 0
    for destino, nuevo in pares:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(nuevo, encoding="utf-8")
        print(f"Escrito {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
