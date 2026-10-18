"""Ejecuciones: valida el pedido con las reglas del reporte, arma los argumentos de `main.py` y consulta/gestiona el historial."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from modulos.notificaciones.aplicacion import destinatarios
from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.notificaciones.dominio import entregas

from modulos.reportes.aplicacion.casos_uso.archivos import carpeta_de
from modulos.reportes.aplicacion.casos_uso.catalogo import ENVIAN_CHAT, lote, validar_corte
from modulos.reportes.aplicacion import dto as dto_reportes
from modulos.reportes.aplicacion.puertos import puertos

# Reportes de Erick que reciben el mes (AAAA-MM) en lugar de la fecha de corte.
USAN_MES = frozenset({"bancarizados-producto", "indicadores-clientes"})


# ---------------------------------------------------------------- argumentos de ejecución

def argumentos(p: dto_reportes.PedidoEjecucion) -> list[str]:
    """Valida el pedido con las reglas del reporte y devuelve los argumentos de `main.py`."""
    nombre = p.reporte
    corte = validar_corte(nombre, p.fecha_corte)
    if p.chat and nombre not in ENVIAN_CHAT:
        raise PeticionInvalida(f"«{nombre}» no envía su archivo por Google Chat.")
    lt = lote(nombre)
    if lt is None:
        if p.forzar or p.confirmar_escritura or p.correo == "todos":
            raise PeticionInvalida(f"«{nombre}» tiene lógica propia: no admite forzar, confirmar escritura ni envío de correo.")
        args = [nombre, "--mes", f"{corte:%Y-%m}"] if nombre in USAN_MES else [nombre, "--fecha-corte", f"{corte:%Y-%m-%d}"]
        if p.fase:
            if nombre != "cmg-mora":
                raise PeticionInvalida(f"«{nombre}» no funciona por fases.")
            args += ["--fase", p.fase]
        if p.chat:
            if not destinatarios.leer(entregas.variable_chat(nombre)):
                raise PeticionInvalida("Indica a quién enviar por Google Chat (pestaña General) o desmarca el envío.")
            args.append("--chat")
        return args
    if lt.escribe_en_bd and not p.confirmar_escritura:
        raise PeticionInvalida(f"«{nombre}» crea/borra tablas permanentes: confirma la escritura en la base de datos.")
    args = [nombre, "--fecha-corte", f"{corte:%Y-%m-%d}"]
    if p.forzar:
        args.append("--forzar")
    if p.confirmar_escritura:
        args.append("--confirmar-escritura")
    if lt.entrega is not None:
        if p.correo == "todos":
            if not p.conforme:
                raise PeticionInvalida("Para enviar a toda la lista debes confirmar que revisaste el correo de prueba.")
            envio = estado_envio(nombre, corte)
            if not envio.prueba:
                raise PeticionInvalida(f"No hay correo de prueba para {corte:%Y-%m-%d}: primero ejecuta el reporte (envía la prueba).")
            if envio.todos:
                raise PeticionInvalida(f"Ya se envió a toda la lista el {envio.todos}.")
            args.append("--conforme")
        args += ["--correo", p.correo]
    elif p.correo == "todos":
        raise PeticionInvalida(f"«{nombre}» no envía correo.")
    return args


# ---------------------------------------------------------------- envío por correo (prueba -> conforme -> todos)

def estado_envio(nombre: str, fecha: date | None) -> dto_reportes.EstadoEnvio:
    lt = lote(nombre)
    if lt is None or lt.entrega is None:
        raise NoEncontrado(f"«{nombre}» no envía correo.")
    corte = validar_corte(nombre, fecha)
    ruta = carpeta_de(nombre) / f"estado_envio_{corte:%Y%m%d}.json"  # mismo archivo que escribe EntregaCorreoResumen
    datos = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    excel = datos.get("excel")
    return dto_reportes.EstadoEnvio(corte=corte, prueba=datos.get("prueba"), todos=datos.get("todos"), excel=Path(excel).name if excel else None)


# ---------------------------------------------------------------- cola e historial (los atiende el puerto de la cola)

def encolar(p: dto_reportes.PedidoEjecucion) -> dto_reportes.Ejecucion:
    return puertos().cola.encolar(p.reporte, argumentos(p))


def historial(reporte: str | None = None, limite: int = 100) -> list[dto_reportes.Ejecucion]:
    return puertos().cola.historial(reporte, limite)


def obtener(id_: str) -> dto_reportes.EjecucionDetalle:
    try:
        return puertos().cola.obtener(id_)
    except KeyError:
        raise NoEncontrado("No existe esa ejecución") from None


def eliminar(ids: list[str]) -> int:
    """Quita del historial las ejecuciones (estado y log); los archivos generados no se tocan."""
    try:
        return puertos().cola.eliminar(ids)
    except KeyError:
        raise NoEncontrado("Alguna ejecución ya no existe: recarga la lista.") from None
    except ValueError as exc:
        raise PeticionInvalida(str(exc)) from exc
