"""Utilidades HTTP de la interfaz web (interfaces/web/http.py): JSON de los DTO y validación con el formato de errores del frontend."""

from datetime import date

import pytest
from django.test import RequestFactory

from aplicacion import dto as e
from interfaces.web import http as h

RF = RequestFactory()


def test_json_serializa_modelos_listas_y_fechas_sin_escapar_tildes():
    r = h.json(e.Corte(fecha=date(2026, 9, 30), origen="por defecto · día anterior"))
    assert r.status_code == 200 and "día anterior" in r.content.decode("utf-8") and "2026-09-30" in r.content.decode("utf-8")
    assert h.json([e.Sesion(usuario="ana")]).content == b'[{"usuario": "ana"}]' and h.json({"a": 1}, 202).status_code == 202


def test_cuerpo_valido_conserva_los_campos_enviados():
    p = h.cuerpo(RF.put("/x", data='{"corte_mensual": "2026-09-30"}', content_type="application/json"), e.PedidoConfiguracion)
    assert p.corte_mensual == "2026-09-30" and p.model_fields_set == {"corte_mensual"}


def test_cuerpo_invalido_es_422_con_la_lista_de_errores_que_lee_el_frontend():
    with pytest.raises(h.ErrorHttp) as exc:
        h.cuerpo(RF.post("/x", data='{"usuario": ""}', content_type="application/json"), e.PedidoSesion)
    assert exc.value.status == 422
    assert all(d["loc"][0] == "body" and {"loc", "msg", "type"} <= set(d) for d in exc.value.detalle)
    with pytest.raises(h.ErrorHttp):
        h.cuerpo(RF.post("/x", data="no es json", content_type="application/json"), e.PedidoSesion)


def test_entero_con_rango():
    assert h.entero(RF.get("/x"), "limite", 20, 1, 200) == 20 and h.entero(RF.get("/x?limite=5"), "limite", 20, 1, 200) == 5
    for malo, tipo in (("0", "greater_than_equal"), ("999", "less_than_equal"), ("a", "int_parsing")):
        with pytest.raises(h.ErrorHttp) as exc:
            h.entero(RF.get(f"/x?limite={malo}"), "limite", 20, 1, 200)
        assert exc.value.status == 422 and exc.value.detalle[0]["type"] == tipo and exc.value.detalle[0]["loc"] == ["query", "limite"]


def test_fecha_y_booleano_de_la_consulta():
    assert h.fecha(RF.get("/x?fecha_corte=2026-09-30"), "fecha_corte") == date(2026, 9, 30) and h.fecha(RF.get("/x"), "fecha_corte") is None
    with pytest.raises(h.ErrorHttp):
        h.fecha(RF.get("/x?fecha_corte=30/09/2026"), "fecha_corte")
    assert h.booleano(RF.get("/x?en_linea=true"), "en_linea") and not h.booleano(RF.get("/x"), "en_linea") and not h.booleano(RF.get("/x?en_linea=no"), "en_linea")
