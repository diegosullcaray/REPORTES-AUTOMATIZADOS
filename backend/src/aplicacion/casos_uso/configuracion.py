"""Configuración editable desde la web (cortes, carpetas, driver), cuenta de acceso, servidores de bases de datos y perfil.

Todo se guarda en el .env; las claves nunca vuelven al navegador. Los cortes rigen desde la próxima ejecución.
"""

from __future__ import annotations

import getpass
import platform
import time
from datetime import date
from pathlib import Path

from aplicacion import dto as e
from aplicacion.cortes import resolver_corte
from aplicacion.errores import NoEncontrado, PeticionInvalida
from aplicacion.puertos import puertos
from dominio import entregas
from dominio.errores import ConfiguracionError, ErrorIntegracion
from dominio.fechas import Cortes, fecha_iso
from dominio.servidores import BASES_DE

from . import sesion


def perfil() -> e.Perfil:
    entorno = puertos().entorno
    try:
        destinatarios: int | None = len(puertos().correo.leer_destinatarios())
    except (OSError, ConfiguracionError, ErrorIntegracion):
        destinatarios = None
    return e.Perfil(
        usuario=getpass.getuser(), equipo=platform.node(),
        correo_prueba=entorno.leer("CORREO_PRUEBA", entregas.CORREO_PRUEBA_DEFECTO).strip(),
        cuenta_envio=entorno.leer("SMTP_USER").strip() or None,
        clave_envio_configurada=bool(entorno.leer("SMTP_PASSWORD").strip()),
        webhook_configurado=bool(entorno.leer("GOOGLE_CHAT_WEBHOOK_URL").strip()),
        destinatarios=destinatarios,
    )


def _corte(frecuencia: str) -> e.Corte:
    try:
        fecha, origen = resolver_corte(frecuencia, None)
        return e.Corte(fecha=fecha, origen=origen)
    except ConfiguracionError as exc:
        return e.Corte(fecha=None, origen=str(exc))


# campo del pedido -> variable del .env. Los cortes se leen en cada ejecución; carpetas y driver se fijan al arrancar la API.
VARIABLES = {
    "corte_mensual": "FECHA_CORTE_MENSUAL", "corte_diario": "FECHA_CORTE_DIARIA",
    "dir_inputs": "REPORTES_DIR_INPUTS", "dir_outputs": "REPORTES_DIR_OUTPUTS", "driver_odbc": "DB_ODBC_DRIVER",
}
AL_REINICIAR = {
    "dir_inputs": ("carpeta de entradas", lambda v: Path(v) != puertos().entorno.dir_inputs()),
    "dir_outputs": ("carpeta de salidas", lambda v: Path(v) != puertos().entorno.dir_outputs()),
    "driver_odbc": ("driver ODBC", lambda v: v != puertos().entorno.driver_odbc()),
}


def _pendientes_reinicio() -> list[str]:
    guardado = puertos().entorno.guardado()
    return [nombre for campo, (nombre, difiere) in AL_REINICIAR.items() if guardado.get(VARIABLES[campo]) and difiere(guardado[VARIABLES[campo]])]


def configuracion() -> e.ConfiguracionGeneral:
    return e.ConfiguracionGeneral(corte_mensual=_corte("mensual"), corte_diario=_corte("diaria"),
                                  dir_inputs=str(puertos().entorno.dir_inputs()), dir_outputs=str(puertos().entorno.dir_outputs()),
                                  driver_odbc=puertos().entorno.driver_odbc(),
                                  pendientes_reinicio=_pendientes_reinicio())


def _validar_ajuste(campo: str, valor: str) -> str:
    if not valor:
        return ""
    if any(c in valor for c in "\r\n#\"'"):
        raise PeticionInvalida(f"{VARIABLES[campo]}: no admite saltos de línea, # ni comillas.")
    if campo.startswith("corte_"):
        try:
            corte = fecha_iso(valor)
            if campo == "corte_mensual":
                Cortes.mensual(corte)
        except (ValueError, ConfiguracionError) as exc:
            raise PeticionInvalida(f"{VARIABLES[campo]}: {exc}") from exc
        if corte > date.today():
            raise PeticionInvalida(f"{VARIABLES[campo]}: la fecha {valor} está en el futuro.")
    elif campo.startswith("dir_") and not Path(valor).is_absolute():
        raise PeticionInvalida(f"{VARIABLES[campo]}: escribe una ruta completa (con letra de unidad).")
    return valor


def actualizar_cuenta(actual: str, p: e.PedidoCuenta) -> str:
    """Cambia WEB_USUARIO y/o WEB_CLAVE en el .env (rige ya, sin reiniciar). Devuelve el usuario resultante."""
    try:
        if not sesion.iniciar(actual, p.clave_actual):  # misma verificación y límite de intentos que el inicio de sesión
            raise PeticionInvalida("La contraseña actual no es correcta.")
    except PermissionError as exc:
        raise PeticionInvalida(str(exc)) from exc
    usuario, clave = (p.usuario or "").strip(), p.clave_nueva or ""
    if not usuario and not clave:
        raise PeticionInvalida("No hay ningún cambio que guardar.")
    cambios: dict[str, str] = {}
    if usuario:
        if any(c in usuario for c in "\r\n#\"' \t"):
            raise PeticionInvalida("El usuario no admite espacios, saltos de línea, # ni comillas.")
        cambios["WEB_USUARIO"] = usuario
    if clave:
        if len(clave) < 8:
            raise PeticionInvalida("La contraseña nueva debe tener al menos 8 caracteres.")
        if any(c in clave for c in "\r\n#\"'"):
            raise PeticionInvalida("La contraseña no admite saltos de línea, # ni comillas (el .env no las soporta).")
        cambios["WEB_CLAVE"] = clave
    puertos().entorno.guardar(cambios)
    return usuario or actual


def guardar_configuracion(p: e.PedidoConfiguracion) -> e.ConfiguracionGeneral:
    """Valida y escribe en el .env solo lo enviado. Los cortes rigen desde la próxima ejecución; carpetas y driver al reiniciar la API."""
    cambios = {VARIABLES[c]: _validar_ajuste(c, (getattr(p, c) or "").strip()) for c in p.model_fields_set}
    if not cambios:
        raise PeticionInvalida("No hay ningún ajuste que guardar.")
    # Los cortes rigen ya (las ejecuciones heredan el entorno del proceso); carpetas y driver, al reiniciar la API.
    puertos().entorno.guardar(cambios, al_proceso=[VARIABLES[c] for c in ("corte_mensual", "corte_diario") if c in p.model_fields_set])
    return configuracion()


def servidores() -> list[e.Servidor]:
    return [
        e.Servidor(nombre=s.nombre, servidor=s.servidor, autenticacion=s.autenticacion, credenciales_en_env=s.credenciales_en_env,
                   descripcion=s.descripcion, bases=list(BASES_DE[s.nombre]))
        for s in puertos().entorno.servidores()
    ]


def probar_servidor(nombre: str) -> e.PruebaConexion:
    """SELECT 1 contra un servidor (mismo camino que usan los reportes: db.leer_sql)."""
    if nombre not in BASES_DE:
        raise NoEncontrado(f"Servidor desconocido: {nombre}")
    inicio = time.perf_counter()
    try:
        puertos().bd.leer_sql(nombre, "SELECT 1 AS ok")
        ok, detalle = True, "Conexión correcta"
    except Exception as exc:  # noqa: BLE001 - diagnóstico para la pantalla, igual que probar_conexiones
        ok, detalle = False, f"{type(exc).__name__}: {str(exc)[:200]}"
    return e.PruebaConexion(nombre=nombre, ok=ok, detalle=detalle, milisegundos=round((time.perf_counter() - inicio) * 1000))
