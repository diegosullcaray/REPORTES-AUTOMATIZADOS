"""Procesos del repo DICCIONARIO (regenerar, verificar, probar) y la validación de las bases: lista cerrada, uno a la vez, con su detalle, historial y log."""

from __future__ import annotations

import inspect
import threading
import time
from collections.abc import Callable

from core.excepciones import NoEncontrado
from core.puertos import nucleo
from core.servidores import BASES_DE
from modulos.diccionario.aplicacion import dto
from modulos.diccionario.aplicacion.puertos import puertos
from modulos.diccionario.dominio.columnas import PROCESOS, Proceso
from modulos.reportes.dominio.verificacion import causa_de

ESPERA_BASE = 8     # segundos de inicio de sesión por servidor
LIMITE = 15         # segundos que se espera a todos juntos: un servidor que no contesta no deja la pantalla esperando
CONSULTA_SERVIDOR = "SELECT @@SERVERNAME AS servidor, SUSER_SNAME() AS usuario, CAST(SERVERPROPERTY('ProductVersion') AS varchar(30)) AS version"
CONSULTA_BASES = "SELECT name, state_desc FROM sys.databases"


def _definicion(p: Proceso) -> dto.ProcesoDef:
    return dto.ProcesoDef(id=p.id, nombre=p.nombre, descripcion=p.descripcion, comando=" ".join(p.comando), escribe=p.escribe, genera=bool(p.generados))


def _proceso(id_: str) -> Proceso:
    if id_ not in PROCESOS:  # el comando sale solo de PROCESOS, nunca de la petición
        raise NoEncontrado(f"No existe el proceso «{id_}».")
    return PROCESOS[id_]


def catalogo() -> list[dto.ProcesoDef]:
    return [_definicion(p) for p in PROCESOS.values()]


def _script_bases() -> list[dto.ScriptArchivo]:
    """Lo que de verdad corre «bases»: las dos consultas, las bases que espera por servidor y el código que las ejecuta."""
    esperadas = "\n".join(f"--   {servidor}: {', '.join(bases)}" for servidor, bases in BASES_DE.items())
    sql = (f"-- 1. Quién es el servidor y con qué usuario entra la API\n{CONSULTA_SERVIDOR};\n\n-- 2. Estado de cada base de datos del servidor\n{CONSULTA_BASES};\n\n"
           f"-- Se comparan con las bases que usan los reportes (core/servidores.py › BASES_DE):\n{esperadas}")
    return [dto.ScriptArchivo(ruta="SQL · lo que se consulta en cada servidor", codigo=sql),
            dto.ScriptArchivo(ruta="procesos.py · _probar_servidor", codigo=inspect.getsource(_probar_servidor)),
            dto.ScriptArchivo(ruta="procesos.py · _validar_bases", codigo=inspect.getsource(_validar_bases)),
            dto.ScriptArchivo(ruta="core/bd.py · leer_sql", codigo=inspect.getsource(nucleo().bd.leer_sql))]


def detalle(id_: str) -> dto.ProcesoDetalle:
    """Lo que hace el proceso (su código) y lo que deja (los archivos que se pueden ver)."""
    p = _proceso(id_)
    scripts = puertos().lector.script_npm(p.npm) if p.npm else _script_bases()
    return dto.ProcesoDetalle(**_definicion(p).model_dump(), scripts=scripts, archivos=puertos().lector.archivos(p.generados) if p.generados else [])


def archivo(id_: str, ruta: str) -> dto.VistaArchivo:
    return puertos().lector.texto(ruta, _proceso(id_).generados)


def _probar_servidor(s) -> tuple[bool, list[str]]:
    """Un servidor: conecta, dice quién es y con qué usuario entra, y comprueba que cada base que usan los reportes esté en línea."""
    t = time.perf_counter()
    try:
        yo = nucleo().bd.leer_sql(s.nombre, CONSULTA_SERVIDOR, timeout=ESPERA_BASE).iloc[0]
        estado = {str(n).lower(): str(e) for n, e in nucleo().bd.leer_sql(s.nombre, CONSULTA_BASES, timeout=ESPERA_BASE).itertuples(index=False)}
    except Exception as exc:  # noqa: BLE001 - diagnóstico por servidor: uno caído no impide probar los demás
        return False, [f"✗ {s.nombre} ({s.servidor}): {causa_de(exc, s.nombre)[0]}"]
    lineas, bien = [f"✓ {s.nombre} ({s.servidor}): conexión correcta · {round((time.perf_counter() - t) * 1000)} ms · SQL Server {yo['version']} · usuario {yo['usuario']}"], True
    for base in BASES_DE[s.nombre]:
        e = estado.get(base.lower())
        if e == "ONLINE":
            lineas.append(f"    ✓ {base}")
        elif e is None:   # sin permiso para verla, o es un servidor vinculado: no se da por caída
            lineas.append(f"    AVISO {base}: no aparece en el servidor (o no hay permiso para verla)")
        else:
            bien = False
            lineas.append(f"    ✗ {base}: {e}")
    return bien, lineas


def _validar_bases(emitir: Callable[[str], None]) -> int:
    """Prueba los servidores a la vez y va escribiendo cada resultado apenas llega. Código 0 si todo está bien."""
    servidores = nucleo().entorno.servidores()
    emitir(f"▶ Probando {', '.join(s.nombre for s in servidores)} a la vez (hasta {LIMITE} s)…\n")
    resultados: dict[str, bool] = {}

    def probar(s) -> None:
        try:
            bien, lineas = _probar_servidor(s)
        except Exception as exc:  # noqa: BLE001 - un fallo raro en un servidor se ve como lo que es, no como «sin respuesta»
            bien, lineas = False, [f"✗ {s.nombre} ({s.servidor}): error inesperado ({type(exc).__name__}): {exc}"]
        resultados[s.nombre] = bien
        emitir("\n".join(lineas) + "\n")

    hilos = [threading.Thread(target=probar, args=(s,), daemon=True) for s in servidores]
    limite = time.monotonic() + LIMITE
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(max(0.0, limite - time.monotonic()))
    for s in servidores:
        if s.nombre not in resultados:
            emitir(f"✗ {s.nombre} ({s.servidor}): sin respuesta en {LIMITE} s (¿VPN o red caída?)\n")
    return 0 if len(resultados) == len(servidores) and all(resultados.values()) else 1


def ejecutar(id_: str) -> dto.Ejecucion:
    p = _proceso(id_)
    lanzador = puertos().lanzador
    if id_ == "bases":
        return lanzador.ejecutar_tarea(id_, _validar_bases)
    # «uno a la vez» lo garantiza el lanzador (comprueba y anota bajo un mismo candado)
    return lanzador.ejecutar(id_, p.comando, puertos().lector.carpeta())


def historial(proceso: str | None = None) -> list[dto.Ejecucion]:
    return [x for x in puertos().lanzador.historial(50) if proceso in (None, x.proceso)]


def obtener(id_: str) -> dto.EjecucionDetalle:
    try:
        return puertos().lanzador.obtener(id_)
    except KeyError:
        raise NoEncontrado("No existe esa ejecución.") from None
