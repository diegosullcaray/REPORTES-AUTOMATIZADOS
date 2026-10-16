"""Verificación de tablas al corte y solicitud a Producción (por reporte y masiva por responsable).

No reimplementa reglas: llama a las mismas funciones que usa la consola, así la web y `main.py` no pueden divergir.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

from aplicacion import dto as e
from aplicacion.errores import NoEncontrado
from aplicacion.puertos import puertos
from aplicacion.verificacion import verificar_reporte, verificar_tabla
from dominio.reportes import ordenados
from dominio.tablas import tablas_de
from dominio.verificacion import Estado, Resultado, mensaje_solicitud, mensaje_solicitud_grupo, nombre_resuelto

from .catalogo import validar_corte


# ---------------------------------------------------------------- verificación y solicitud a Producción

def verificar(nombre: str, fecha: date | None) -> e.Verificacion:
    corte = validar_corte(nombre, fecha)
    resultados = verificar_reporte(nombre, corte)
    pendientes = [x for x in resultados if x.estado in {Estado.DESACTUALIZADA, Estado.NO_EXISTE}]
    return e.Verificacion(
        corte=corte,
        listo=not pendientes and not any(x.estado is Estado.ERROR for x in resultados),
        resultados=[
            e.ResultadoTabla(nombre=nombre_resuelto(x.tabla, corte), servidor=x.tabla.servidor, estado=x.estado.value,
                             ultima_fecha=x.ultima_fecha, detalle=x.detalle)
            for x in resultados
        ],
        solicitud=mensaje_solicitud(nombre, corte, resultados) if pendientes else None,
    )


GRUPOS_VALIDACION = {"piero": "Heredados de Piero", "erick": "Heredados de Erick"}
_PENDIENTE = {Estado.DESACTUALIZADA, Estado.NO_EXISTE}


def _verificar_grupo(grupo: str, fecha: date | None):
    """Verifica cada tabla distinta una sola vez aunque la usen varios reportes. Devuelve corte, reportes y {tabla: [Tabla, Resultado, reportes]}."""
    if grupo not in GRUPOS_VALIDACION:
        raise NoEncontrado(f"Grupo desconocido: {grupo}")
    reportes = [r for r in ordenados() if r.grupo == grupo and r.frecuencia == "mensual" and tablas_de(r.nombre)]
    if not reportes:
        raise NoEncontrado(f"El grupo «{grupo}» no tiene reportes mensuales con tablas registradas.")
    corte = validar_corte(reportes[0].nombre, fecha)
    unicas: dict[str, list] = {}
    for r in reportes:
        for t in tablas_de(r.nombre):
            clave = nombre_resuelto(t, corte)
            if clave not in unicas:
                unicas[clave] = [t, None, []]
            unicas[clave][2].append(r.nombre)

    def por_servidor(claves: list[str]) -> None:
        """Un servidor, en orden. Si no responde, sus demás tablas se marcan con la misma causa sin reintentar (cada intento tarda)."""
        caido: Resultado | None = None
        for clave in claves:
            t = unicas[clave][0]
            if caido and t.verificable:
                unicas[clave][1] = Resultado(t, Estado.ERROR, detalle=caido.detalle, sin_conexion=True)
            else:
                unicas[clave][1] = verificar_tabla(t, corte)
                if unicas[clave][1].sin_conexion:
                    caido = unicas[clave][1]

    grupos: dict[str, list[str]] = {}
    for clave, (t, _, _) in unicas.items():
        grupos.setdefault(t.servidor, []).append(clave)
    with ThreadPoolExecutor(max_workers=len(grupos)) as pool:  # los servidores se consultan a la vez
        list(pool.map(por_servidor, grupos.values()))
    return corte, reportes, unicas


def _solucion(causa: str) -> str:
    if "driver ODBC" in causa:
        return "Instala «ODBC Driver 17 for SQL Server» o define DB_ODBC_DRIVER en backend/.env con un driver instalado."
    if "requiere" in causa and "_USER" in causa:
        return "Define el usuario y la contraseña de esa conexión en backend/.env (por ejemplo RCC_USER y RCC_PASSWORD)."
    if "No se pudo conectar" in causa:
        return "Comprueba la red o la VPN y que el nombre del servidor en backend/.env sea correcto; luego vuelve a verificar."
    if "rechazó el inicio de sesión" in causa:
        return "Revisa el usuario y la contraseña de esa conexión en backend/.env."
    return "Revisa el detalle de la tabla y vuelve a verificar."


def verificar_grupo(grupo: str, fecha: date | None) -> e.VerificacionGrupo:
    corte, reportes, unicas = _verificar_grupo(grupo, fecha)
    resumen = []
    for r in reportes:
        propias = [x[1] for x in unicas.values() if r.nombre in x[2]]
        pendientes = sum(x.estado in _PENDIENTE for x in propias)
        dudosas = sum(x.estado is Estado.ERROR for x in propias)
        resumen.append(e.ResumenValidacion(nombre=r.nombre, orden=r.orden, tablas=len(propias), pendientes=pendientes, dudosas=dudosas, listo=not (pendientes or dudosas)))
    por_pedir = [tuple(x) for x in unicas.values() if x[1].estado in _PENDIENTE]
    causas: dict[str, int] = {}
    for _, res, _ in unicas.values():
        if res.estado is Estado.ERROR:
            causas[res.detalle] = causas.get(res.detalle, 0) + 1
    return e.VerificacionGrupo(
        problemas=[e.ProblemaValidacion(causa=c, tablas=n, solucion=_solucion(c)) for c, n in sorted(causas.items(), key=lambda x: -x[1])],
        grupo=grupo, titulo=GRUPOS_VALIDACION[grupo], corte=corte, listo=all(x.listo for x in resumen), reportes=resumen,
        tablas=[
            e.TablaValidada(nombre=nombre, servidor=t.servidor, estado=res.estado.value, ultima_fecha=res.ultima_fecha, detalle=res.detalle, reportes=usan)
            for nombre, (t, res, usan) in unicas.items()
        ],
        solicitud=mensaje_solicitud_grupo(GRUPOS_VALIDACION[grupo], corte, por_pedir) if por_pedir else None,
    )


def guardar_solicitud_grupo(grupo: str, fecha: date | None) -> e.Solicitud:
    """Vuelve a verificar (no se confía en el navegador) y guarda el mensaje único en data/outputs/solicitudes."""
    corte, _, unicas = _verificar_grupo(grupo, fecha)
    texto = mensaje_solicitud_grupo(GRUPOS_VALIDACION[grupo], corte, [tuple(x) for x in unicas.values() if x[1].estado in _PENDIENTE])
    destino = puertos().entorno.dir_outputs() / "solicitudes"
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / f"solicitud_mensual_{grupo}_{corte:%Y%m%d}.txt"
    ruta.write_text(texto + "\n", encoding="utf-8")
    return e.Solicitud(archivo=ruta.name, texto=texto)


def guardar_solicitud(nombre: str, fecha: date | None) -> e.Solicitud:
    """Verifica de nuevo (no se confía en lo que mande el navegador) y guarda el mensaje en data/outputs/solicitudes."""
    corte = validar_corte(nombre, fecha)
    texto = mensaje_solicitud(nombre, corte, verificar_reporte(nombre, corte))
    destino = puertos().entorno.dir_outputs() / "solicitudes"
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / f"solicitud_{nombre}_{corte:%Y%m%d}.txt"
    ruta.write_text(texto + "\n", encoding="utf-8")
    return e.Solicitud(archivo=ruta.name, texto=texto)
