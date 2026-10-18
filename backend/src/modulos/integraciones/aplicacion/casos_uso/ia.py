"""Conexiones con proveedores de IA por API key (como «AI» en Settings de Dokploy), guardadas en el .env.

  IA_CONFIGS              ids separados por coma
  IA_<ID>_NOMBRE / _URL / _CLAVE / _MODELO / _ACTIVO

La API key es de solo escritura: nunca vuelve al navegador.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from core.excepciones import ErrorIntegracion, NoEncontrado, PeticionInvalida
from core.puertos import nucleo
from modulos.integraciones.aplicacion import dto as dto_integraciones
from modulos.integraciones.aplicacion.puertos import puertos

_SUFIJOS = ("NOMBRE", "URL", "CLAVE", "MODELO", "ACTIVO")


def _env(variable: str) -> str:
    return nucleo().entorno.leer(variable).strip()


def _ids() -> list[str]:
    return [i for i in _env("IA_CONFIGS").split(",") if i]


def _var(id_: str, sufijo: str) -> str:
    return f"IA_{id_.upper().replace('-', '_')}_{sufijo}"


def _config(id_: str) -> dto_integraciones.ConfigIA:
    url = _env(_var(id_, "URL"))
    return dto_integraciones.ConfigIA(
        id=id_, nombre=_env(_var(id_, "NOMBRE")), api_url=url, modelo=_env(_var(id_, "MODELO")), activo=_env(_var(id_, "ACTIVO")) != "0",
        proveedor=puertos().ia.proveedor_de(url), clave_configurada=bool(_env(_var(id_, "CLAVE"))),
    )


def listar() -> list[dto_integraciones.ConfigIA]:
    return [_config(i) for i in _ids()]


def _existente(id_: str) -> str:
    if id_ not in _ids():
        raise NoEncontrado(f"No existe la conexión «{id_}».")
    return id_


def _texto(campo: str, valor: str, *, espacios: bool = False) -> str:
    valor = valor.strip()
    if not valor:
        raise PeticionInvalida(f"{campo}: no puede quedar vacío.")
    if any(c in valor for c in "\r\n#\"'") or (not espacios and " " in valor):
        raise PeticionInvalida(f"{campo}: no admite {'saltos de línea, # ni comillas' if espacios else 'espacios, saltos de línea, # ni comillas'}.")
    return valor


def _url(valor: str) -> str:
    valor = _texto("API URL", valor).rstrip("/")
    partes = urlparse(valor)
    if partes.scheme not in {"http", "https"} or not partes.netloc:
        raise PeticionInvalida("La API URL debe empezar con http:// o https://.")
    return valor


def _clave(valor: str) -> str:
    valor = valor.strip()
    if any(c in valor for c in "\r\n#\"' "):
        raise PeticionInvalida("La API key no admite espacios, saltos de línea, # ni comillas.")
    return valor


def crear(p: dto_integraciones.PedidoIA) -> dto_integraciones.ConfigIA:
    nombre = _texto("Nombre", p.nombre, espacios=True)
    base = re.sub(r"[^a-z0-9]+", "-", nombre.lower()).strip("-")[:30] or "ia"
    id_, n = base, 2
    while id_ in _ids():
        id_, n = f"{base}-{n}", n + 1
    cambios = {_var(id_, "NOMBRE"): nombre, _var(id_, "URL"): _url(p.api_url), _var(id_, "CLAVE"): _clave(p.api_key),
               _var(id_, "MODELO"): _texto("Modelo", p.modelo), _var(id_, "ACTIVO"): "1" if p.activo else "0",
               "IA_CONFIGS": ",".join([*_ids(), id_])}
    nucleo().entorno.guardar(cambios)
    return _config(id_)


def actualizar(id_: str, p: dto_integraciones.PedidoIAActualizar) -> dto_integraciones.ConfigIA:
    _existente(id_)
    cambios: dict[str, str] = {}
    if p.nombre is not None:
        cambios[_var(id_, "NOMBRE")] = _texto("Nombre", p.nombre, espacios=True)
    if p.api_url is not None:
        cambios[_var(id_, "URL")] = _url(p.api_url)
    if p.api_key:  # vacía o ausente = conservar
        cambios[_var(id_, "CLAVE")] = _clave(p.api_key)
    if p.modelo is not None:
        cambios[_var(id_, "MODELO")] = _texto("Modelo", p.modelo)
    if p.activo is not None:
        cambios[_var(id_, "ACTIVO")] = "1" if p.activo else "0"
    if not cambios:
        raise PeticionInvalida("No hay ningún ajuste que guardar.")
    nucleo().entorno.guardar(cambios)
    return _config(id_)


def eliminar(id_: str) -> None:
    _existente(id_)
    cambios = {_var(id_, s): "" for s in _SUFIJOS}
    cambios["IA_CONFIGS"] = ",".join(i for i in _ids() if i != id_)
    nucleo().entorno.guardar(cambios)


def modelos(p: dto_integraciones.PedidoModelos) -> dto_integraciones.ModelosIA:
    """Modelos del proveedor. Sin clave escrita usa la guardada de `id`, pero solo si la URL es la guardada (la clave no se envía a otro destino)."""
    url, clave = _url(p.api_url), _clave(p.api_key)
    if not clave and p.id:
        _existente(p.id)
        if _env(_var(p.id, "URL")).rstrip("/") != url:
            raise PeticionInvalida("Cambiaste la API URL: escribe de nuevo la API key.")
        clave = _env(_var(p.id, "CLAVE"))
    try:
        return dto_integraciones.ModelosIA(proveedor=puertos().ia.proveedor_de(url), modelos=puertos().ia.modelos(url, clave))
    except ErrorIntegracion as exc:
        raise PeticionInvalida(str(exc)) from exc


def probar(id_: str) -> dto_integraciones.ModelosIA:
    """Conecta con la clave guardada y lista los modelos: comprueba URL y clave."""
    c = _config(_existente(id_))
    return modelos(dto_integraciones.PedidoModelos(api_url=c.api_url, id=id_))
