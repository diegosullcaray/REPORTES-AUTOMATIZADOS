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
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
LINEA_BASE = RAIZ / "governance" / "gobernanza.linea-base.json"
FUENTES = [p for p in (RAIZ / "src").rglob("*.py") if "__pycache__" not in p.parts] + [RAIZ / "main.py"]


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
    return p.relative_to(RAIZ).as_posix()


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
        if p.name == "db.py":
            continue
        txt = p.read_text(encoding="utf-8")
        for rx, msg in ((r"pyodbc\.connect\(", "pyodbc.connect fuera de db.py"), (r"\bcreate_engine\(", "create_engine fuera de db.py")):
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
    from reportes.config import SERVIDORES
    from reportes.registro import REPORTES

    for r in REPORTES.values():
        ruta = RAIZ / "src" / (r.modulo.replace(".", "/") + ".py")
        if not ruta.exists():
            yield Hallazgo("registro-sincronizado", "error", "src/reportes/registro.py", f"{r.nombre}: módulo {r.modulo} no existe")
            continue
        if not re.search(r"^def main\(", ruta.read_text(encoding="utf-8"), re.M):
            yield Hallazgo("registro-sincronizado", "error", rel(ruta), "el módulo no define main(argv)")
        for b in r.servidores:
            if b not in SERVIDORES:
                yield Hallazgo("registro-sincronizado", "error", "src/reportes/registro.py", f"{r.nombre}: servidor '{b}' no está en config.SERVIDORES")
    registrados = {r.modulo for r in REPORTES.values()}
    for carpeta in ("diarios", "mensuales"):
        for p in sorted((RAIZ / "src" / "reportes" / carpeta).rglob("*.py")):
            mod = ".".join(p.relative_to(RAIZ / "src").with_suffix("").parts)
            if p.stem != "__init__" and mod not in registrados:
                yield Hallazgo("registro-sincronizado", "aviso", rel(p), "módulo sin registrar en registro.py")
    for r in REPORTES.values():
        esperado = "r" + r.orden.replace(".", "_")
        if not r.modulo.rsplit(".", 1)[1].startswith(esperado + "_"):
            yield Hallazgo("registro-sincronizado", "error", "src/reportes/registro.py", f"{r.nombre}: el módulo debe empezar por {esperado}_ (número del legado {r.orden})")
        if not r.carpeta.split("/")[-1].startswith(r.orden.split(".")[0] + "_"):
            yield Hallazgo("registro-sincronizado", "error", "src/reportes/registro.py", f"{r.nombre}: la carpeta de salida debe empezar por {r.orden.split('.')[0]}_")


def r_nombres():
    ok = re.compile(r"^[a-z0-9_]+(\.[a-z]+)?$")
    for p in (RAIZ / "src").rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        for parte in p.relative_to(RAIZ).parts:
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
    tests = {p.name for p in (RAIZ / "tests").rglob("test_*.py")} if (RAIZ / "tests").exists() else set()
    for p in FUENTES:
        if p.stem in {"__init__", "main"}:
            continue
        if f"test_{p.stem}.py" not in tests:
            yield Hallazgo("prueba-vecina", "aviso", rel(p), "sin tests/test_<modulo>.py")


def r_env():
    from reportes.config import SERVIDORES

    ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
    for b in SERVIDORES.values():
        for suf in ("SERVER", "USER", "PASSWORD"):
            if f"{b.prefijo}_{suf}" not in ejemplo:
                yield Hallazgo("env-example-completo", "error", ".env.example", f"falta {b.prefijo}_{suf}")


def r_gitignore():
    g = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
    for req in (".env", "data/*", "*.pkl"):
        if req not in g:
            yield Hallazgo("gitignore-protege-datos", "error", ".gitignore", f"falta '{req}'")


def r_tablas():
    import extraer_tablas as ex
    from reportes.registro import REPORTES
    from reportes.tablas import TABLAS, USO

    for comando, usadas in ex.por_reporte().items():
        for n in sorted(usadas - set(TABLAS)):
            yield Hallazgo("tabla-sin-registrar", "error", "src/reportes/tablas.py", f"{n}: la usa «{comando}» pero no está registrada")
        for n in sorted(usadas - set(USO.get(comando, ()))):
            yield Hallazgo("tabla-sin-registrar", "error", "src/reportes/tablas.py", f"USO[{comando}] no declara {n}, que el módulo consulta")
    for reporte, nombres in USO.items():
        if reporte not in REPORTES:
            yield Hallazgo("tabla-sin-registrar", "error", "src/reportes/tablas.py", f"USO[{reporte}]: reporte inexistente en registro.py")
        for n in nombres:
            if n not in TABLAS:
                yield Hallazgo("tabla-sin-registrar", "error", "src/reportes/tablas.py", f"USO[{reporte}] cita '{n}' inexistente en TABLAS")
    for r in REPORTES:
        if r not in USO:
            yield Hallazgo("tabla-sin-registrar", "error", "src/reportes/tablas.py", f"reporte '{r}' sin tablas en USO")
    for t in TABLAS.values():
        if t.tipo in {"historica", "stock"} and not t.col_fecha:
            yield Hallazgo("tabla-sin-fecha", "aviso", "src/reportes/tablas.py", f"{t.nombre}: sin columna de fecha, no se puede verificar")
        if t.confianza == "convencion":
            yield Hallazgo("tabla-fecha-por-validar", "aviso", "src/reportes/tablas.py", f"{t.nombre}: columna {t.col_fecha} inferida por prefijo; validar con el DBA")


def r_servidor_coherente():
    """Un T-SQL solo puede nombrar bases de SU servidor: las tablas de cada reporte deben vivir en el servidor que declara."""
    from importlib import import_module

    from reportes.config import ConfiguracionError, servidor_de_base
    from reportes.registro import REPORTES
    from reportes.tablas import TABLAS, USO

    for r in REPORTES.values():
        try:
            usados = {TABLAS[n].servidor for n in USO.get(r.nombre, ()) if TABLAS[n].tipo != "destino"}
        except ConfiguracionError as exc:
            yield Hallazgo("servidor-coherente", "error", "src/reportes/config.py", f"{r.nombre}: {exc}")
            continue
        fuera = usados - set(r.servidores)
        if fuera:
            yield Hallazgo("servidor-coherente", "error", "src/reportes/registro.py",
                           f"{r.nombre}: usa tablas de {sorted(fuera)} pero declara {list(r.servidores)}")
        lote = getattr(import_module(r.modulo), "REPORTE", None)
        if lote is not None:
            if lote.servidor not in r.servidores:
                yield Hallazgo("servidor-coherente", "error", "src/reportes/registro.py", f"{r.nombre}: ReporteLote.servidor '{lote.servidor}' no está en registro")
            if lote.base and servidor_de_base(lote.base) != lote.servidor:
                yield Hallazgo("servidor-coherente", "error", r.modulo.replace(".", "/") + ".py",
                               f"base '{lote.base}' vive en {servidor_de_base(lote.base)}, no en {lote.servidor}")


REGLAS = {
    "secretos-en-codigo": (r_secretos, "Ninguna credencial literal en src/. Solo .env."),
    "conexion-solo-en-db": (r_conexion, "pyodbc/SQLAlchemy se abren únicamente en reportes/db.py."),
    "rutas-absolutas": (r_rutas, "Sin rutas D:\\... fijas; usar config.DIR_OUTPUTS."),
    "registro-sincronizado": (r_registro, "Todo reporte registrado existe, expone main() y usa servidores válidos (mish/slc/rcc)."),
    "nombres-canonicos": (r_nombres, "Módulos en snake_case, sin espacios ni tildes."),
    "prueba-vecina": (r_prueba, "Cada módulo tiene tests/test_<modulo>.py."),
    "env-example-completo": (r_env, ".env.example declara las variables de las 3 conexiones."),
    "gitignore-protege-datos": (r_gitignore, ".gitignore excluye .env, data/ (inputs y outputs) y cachés."),
    "tabla-sin-registrar": (r_tablas, "Toda tabla que consulta el código está en reportes/tablas.py y todo reporte declara sus tablas."),
    "servidor-coherente": (r_servidor_coherente, "Las tablas y la base de cada reporte viven en el servidor que declara (config.BASES_DE)."),
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
