"""Motor de reglas de gobernanza de REPORTES-AUTOMATIZADOS.

    python governance/scripts/validar_gobernanza.py                    # todos los hallazgos
    python governance/scripts/validar_gobernanza.py --listar           # catálogo de reglas
    python governance/scripts/validar_gobernanza.py --linea-base --check   # exige cero hallazgos NUEVOS
    python governance/scripts/validar_gobernanza.py --guardar-linea-base   # congelar deuda (deliberado, ADR-0003)
    python governance/scripts/validar_gobernanza.py --regla=secretos-en-codigo

Código de salida: 1 si hay errores (o hallazgos nuevos con --check); los avisos no bloquean.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BACK = RAIZ / "backend"  # el motor Python vive en backend/; governance/ queda en la raíz
sys.path.insert(0, str(BACK / "src"))
sys.path.insert(0, str(BACK))   # config/ (proyecto Django y composición)
from config import composicion  # noqa: F401 - conecta los adaptadores reales a los puertos
sys.path.insert(0, str(Path(__file__).resolve().parent))
LINEA_BASE = RAIZ / "governance" / "gobernanza.linea-base.json"
FUENTES = [p for base in (BACK / "src", BACK / "config") for p in base.rglob("*.py") if "__pycache__" not in p.parts] + [BACK / "main.py", BACK / "manage.py"]


@dataclass(frozen=True)
class Hallazgo:
    regla: str
    nivel: str  # error | aviso
    archivo: str
    detalle: str

    @property
    def clave(self) -> str:
        return f"{self.regla}|{self.archivo}|{self.detalle}"


def rel(p: Path) -> str:
    return p.relative_to(BACK).as_posix()  # rutas de la línea base relativas a backend/


# ---------------------------------------------------------------- reglas
def r_secretos(): 
    patrones = [
        (re.compile(r"(?i)\b(PWD|UID)=(?![{;'\"\s])[^;'\"\s]+"), "cadena de conexión con credencial literal"),
        (re.compile(r"(?i)\b(password|passwd|pwd|clave)\s*=\s*r?[\"'][^\"']{3,}[\"']"), "contraseña asignada como literal"),
    ]
    for p in FUENTES:
        for n, linea in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if linea.lstrip().startswith(("#", "--")):
                continue
            for rx, msg in patrones:
                if rx.search(linea):
                    yield Hallazgo("secretos-en-codigo", "error", rel(p), f"L{n}: {msg}")


def r_conexion(): 
    for p in FUENTES:
        if p.name == "bd.py" and p.parent.name == "core":
            continue
        txt = p.read_text(encoding="utf-8")
        for rx, msg in ((r"pyodbc\.connect\(", "pyodbc.connect fuera de core/bd.py"), (r"\bcreate_engine\(", "create_engine fuera de core/bd.py")):
            if re.search(rx, txt):
                yield Hallazgo("conexion-solo-en-db", "error", rel(p), msg)


def r_rutas(): 
    rx = re.compile(r"(?<![A-Za-z0-9_])[A-Z]:\\\\?[A-Za-z0-9_ ]")
    for p in FUENTES:
        for n, linea in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if linea.lstrip().startswith(("#", "--")):
                continue
            if rx.search(linea):
                yield Hallazgo("rutas-absolutas", "error", rel(p), f"L{n}: ruta absoluta de Windows")


def r_registro():
    from core.configuracion import SERVIDORES
    from modulos.reportes.dominio.reportes import REPORTES

    for r in REPORTES.values():
        ruta = BACK / "src" / (r.modulo.replace(".", "/") + ".py")
        if not ruta.exists():
            yield Hallazgo("registro-sincronizado", "error", "src/modulos/reportes/dominio/reportes.py", f"{r.nombre}: módulo {r.modulo} no existe")
            continue
        if not re.search(r"^def main\(", ruta.read_text(encoding="utf-8"), re.M):
            yield Hallazgo("registro-sincronizado", "error", rel(ruta), "el módulo no define main(argv)")
        for b in r.servidores:
            if b not in SERVIDORES:
                yield Hallazgo("registro-sincronizado", "error", "src/modulos/reportes/dominio/reportes.py", f"{r.nombre}: servidor '{b}' no está en core/configuracion.py (SERVIDORES)")
    registrados = {r.modulo for r in REPORTES.values()}
    for carpeta in ("diarios", "mensuales"):
        for p in sorted((BACK / "src" / "modulos" / "reportes" / "catalogo" / carpeta).rglob("*.py")):
            mod = ".".join(p.relative_to(BACK / "src").with_suffix("").parts)
            if p.stem != "__init__" and mod not in registrados:
                yield Hallazgo("registro-sincronizado", "aviso", rel(p), "módulo sin registrar en modulos/reportes/dominio/reportes.py")
    for r in REPORTES.values():
        esperado = "r" + r.orden.replace(".", "_")
        if not r.modulo.rsplit(".", 1)[1].startswith(esperado + "_"):
            yield Hallazgo("registro-sincronizado", "error", "src/modulos/reportes/dominio/reportes.py", f"{r.nombre}: el módulo debe empezar por {esperado}_ (número del legado {r.orden})")
        if not r.carpeta.split("/")[-1].startswith(r.orden.split(".")[0] + "_"):
            yield Hallazgo("registro-sincronizado", "error", "src/modulos/reportes/dominio/reportes.py", f"{r.nombre}: la carpeta de salida debe empezar por {r.orden.split('.')[0]}_")


def r_nombres():
    ok = re.compile(r"^[a-z0-9_]+(\.[a-z]+)?$")
    for p in (BACK / "src").rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        for parte in p.relative_to(BACK).parts:
            if not ok.match(parte):
                yield Hallazgo("nombres-canonicos", "aviso", rel(p), f"'{parte}' debe ser snake_case sin espacios ni tildes")
                break


def r_fechas_fijas():
    """El T-SQL incrustado no puede traer fechas literales: usa tokens @@F@@, @@F_ISO@@, @@F_ANT@@… (se resuelven por --fecha-corte)."""
    rx = re.compile(r"'(20\d{6}|20\d\d-\d\d-\d\d)'")
    for p in FUENTES:
        txt = p.read_text(encoding="utf-8")
        if "ReporteLote(" not in txt:
            continue
        dentro_bloque = False
        for n, linea in enumerate(txt.splitlines(), 1):
            if "/*" in linea:
                dentro_bloque = True
            codigo = re.sub(r"--.*", "", linea)
            if not dentro_bloque and rx.search(codigo) and "2021-01-30" not in codigo:
                yield Hallazgo("fechas-fijas-en-sql", "error", rel(p), f"L{n}: fecha literal en el SQL; usa un token @@F@@/@@F_ISO@@…")
            if "*/" in linea:
                dentro_bloque = False


def r_prueba():
    tests = {p.name for p in (BACK / "tests").rglob("test_*.py")} if (BACK / "tests").exists() else set()
    for p in FUENTES:
        if p.stem in {"__init__", "main", "manage"} or ("web" in p.parts and "interfaces" in p.parts) or p.name in {"settings.py", "urls.py", "wsgi.py"}:  # vistas, rutas y ajustes de Django se prueban por HTTP (tests/config/test_api.py)
            continue
        if f"test_{p.stem}.py" not in tests:
            yield Hallazgo("prueba-vecina", "aviso", rel(p), "sin tests/test_<modulo>.py")


def r_env():
    from core.configuracion import SERVIDORES

    ejemplo = (BACK / ".env.example").read_text(encoding="utf-8")
    for b in SERVIDORES.values():
        for suf in ("SERVER", "USER", "PASSWORD"):
            if f"{b.prefijo}_{suf}" not in ejemplo:
                yield Hallazgo("env-example-completo", "error", ".env.example", f"falta {b.prefijo}_{suf}")


def r_gitignore():
    g = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
    for req in (".env", "/data/*", "*.pkl"):
        if req not in g:
            yield Hallazgo("gitignore-protege-datos", "error", ".gitignore", f"falta '{req}'")


def r_tablas():
    import extraer_tablas as ex
    from modulos.reportes.dominio.reportes import REPORTES
    from modulos.reportes.dominio.tablas import TABLAS, USO

    for comando, usadas in ex.por_reporte().items():
        for n in sorted(usadas - set(TABLAS)):
            yield Hallazgo("tabla-sin-registrar", "error", "src/modulos/reportes/dominio/tablas.py", f"{n}: la usa «{comando}» pero no está registrada")
        for n in sorted(usadas - set(USO.get(comando, ()))):
            yield Hallazgo("tabla-sin-registrar", "error", "src/modulos/reportes/dominio/tablas.py", f"USO[{comando}] no declara {n}, que el módulo consulta")
    for reporte, nombres in USO.items():
        if reporte not in REPORTES:
            yield Hallazgo("tabla-sin-registrar", "error", "src/modulos/reportes/dominio/tablas.py", f"USO[{reporte}]: reporte inexistente en modulos/reportes/dominio/reportes.py")
        for n in nombres:
            if n not in TABLAS:
                yield Hallazgo("tabla-sin-registrar", "error", "src/modulos/reportes/dominio/tablas.py", f"USO[{reporte}] cita '{n}' inexistente en TABLAS")
    for r in REPORTES:
        if r not in USO:
            yield Hallazgo("tabla-sin-registrar", "error", "src/modulos/reportes/dominio/tablas.py", f"reporte '{r}' sin tablas en USO")
    for t in TABLAS.values():
        if t.tipo in {"historica", "stock"} and not t.col_fecha:
            yield Hallazgo("tabla-sin-fecha", "aviso", "src/modulos/reportes/dominio/tablas.py", f"{t.nombre}: sin columna de fecha, no se puede verificar")
        if t.confianza == "convencion":
            yield Hallazgo("tabla-fecha-por-validar", "aviso", "src/modulos/reportes/dominio/tablas.py", f"{t.nombre}: columna {t.col_fecha} inferida por prefijo; validar con el DBA")


def r_servidor_coherente():
    """Un T-SQL solo puede nombrar bases de SU servidor: las tablas de cada reporte deben vivir en el servidor que declara."""
    from importlib import import_module

    from core.excepciones import ConfiguracionError
    from core.servidores import servidor_de_base
    from modulos.reportes.dominio.reportes import REPORTES
    from modulos.reportes.dominio.tablas import TABLAS, USO

    for r in REPORTES.values():
        try:
            usados = {TABLAS[n].servidor for n in USO.get(r.nombre, ()) if TABLAS[n].tipo != "destino"}
        except ConfiguracionError as exc:
            yield Hallazgo("servidor-coherente", "error", "src/core/servidores.py", f"{r.nombre}: {exc}")
            continue
        fuera = usados - set(r.servidores)
        if fuera:
            yield Hallazgo("servidor-coherente", "error", "src/modulos/reportes/dominio/reportes.py",
                           f"{r.nombre}: usa tablas de {sorted(fuera)} pero declara {list(r.servidores)}")
        lote = getattr(import_module(r.modulo), "REPORTE", None)
        if lote is not None:
            if lote.servidor not in r.servidores:
                yield Hallazgo("servidor-coherente", "error", "src/modulos/reportes/dominio/reportes.py", f"{r.nombre}: ReporteLote.servidor '{lote.servidor}' no está en registro")
            if lote.base and servidor_de_base(lote.base) != lote.servidor:
                yield Hallazgo("servidor-coherente", "error", r.modulo.replace(".", "/") + ".py",
                               f"base '{lote.base}' vive en {servidor_de_base(lote.base)}, no en {lote.servidor}")


# ---------------------------------------------------------------- arquitectura: monolito modular con Clean Architecture dentro de cada módulo
# Qué módulo puede usar a cuál (sin ciclos); config (composición y Django) conoce a todos. Ver ADR-0016.
DEPENDE = {
    "reportes": {"notificaciones", "integraciones"},
    "notificaciones": set(),
    "integraciones": set(),
    "diccionario": {"reportes"},   # cruza el diccionario con el registro de tablas de reportes
    "sistema": {"reportes", "notificaciones", "integraciones"},
}
# capa -> capas del MISMO módulo que puede importar. `catalogo` son los reportes del legado: el anillo exterior del módulo de reportes.
CAPAS_DE_MODULO = {
    "dominio": {"dominio"},
    "aplicacion": {"aplicacion", "dominio"},
    "infraestructura": {"infraestructura", "aplicacion", "dominio"},
    "interfaces": {"interfaces", "aplicacion", "dominio"},
    "catalogo": {"catalogo", "infraestructura", "aplicacion", "dominio"},
}
# `core` (núcleo compartido): lo público lo importa cualquiera; sus adaptadores solo la infraestructura, el catálogo y config.
CORE_ADAPTADORES = {"core.bd", "core.entorno", "core.configuracion"}
USAN_ADAPTADORES_DEL_NUCLEO = {"infraestructura", "catalogo", "config"}
# librerías que dominio y aplicación de un módulo no pueden importar (I/O, frameworks y proveedores); pandas y pydantic son tipos de datos y se admiten en `aplicacion`
SIN_TERCEROS_DOMINIO = {"os", "sys", "subprocess", "smtplib", "urllib.request", "urllib.error", "http.client", "socket", "sqlite3", "requests", "pandas", "pydantic", "fastapi",
                        "starlette", "uvicorn", "django", "sqlalchemy", "pyodbc", "openpyxl", "PIL", "dotenv", "argparse", "logging", "json"}
SIN_TERCEROS_APLICACION = SIN_TERCEROS_DOMINIO - {"pandas", "pydantic", "argparse", "logging", "json", "sys"}
SIN_TERCEROS = {"dominio": SIN_TERCEROS_DOMINIO, "aplicacion": SIN_TERCEROS_APLICACION}


def _ubicar(p: Path):
    """(módulo, capa) de un archivo: ("reportes", "dominio"), ("core", None), ("config", None)… o None si está fuera de la estructura."""
    if p.parent == BACK:                                   # manage.py
        return "config", None
    base = BACK if BACK / "config" in p.parents else BACK / "src"
    partes = p.relative_to(base).parts
    if partes[0] == "config":
        return "config", None
    if partes[0] == "core":
        return "core", None
    if partes[0] == "modulos" and len(partes) > 3 and partes[1] in DEPENDE and partes[2] in CAPAS_DE_MODULO:
        return partes[1], partes[2]
    return None


def r_capas():
    for p in FUENTES:
        if p.name == "__init__.py" or p == BACK / "main.py":
            continue
        ubicacion = _ubicar(p)
        if ubicacion is None:
            yield Hallazgo("arquitectura-capas", "error", rel(p), "archivo fuera de la estructura: core/, config/ o modulos/<módulo>/<dominio|aplicacion|infraestructura|interfaces|catalogo>/")
            continue
        modulo, capa = ubicacion
        for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(n, ast.Import):
                nombres = [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                nombres = [f"{n.module}.{a.name}" for a in n.names]   # `from core import bd` importa el módulo core.bd
            else:
                continue
            for nombre in nombres:
                partes = nombre.split(".")
                aviso = None
                if partes[0] == "core":
                    if modulo != "core" and any(nombre == a or nombre.startswith(a + ".") for a in CORE_ADAPTADORES) and capa not in USAN_ADAPTADORES_DEL_NUCLEO and modulo != "config":
                        aviso = f"«{modulo}/{capa}» no puede importar el adaptador «{nombre}» del núcleo (pídelo por `core.puertos`)"
                elif partes[0] == "modulos" and len(partes) > 1:
                    destino, capa_destino = partes[1], (partes[2] if len(partes) > 2 else None)
                    if modulo == "core":
                        aviso = f"el núcleo no puede depender de «{nombre}» (un módulo)"
                    elif modulo == "config":
                        pass
                    elif destino == modulo:
                        if capa_destino and capa_destino not in CAPAS_DE_MODULO.get(capa, ()):
                            aviso = f"«{capa}» no puede importar «{capa_destino}» (la dependencia solo apunta hacia adentro)"
                    elif destino not in DEPENDE.get(modulo, ()):
                        aviso = f"el módulo «{modulo}» no puede depender de «{destino}» (grafo permitido: {sorted(DEPENDE.get(modulo, ())) or 'ninguno'})"
                    elif capa_destino not in {"dominio", "aplicacion"}:
                        aviso = f"un módulo solo usa el dominio y la aplicación de otro: «{nombre}» no es público"
                    elif capa_destino == "aplicacion" and len(partes) > 3 and partes[3] == "puertos":
                        aviso = f"los puertos de «{destino}» son privados: usa su API pública (`{destino}/aplicacion/…`), no «{nombre}»"
                elif partes[0] == "config" and modulo != "config" and capa != "interfaces":
                    aviso = f"«{modulo}/{capa}» no puede importar «config» (solo las entradas, en `interfaces`)"
                elif capa in SIN_TERCEROS and any(nombre == f or nombre.startswith(f + ".") for f in SIN_TERCEROS[capa]):
                    aviso = f"«{capa}» no puede importar «{nombre}» (I/O o framework: va detrás de un puerto en la infraestructura del módulo)"
                if aviso:
                    yield Hallazgo("arquitectura-capas", "error", rel(p), f"L{n.lineno}: {aviso}")


REGLAS = {
    "secretos-en-codigo": (r_secretos, "Ninguna credencial literal en src/. Solo .env."),
    "conexion-solo-en-db": (r_conexion, "pyodbc/SQLAlchemy se abren únicamente en core/bd.py."),
    "rutas-absolutas": (r_rutas, "Sin rutas D:\\... fijas; usar core/configuracion.py (DIR_OUTPUTS)."),
    "registro-sincronizado": (r_registro, "Todo reporte registrado existe, expone main() y usa servidores válidos (mish/slc/rcc)."),
    "nombres-canonicos": (r_nombres, "Módulos en snake_case, sin espacios ni tildes."),
    "prueba-vecina": (r_prueba, "Cada módulo tiene tests/test_<modulo>.py."),
    "env-example-completo": (r_env, ".env.example declara las variables de las 3 conexiones."),
    "gitignore-protege-datos": (r_gitignore, ".gitignore excluye .env, data/ (inputs y outputs) y cachés."),
    "tabla-sin-registrar": (r_tablas, "Toda tabla que consulta el código está en modulos/reportes/dominio/tablas.py y todo reporte declara sus tablas."),
    "servidor-coherente": (r_servidor_coherente, "Las tablas y la base de cada reporte viven en el servidor que declara (core/servidores.py, BASES_DE)."),
    "arquitectura-capas": (r_capas, "Monolito modular: cada módulo en capas (dominio ← aplicacion ← infraestructura/interfaces), dependencias entre módulos solo por su API pública y sin ciclos (ADR-0016)."),
    "fechas-fijas-en-sql": (r_fechas_fijas, "Sin fechas literales en el T-SQL incrustado: todo por tokens de fecha de corte."),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--regla")
    ap.add_argument("--linea-base", action="store_true", help="descuenta la deuda congelada")
    ap.add_argument("--sin-linea-base", action="store_true", help="muestra el pasivo completo")
    ap.add_argument("--guardar-linea-base", action="store_true")
    ap.add_argument("--check", action="store_true", help="falla si hay hallazgos nuevos")
    a = ap.parse_args(argv)

    if a.listar:
        for n, (_, porque) in REGLAS.items():
            print(f"  {n:<26} {porque}")
        return 0

    seleccion = {a.regla: REGLAS[a.regla]} if a.regla else REGLAS
    hallazgos = [h for fn, _ in seleccion.values() for h in fn()]

    if a.guardar_linea_base:
        LINEA_BASE.write_text(json.dumps({
            "generado": date.today().isoformat(),
            "nota": "Deuda conocida al momento de congelar. Regenerar a propósito, nunca en automático. Ver ADR-0003.",
            "claves": sorted(h.clave for h in hallazgos),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Línea base guardada: {len(hallazgos)} hallazgos congelados.")
        return 0

    congeladas: set[str] = set()
    if a.linea_base and not a.sin_linea_base and LINEA_BASE.exists():
        congeladas = set(json.loads(LINEA_BASE.read_text(encoding="utf-8"))["claves"])
    nuevos = [h for h in hallazgos if h.clave not in congeladas]
    for h in nuevos:
        print(f"[{h.nivel.upper():<5}] {h.regla:<24} {h.archivo}  {h.detalle}")
    errores = sum(h.nivel == "error" for h in nuevos)
    print(f"\n{len(nuevos)} hallazgos ({errores} errores, {len(nuevos) - errores} avisos); {len(hallazgos) - len(nuevos)} congelados en línea base.")
    return 1 if errores or (a.check and nuevos) else 0


if __name__ == "__main__":
    raise SystemExit(main())
