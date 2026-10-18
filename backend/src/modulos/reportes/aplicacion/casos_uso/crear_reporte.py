"""Alta de un reporte desde la web: escribe su módulo, su test y su registro, y lo deja disponible sin reiniciar."""

from __future__ import annotations

import functools
import re
import shutil
import threading
from pathlib import Path

from core.excepciones import ConfiguracionError, NoEncontrado, PeticionInvalida
from core.servidores import servidor_de_base
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion import nuevo_reporte as nr
from modulos.reportes.aplicacion.casos_uso import etiquetas
from modulos.reportes.aplicacion.puertos import puertos
from modulos.reportes.dominio import reglas_fecha, reportes as dominio, tablas as dominio_tablas

BACK = Path(__file__).resolve().parents[5]
_CANDADO = threading.RLock()  # alta y baja leen y reescriben los mismos archivos del registro: de a una


def _exclusivo(f):
    @functools.wraps(f)
    def envuelta(*a, **k):
        with _CANDADO:
            return f(*a, **k)
    return envuelta


def _limpiar_grupo(carpeta: Path, tope: Path) -> None:
    """Quita la carpeta de un grupo propio (catalogo/grupos/<id>) cuando ya solo queda su __init__.py y cachés."""
    if carpeta.parent == tope and carpeta.is_dir() and all(q.name in {"__init__.py", "__pycache__"} for q in carpeta.iterdir()):
        shutil.rmtree(carpeta)


@_exclusivo
def crear(p: dto_reportes.PedidoReporteNuevo, raiz: Path = BACK, en_vivo: bool = True) -> dto_reportes.ReporteCreado:
    nombre, descripcion, sql = p.nombre.strip(), " ".join(p.descripcion.split()), p.sql.strip() or nr.PLANTILLA_SQL
    nr.validar_identidad(nombre, p.orden)
    if p.grupo not in dominio.GRUPOS:
        raise PeticionInvalida(f"No existe el grupo «{p.grupo}».")
    if not descripcion:
        raise PeticionInvalida("Escribe una descripción.")
    if nombre in dominio.REPORTES:
        raise PeticionInvalida(f"Ya existe el reporte «{nombre}».")
    if any(r.grupo == p.grupo and r.orden == p.orden for r in dominio.REPORTES.values()):
        raise PeticionInvalida(f"Ya hay un reporte {p.orden} en {p.grupo}.")
    usa = re.search(r"^\s*use\s+\[?(\w+)\]?", sql, re.I | re.M)
    base = p.base or (usa.group(1).lower() if usa else "")
    if not base:
        raise PeticionInvalida("El T-SQL debe empezar con `use <base>;` para saber a qué base conectarse.")
    try:
        servidor = servidor_de_base(base)
    except ConfiguracionError as exc:
        raise PeticionInvalida(str(exc)) from exc
    frecuencia = p.frecuencia or dominio.FRECUENCIA_GRUPO[p.grupo]
    if p.grupo in dominio.GRUPOS_BASE and frecuencia != dominio.FRECUENCIA_GRUPO[p.grupo]:
        raise PeticionInvalida(f"El grupo «{dominio.NOMBRE_GRUPO[p.grupo]}» solo admite reportes {dominio.FRECUENCIA_GRUPO[p.grupo]}s.")
    try:
        usadas = nr.validar_sql(sql, frecuencia, servidor)
    except ConfiguracionError as exc:
        raise PeticionInvalida(str(exc)) from exc

    hermano = next((r for r in dominio.REPORTES.values() if r.grupo == p.grupo and r.frecuencia == frecuencia and r.orden.split(".")[0] == p.orden.split(".")[0]), None)
    modulo, ruta_mod, carpeta = nr.rutas(p.grupo, frecuencia, p.orden, nombre, hermano.carpeta if hermano else None)
    destino = raiz / "src" / ruta_mod
    prueba = raiz / "tests" / Path(ruta_mod).with_name(f"test_{destino.stem}.py")
    if destino.exists():
        raise PeticionInvalida(f"Ya existe {ruta_mod}.")
    nuevas = [t for t in usadas if t not in dominio_tablas.TABLAS]

    f_rep, f_tab = raiz / "src/modulos/reportes/dominio/reportes.py", raiz / "src/modulos/reportes/dominio/tablas.py"
    texto_rep = nr.insertar_definicion(f_rep.read_text(encoding="utf-8"), nombre, p.grupo, p.orden, modulo, carpeta, servidor, descripcion)
    texto_tab = nr.insertar_tablas(f_tab.read_text(encoding="utf-8"), nombre, usadas, nuevas)
    f_reg = raiz / "src/modulos/reportes/dominio/reglas_fecha.py"
    reglas = {}
    for t in usadas:
        conocida = dominio_tablas.TABLAS.get(t)
        reglas[t] = nr.regla_provisional("D" if frecuencia == "diaria" else "F", conocida and conocida.col_fecha, conocida.tipo if conocida else "")
    texto_reg = nr.insertar_reglas(f_reg.read_text(encoding="utf-8"), nombre, reglas)

    creados = [destino, prueba]
    originales = {f: f.read_text(encoding="utf-8") for f in (f_rep, f_tab, f_reg)}
    try:
        for ruta, texto in ((destino, nr.render_modulo(nombre, descripcion, frecuencia, servidor, base, sql)),
                            (prueba, nr.render_test(nombre, modulo, frecuencia))):
            ruta.parent.mkdir(parents=True, exist_ok=True)
            tope = raiz / ("tests" if ruta is prueba else "src")  # ambos árboles son de paquetes: cada carpeta nueva lleva su __init__.py
            for q in (ruta.parent, *ruta.parent.parents):
                if q == tope:
                    break
                (q / "__init__.py").touch()
            ruta.write_text(texto, encoding="utf-8", newline="\n")
        f_rep.write_text(texto_rep, encoding="utf-8", newline="")
        f_tab.write_text(texto_tab, encoding="utf-8", newline="")
        f_reg.write_text(texto_reg, encoding="utf-8", newline="")
    except OSError:
        for ruta in creados:
            ruta.unlink(missing_ok=True)
        for f, t in originales.items():  # el registro vuelve a como estaba: nunca apunta a un módulo que no existe
            f.write_text(t, encoding="utf-8", newline="")
        raise

    if en_vivo:  # disponible ya, sin reiniciar el servidor
        dominio.REPORTES[nombre] = dominio.Reporte(nombre, modulo, frecuencia, (servidor,), descripcion, p.grupo, p.orden, carpeta)
        for t in nuevas:
            dominio_tablas.TABLAS[t] = dominio_tablas.Tabla(t, "referencia", None, "por_confirmar")
        dominio_tablas.USO[nombre] = tuple(usadas)
        reglas_fecha.REGLAS[nombre] = reglas
    return dto_reportes.ReporteCreado(nombre=nombre, ruta=f"backend/src/{ruta_mod}", tablas_nuevas=nuevas)


@_exclusivo
def eliminar(nombre: str, raiz: Path = BACK, en_vivo: bool = True) -> None:
    """Deshace `crear`: borra módulo, test y registro. Solo reportes creados desde la web; nunca los del legado."""
    r = dominio.REPORTES.get(nombre)
    if r is None:
        raise NoEncontrado(f"No existe el reporte «{nombre}».")
    ruta_mod = r.modulo.replace(".", "/") + ".py"
    destino = raiz / "src" / ruta_mod
    if nr.MARCA_WEB not in destino.read_text(encoding="utf-8"):
        raise PeticionInvalida("Solo se eliminan reportes creados desde la web; los del legado no.")
    if any(x.estado in {"en_cola", "ejecutando"} for x in puertos().cola.historial(nombre)):
        raise PeticionInvalida("El reporte tiene una ejecución en curso: espera a que termine para eliminarlo.")
    archivos = [raiz / "src/modulos/reportes/dominio" / f for f in ("reportes.py", "tablas.py", "reglas_fecha.py")]
    originales = {f: f.read_text(encoding="utf-8") for f in archivos}
    nuevos = {f: nr.quitar_reporte(originales[f], pat, f.name) for f, pat in zip(archivos, nr.patrones_de_reporte(nombre))}  # si algo no casa, no se toca nada
    prueba = raiz / "tests" / Path(ruta_mod).with_name(f"test_{destino.stem}.py")
    try:
        for f, t in nuevos.items():
            f.write_text(t, encoding="utf-8", newline="")
        destino.unlink()
        prueba.unlink(missing_ok=True)
    except OSError:
        for f, t in originales.items():
            f.write_text(t, encoding="utf-8", newline="")
        raise
    _limpiar_grupo(destino.parent, raiz / "src/modulos/reportes/catalogo/grupos")
    _limpiar_grupo(prueba.parent, raiz / "tests/modulos/reportes/catalogo/grupos")
    if en_vivo:
        dominio.REPORTES.pop(nombre, None)
        dominio_tablas.USO.pop(nombre, None)
        reglas_fecha.REGLAS.pop(nombre, None)


def _grupo(g: str, catalogo: dto_reportes.CatalogoEtiquetas) -> dto_reportes.Grupo:
    return dto_reportes.Grupo(id=g, nombre=dominio.NOMBRE_GRUPO[g], frecuencia=dominio.FRECUENCIA_GRUPO[g], propio=g not in dominio.GRUPOS_BASE,
                              reportes=sum(1 for r in dominio.REPORTES.values() if r.grupo == g), etiquetas=etiquetas.de_grupo(g, catalogo))


def listar_grupos() -> list[dto_reportes.Grupo]:
    catalogo = puertos().etiquetas.leer()
    return [_grupo(g, catalogo) for g in dominio.GRUPOS]


@_exclusivo
def crear_grupo(p: dto_reportes.PedidoGrupo, raiz: Path = BACK, en_vivo: bool = True) -> dto_reportes.Grupo:
    """Un grupo nuevo, con sus etiquetas, donde luego se crean reportes. Queda escrito en dominio/reportes.py."""
    nombre = " ".join(p.nombre.split())
    id_ = nr.id_de_grupo(nombre)
    if id_ in dominio.GRUPOS or any(n.casefold() == nombre.casefold() for n in dominio.NOMBRE_GRUPO.values()):
        raise PeticionInvalida(f"Ya existe un grupo «{nombre}».")
    etiquetas.asignar(id_, p.etiquetas)  # valida las etiquetas antes de tocar el código
    f_rep = raiz / "src/modulos/reportes/dominio/reportes.py"
    f_rep.write_text(nr.insertar_grupo(f_rep.read_text(encoding="utf-8"), id_, nombre, "mensual"), encoding="utf-8", newline="")
    if en_vivo:
        dominio.registrar_grupo(id_, nombre, "mensual")
    return dto_reportes.Grupo(id=id_, nombre=nombre, frecuencia="mensual", propio=True, reportes=0, etiquetas=etiquetas.de_grupo(id_))


def asignar_etiquetas(id_: str, p: dto_reportes.PedidoEtiquetasGrupo) -> dto_reportes.Grupo:
    if id_ not in dominio.GRUPOS:
        raise NoEncontrado(f"No existe el grupo «{id_}».")
    etiquetas.asignar(id_, p.etiquetas)
    return _grupo(id_, puertos().etiquetas.leer())


@_exclusivo
def eliminar_grupo(id_: str, raiz: Path = BACK, en_vivo: bool = True) -> None:
    """Quita un grupo creado desde la web. Solo si está vacío (como en Dokploy: primero se borran sus servicios) y nunca los del legado."""
    if id_ not in dominio.GRUPOS:
        raise NoEncontrado(f"No existe el grupo «{id_}».")
    if id_ in dominio.GRUPOS_BASE:
        raise PeticionInvalida("Los grupos del legado (diarias, piero, erick) no se eliminan.")
    n = sum(1 for r in dominio.REPORTES.values() if r.grupo == id_)
    if n:
        raise PeticionInvalida(f"El grupo tiene {n} {'reporte' if n == 1 else 'reportes'}: elimínalos primero.")
    f_rep = raiz / "src/modulos/reportes/dominio/reportes.py"
    f_rep.write_text(nr.quitar_grupo(f_rep.read_text(encoding="utf-8"), id_), encoding="utf-8", newline="")
    etiquetas.quitar_grupo(id_)
    if en_vivo:
        dominio.quitar_grupo(id_)
