"""Alta de un reporte desde la web: validación y texto de lo que se escribe (módulo, test y líneas de registro). Sin disco ni estado."""

from __future__ import annotations

import re
import unicodedata
from datetime import date

from core.excepciones import ConfiguracionError, PeticionInvalida
from core.servidores import BASES_DE, servidor_de_base
from modulos.reportes.dominio.fechas import Cortes

SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
ORDEN = re.compile(r"\d{2}(\.\d{1,2})?")
FECHA_FIJA = re.compile(r"'(20\d{6}|20\d\d-\d\d-\d\d)'")  # misma regla que la compuerta fechas-fijas-en-sql
# Misma extracción que governance/scripts/extraer_tablas.py (tablas de 3 partes tras FROM/JOIN/INTO/UPDATE/EXEC).
_RX_TABLA = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE|TRUNCATE\s+TABLE|EXEC(?:UTE)?)\s+(\[?[A-Za-z_{][\w$#.{}\[\]]*)", re.I)
_BASE = {"diarias": ("diarios", "diarias"), "piero": ("mensuales/piero", "mensuales/piero"), "erick": ("mensuales/erick", "mensuales/erick")}


def validar_identidad(nombre: str, orden: str) -> None:
    if not SLUG.fullmatch(nombre) or len(nombre) > 60:
        raise PeticionInvalida("El nombre va en minúsculas, números y guiones (ej. cartera-sin-asignar).")
    if not ORDEN.fullmatch(orden):
        raise PeticionInvalida("El número del legado tiene la forma 07 o 07.1.")


def id_de_grupo(nombre: str) -> str:
    """«Cierre de riesgos» → «cierre-de-riesgos» (sin tildes; es la URL, la carpeta del módulo y la de salida)."""
    plano = unicodedata.normalize("NFKD", nombre.strip().lower()).encode("ascii", "ignore").decode()
    id_ = re.sub(r"[^a-z0-9]+", "-", plano).strip("-")[:30]
    if not id_ or any(c in nombre for c in "\r\n#\"'"):
        raise PeticionInvalida("Ponle un nombre al grupo (letras y números; sin #, comillas ni saltos de línea).")
    return id_


def validar_sql(sql: str, frecuencia: str, servidor: str) -> list[str]:
    """Comprueba el T-SQL como lo hará el ejecutor y devuelve las tablas que consulta (normalizadas, en minúsculas)."""
    if not sql.strip():
        raise PeticionInvalida("Pega el T-SQL del reporte.")
    if '"""' in sql:
        raise PeticionInvalida('El T-SQL no puede contener """ (rompería el módulo).')
    sin_comentarios = re.sub(r"--.*", "", re.sub(r"/\*.*?\*/", "", sql, flags=re.S))
    if FECHA_FIJA.search(sin_comentarios):
        raise PeticionInvalida("El T-SQL trae una fecha literal: usa un token (@@F@@, @@F_ISO@@, @@F_ANT@@…).")
    prueba = date(2026, 7, 31)  # fin de mes: vale para ambas frecuencias
    try:
        resuelto = (Cortes.mensual(prueba) if frecuencia == "mensual" else Cortes(prueba)).aplicar(sql)
    except ConfiguracionError as exc:
        raise PeticionInvalida("Hay un token @@…@@ que no existe. Se resuelven @@F@@, @@F_ISO@@, @@F_ANT@@… (ver reportes existentes).") from exc
    if resuelto == sql:
        raise PeticionInvalida("El T-SQL no usa ningún token de fecha: el corte no entraría en la consulta.")
    tablas = tablas_de_sql(sql)
    ajenas = [t for t in tablas if _servidor(t) not in (None, servidor)]
    if ajenas:
        raise PeticionInvalida(f"Un reporte se conecta a un solo servidor ({servidor}); estas tablas viven en otro: {', '.join(ajenas)}.")
    return tablas


def _servidor(tabla: str) -> str | None:
    try:
        return servidor_de_base(tabla.split(".")[0])
    except ConfiguracionError:
        return None


def tablas_de_sql(sql: str) -> list[str]:
    texto = re.sub(r"--[^\n]*", "", re.sub(r"/\*.*?\*/", "", sql, flags=re.S))
    salida: set[str] = set()
    for m in _RX_TABLA.finditer(texto):
        n = m.group(1).replace("[", "").replace("]", "").rstrip(".").lower()
        n = re.sub(r"\bdb\d{6}\b", "db{yyyymm}", n)
        n = re.sub(r"(?<=[a-z])\d{8}\b", "{yyyymmdd}", n)
        partes = n.split(".")
        if len(partes) >= 3 and (partes[0] == "db{yyyymm}" or partes[0] in {b for bs in BASES_DE.values() for b in bs}):
            salida.add(n)
    return sorted(salida)


def rutas(grupo: str, frecuencia: str, orden: str, nombre: str, carpeta_existente: str | None) -> tuple[str, str, str]:
    """(módulo importable, ruta relativa del módulo bajo src/, carpeta de salida bajo data/outputs). Los grupos propios viven en catalogo/grupos/<id>."""
    dir_modulo, base_salida = _BASE.get(grupo) or (f"grupos/{grupo.replace('-', '_')}", f"{'diarias' if frecuencia == 'diaria' else 'mensuales'}/{grupo.replace('-', '_')}")
    mod = f"r{orden.replace('.', '_')}_{nombre.replace('-', '_')}"
    paquete = f"modulos.reportes.catalogo.{dir_modulo.replace('/', '.')}"
    salida = carpeta_existente or f"{base_salida}/{orden.split('.')[0]}_{nombre.replace('-', '_')}"
    return f"{paquete}.{mod}", f"{paquete.replace('.', '/')}/{mod}.py", salida


def render_modulo(nombre: str, descripcion: str, frecuencia: str, servidor: str, base: str, sql: str) -> str:
    return f'''"""{descripcion}

Comando: python main.py {nombre} --fecha-corte AAAA-MM-DD
Creado desde la web. T-SQL con tokens de fecha (@@F@@…); el ejecutor común valida tablas al corte, ejecuta,
valida datos y exporta a data/outputs/. Tablas: ver tablas.USO["{nombre}"].
"""

from __future__ import annotations

from modulos.reportes.aplicacion.ejecucion import ReporteLote, correr

SQL = r"""
{sql.strip()}
"""

REPORTE = ReporteLote(
    comando={nombre!r},
    descripcion={descripcion!r},
    frecuencia={frecuencia!r},
    servidor={servidor!r},
    base={base!r},
    sql=SQL,
)


def main(argv: list[str] | None = None) -> int:
    return correr(REPORTE, argv)
'''


def render_test(nombre: str, modulo: str, frecuencia: str) -> str:
    corte = "Cortes.mensual(date(2026, 7, 31))" if frecuencia == "mensual" else "Cortes(date(2026, 7, 31))"
    return f'''"""Reporte «{nombre}» (creado desde la web): su módulo importa, resuelve los tokens de fecha y es coherente con el registro."""

from datetime import date

from {modulo.rsplit(".", 1)[0]} import {modulo.rsplit(".", 1)[1]} as m
from modulos.reportes.dominio.fechas import Cortes
from modulos.reportes.dominio.reportes import REPORTES
from modulos.reportes.dominio.tablas import USO


def test_registrado_y_con_tokens_resueltos():
    assert m.REPORTE.comando == {nombre!r} and {nombre!r} in REPORTES and {nombre!r} in USO
    sql = {corte}.aplicar(m.REPORTE.sql)
    assert "@@" not in sql and ("20260731" in sql or "2026-07-31" in sql)


def test_main_existe():
    assert callable(m.main)
'''


def insertar_definicion(texto: str, nombre: str, grupo: str, orden: str, modulo: str, carpeta: str, servidor: str, descripcion: str) -> str:
    """Añade la tupla al final de `_DEFINICION` en dominio/reportes.py."""
    ancla = "]\n\nREPORTES: dict"
    if ancla not in texto:
        raise PeticionInvalida("No pude ubicar _DEFINICION en dominio/reportes.py; regístralo a mano.")
    fila = f"    ({nombre!r}, {grupo!r}, {orden!r}, {modulo!r}, {carpeta!r}, ({servidor!r},),\n     {descripcion!r}),\n"
    return texto.replace(ancla, fila + ancla, 1)


def insertar_tablas(texto: str, nombre: str, usadas: list[str], nuevas: list[str]) -> str:
    """Añade las tablas nuevas a `_FILAS` y el reporte a `USO` en dominio/tablas.py."""
    ancla_filas, ancla_uso = "]\n\nTABLAS: dict", "}\n\n\ndef tablas_de"
    if ancla_filas not in texto or ancla_uso not in texto:
        raise PeticionInvalida("No pude ubicar _FILAS/USO en dominio/tablas.py; regístralo a mano.")
    filas = "".join(f"    ({t!r}, 'referencia', None, 'por_confirmar'),\n" for t in nuevas)
    uso = f"    {nombre!r}: (\n" + "".join(f"        {t!r},\n" for t in usadas) + "    ),\n"
    return texto.replace(ancla_filas, filas + ancla_filas, 1).replace(ancla_uso, uso + ancla_uso, 1)


def regla_provisional(letra: str, col_fecha: str | None, tipo: str) -> str:
    """Condición de fecha a documentar en dominio/reglas_fecha.py; la columna ya registrada se nombra, el resto queda por completar."""
    if col_fecha and tipo in {"historica", "stock"}:
        return f"{col_fecha} = {letra} (por confirmar: reporte creado desde la web)"
    return "por documentar: reporte creado desde la web"


def insertar_reglas(texto: str, nombre: str, reglas: dict[str, str]) -> str:
    """Añade el reporte al final de `REGLAS` en dominio/reglas_fecha.py."""
    fin = texto.rstrip().rfind("\n}")
    if fin < 0:
        raise PeticionInvalida("No pude ubicar REGLAS en dominio/reglas_fecha.py; regístralo a mano.")
    bloque = f"    {nombre!r}: {{\n" + "".join(f"        {t!r}: {r!r},\n" for t, r in reglas.items()) + "    },\n"
    return texto[: fin + 1] + bloque + texto[fin + 1:]


def insertar_grupo(texto: str, id_: str, nombre: str, frecuencia: str) -> str:
    """Añade el grupo a `_GRUPOS_EXTRA` en dominio/reportes.py."""
    ancla = "_GRUPOS_EXTRA: list[tuple[str, str, str]] = [\n"
    if ancla not in texto:
        raise PeticionInvalida("No pude ubicar _GRUPOS_EXTRA en dominio/reportes.py; regístralo a mano.")
    return texto.replace(ancla, ancla + f"    ({id_!r}, {nombre!r}, {frecuencia!r}),\n", 1)


def quitar_grupo(texto: str, id_: str) -> str:
    """Quita el grupo de `_GRUPOS_EXTRA` en dominio/reportes.py."""
    nuevo, n = re.subn(rf"^    \({re.escape(repr(id_))}, [^\n]*\),\n", "", texto, count=1, flags=re.M)
    if not n:
        raise PeticionInvalida(f"No encontré «{id_}» en _GRUPOS_EXTRA de dominio/reportes.py; quítalo a mano.")
    return nuevo
