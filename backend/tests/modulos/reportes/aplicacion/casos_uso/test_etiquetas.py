"""Etiquetas de los grupos: se crean, editan y borran por la API; borrar una la suelta de los grupos que la llevaban."""

import pytest
from tests.cliente_web import TestClient

from modulos.reportes.aplicacion.casos_uso import etiquetas
from modulos.reportes.aplicacion.dto import PedidoEtiqueta
from modulos.sistema.aplicacion.casos_uso import sesion

cliente = TestClient()
cliente.cookies.set(sesion.COOKIE, sesion.emitir("tester"))


def test_crear_listar_actualizar_y_eliminar():
    r = cliente.post("/api/etiquetas", json={"nombre": " Riesgos  2026 ", "color": "#EF4444"})
    assert r.status_code == 201
    e = r.json()
    assert e["nombre"] == "Riesgos 2026" and e["color"] == "#ef4444"
    assert cliente.get("/api/etiquetas").json() == [e]
    r = cliente.put(f"/api/etiquetas/{e['id']}", json={"nombre": "Riesgos", "color": "#3b82f6"})
    assert r.json()["color"] == "#3b82f6" and cliente.get("/api/etiquetas").json()[0]["nombre"] == "Riesgos"
    assert cliente.delete(f"/api/etiquetas/{e['id']}").status_code == 200
    assert cliente.get("/api/etiquetas").json() == [] and cliente.delete(f"/api/etiquetas/{e['id']}").status_code == 404


@pytest.mark.parametrize("cuerpo,frag", [
    ({"nombre": "  "}, "nombre"), ({"nombre": "-malo"}, "nombre"), ({"nombre": "x" * 60}, "nombre"), ({"nombre": "ok", "color": "rojo"}, "color"), ({"nombre": "ok", "color": "#fff"}, "color"), ({"nombre": "ok", "color": "#gggggg"}, "color"),
])
def test_validaciones(cuerpo, frag):
    r = cliente.post("/api/etiquetas", json=cuerpo)
    assert r.status_code == 422 and frag in r.text.lower()


def test_nombre_repetido_sin_importar_mayusculas_pero_editable_a_si_misma():
    e = etiquetas.crear(PedidoEtiqueta(nombre="Cierre"))
    assert cliente.post("/api/etiquetas", json={"nombre": "CIERRE"}).status_code == 422
    assert cliente.put(f"/api/etiquetas/{e.id}", json={"nombre": "CIERRE", "color": "#22c55e"}).status_code == 200


def test_asignar_a_grupo_y_borrar_la_etiqueta_la_suelta():
    a, b = etiquetas.crear(PedidoEtiqueta(nombre="A")), etiquetas.crear(PedidoEtiqueta(nombre="B"))
    r = cliente.put("/api/grupos/piero/etiquetas", json={"etiquetas": [a.id, b.id, a.id]})
    assert r.status_code == 200 and [x["nombre"] for x in r.json()["etiquetas"]] == ["A", "B"]
    etiquetas.eliminar(a.id)
    piero = next(g for g in cliente.get("/api/grupos").json() if g["id"] == "piero")
    assert [x["nombre"] for x in piero["etiquetas"]] == ["B"]


def test_asignar_rechaza_grupo_o_etiqueta_inexistente():
    assert cliente.put("/api/grupos/nada/etiquetas", json={"etiquetas": []}).status_code == 404
    r = cliente.put("/api/grupos/piero/etiquetas", json={"etiquetas": ["x"]})
    assert r.status_code == 422 and "desconocidas" in r.text
