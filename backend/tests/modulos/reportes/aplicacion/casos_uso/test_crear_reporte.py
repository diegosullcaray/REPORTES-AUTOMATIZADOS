"""Crear un reporte desde la web escribe módulo, test y registro en un árbol aislado (nunca en el repo real)."""

import shutil
from pathlib import Path
from types import SimpleNamespace
from datetime import date

import pytest

from core.excepciones import NoEncontrado, PeticionInvalida
from modulos.reportes.aplicacion.casos_uso import crear_reporte
from modulos.reportes.aplicacion.dto import PedidoGrupo, PedidoReporteNuevo
from modulos.reportes.dominio import reglas_fecha, reportes as dominio, tablas as dominio_tablas
from modulos.reportes.dominio.fechas import Cortes

SQL = "use storage;\ngo\nselect * from storage.com_act.hcda001 a join storage.zz.tabla_nueva b on 1=1 where a.hfecpro='@@F@@'"
PEDIDO = dict(nombre="mi-reporte", grupo="piero", orden="99", base="storage", descripcion="Mi reporte", sql=SQL)


@pytest.fixture
def raiz(tmp_path):
    for rel in ("reportes", "tablas", "reglas_fecha"):
        destino = tmp_path / "src/modulos/reportes/dominio" / f"{rel}.py"
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(crear_reporte.BACK / "src/modulos/reportes/dominio" / f"{rel}.py", destino)
    return tmp_path


def test_crea_modulo_test_y_registro(raiz):
    r = crear_reporte.crear(PedidoReporteNuevo(**PEDIDO), raiz=raiz, en_vivo=False)
    assert r.nombre == "mi-reporte" and r.tablas_nuevas == ["storage.zz.tabla_nueva"]
    modulo = raiz / "src/modulos/reportes/catalogo/mensuales/piero/r99_mi_reporte.py"
    assert modulo.exists() and (raiz / "tests/modulos/reportes/catalogo/mensuales/piero/test_r99_mi_reporte.py").exists()
    ns: dict = {}
    exec(compile(modulo.read_text(encoding="utf-8"), "m", "exec"), ns)  # el módulo generado se ejecuta
    assert "@@" not in Cortes.mensual(date(2026, 7, 31)).aplicar(ns["REPORTE"].sql) and ns["REPORTE"].servidor == "mish"
    reg: dict = {}
    exec(compile((raiz / "src/modulos/reportes/dominio/reportes.py").read_text(encoding="utf-8"), "r", "exec"), reg)
    assert reg["REPORTES"]["mi-reporte"].carpeta == "mensuales/piero/99_mi_reporte"
    reglas = (raiz / "src/modulos/reportes/dominio/reglas_fecha.py").read_text(encoding="utf-8")
    ns_reg: dict = {}
    exec(compile(reglas, "g", "exec"), ns_reg)
    assert set(ns_reg["REGLAS"]["mi-reporte"]) == {"storage.com_act.hcda001", "storage.zz.tabla_nueva"}
    assert "HFECPRO = F" in ns_reg["REGLAS"]["mi-reporte"]["storage.com_act.hcda001"]
    tabs = (raiz / "src/modulos/reportes/dominio/tablas.py").read_text(encoding="utf-8")
    assert "'mi-reporte': (" in tabs and "'storage.zz.tabla_nueva', 'referencia', None, 'por_confirmar'" in tabs


@pytest.fixture
def dominio_aislado(monkeypatch):
    """crear_grupo registra el grupo en el proceso: se devuelve el dominio a como estaba."""
    monkeypatch.setattr(dominio, "GRUPOS", list(dominio.GRUPOS))
    for nombre in ("TITULOS_GRUPO", "NOMBRE_GRUPO", "FRECUENCIA_GRUPO"):
        monkeypatch.setattr(dominio, nombre, dict(getattr(dominio, nombre)))


def test_grupo_nuevo_queda_escrito_y_acepta_reportes(raiz, dominio_aislado):
    g = crear_reporte.crear_grupo(PedidoGrupo(nombre="Cierre de Riesgos"), raiz=raiz)
    assert (g.id, g.nombre, g.propio, g.reportes) == ("cierre-de-riesgos", "Cierre de Riesgos", True, 0)
    assert [x.id for x in crear_reporte.listar_grupos()][-1] == "cierre-de-riesgos"
    reg: dict = {}
    exec(compile((raiz / "src/modulos/reportes/dominio/reportes.py").read_text(encoding="utf-8"), "r", "exec"), reg)
    assert "cierre-de-riesgos" in reg["GRUPOS"] and reg["FRECUENCIA_GRUPO"]["cierre-de-riesgos"] == "mensual"

    r = crear_reporte.crear(PedidoReporteNuevo(**{**PEDIDO, "grupo": "cierre-de-riesgos", "orden": "01"}), raiz=raiz, en_vivo=False)
    assert r.ruta == "backend/src/modulos/reportes/catalogo/grupos/cierre_de_riesgos/r01_mi_reporte.py"
    assert (raiz / "src/modulos/reportes/catalogo/grupos/__init__.py").exists() and (raiz / "src/modulos/reportes/catalogo/grupos/cierre_de_riesgos/__init__.py").exists()


@pytest.mark.parametrize("nombre", ["Diarias", "mensuales · piero", " ", "a#b"])
def test_grupo_repetido_o_invalido(raiz, nombre):
    with pytest.raises(PeticionInvalida):
        crear_reporte.crear_grupo(PedidoGrupo(nombre=nombre), raiz=raiz, en_vivo=False)


@pytest.mark.parametrize("cambio,frag", [
    ({"grupo": "no-existe"}, "No existe el grupo"),
    ({"nombre": "saca-tu-garra"}, "Ya existe"),
    ({"orden": "01"}, "Ya hay un reporte"),
    ({"base": "inventada"}, "inventada"),
    ({"descripcion": "  "}, "descripción"),
])
def test_rechaza_sin_escribir_nada(raiz, cambio, frag):
    with pytest.raises(PeticionInvalida, match=frag):
        crear_reporte.crear(PedidoReporteNuevo(**{**PEDIDO, **cambio}), raiz=raiz, en_vivo=False)
    assert not (raiz / "src/modulos/reportes/catalogo").exists()


def test_eliminar_grupo_vacio_lo_quita_del_archivo_y_del_proceso(raiz, dominio_aislado):
    crear_reporte.crear_grupo(PedidoGrupo(nombre="Temporal"), raiz=raiz)
    assert "temporal" in dominio.GRUPOS
    crear_reporte.eliminar_grupo("temporal", raiz=raiz)
    assert "temporal" not in dominio.GRUPOS and "temporal" not in dominio.FRECUENCIA_GRUPO
    assert "'temporal'" not in (raiz / "src/modulos/reportes/dominio/reportes.py").read_text(encoding="utf-8")


def test_eliminar_grupo_con_reportes_no_se_puede(raiz, dominio_aislado):
    crear_reporte.crear_grupo(PedidoGrupo(nombre="Con reportes"), raiz=raiz)
    crear_reporte.crear(PedidoReporteNuevo(**{**PEDIDO, "grupo": "con-reportes", "orden": "01"}), raiz=raiz)  # en vivo: queda registrado
    try:
        with pytest.raises(PeticionInvalida, match="1 reporte"):
            crear_reporte.eliminar_grupo("con-reportes", raiz=raiz)
    finally:
        dominio.REPORTES.pop("mi-reporte", None)
        dominio_tablas.TABLAS.pop("storage.zz.tabla_nueva", None)
        dominio_tablas.USO.pop("mi-reporte", None)
        reglas_fecha.REGLAS.pop("mi-reporte", None)


@pytest.mark.parametrize("id_,error", [("piero", PeticionInvalida), ("no-existe", NoEncontrado)])
def test_no_elimina_los_del_legado_ni_inexistentes(raiz, id_, error):
    with pytest.raises(error):
        crear_reporte.eliminar_grupo(id_, raiz=raiz, en_vivo=False)


def test_la_frecuencia_se_elige_por_reporte_en_los_grupos_propios(raiz, dominio_aislado):
    crear_reporte.crear_grupo(PedidoGrupo(nombre="Mixto"), raiz=raiz)
    r = crear_reporte.crear(PedidoReporteNuevo(**{**PEDIDO, "grupo": "mixto", "orden": "01", "frecuencia": "diaria"}), raiz=raiz, en_vivo=False)
    texto = (raiz / "src/modulos/reportes/dominio/reportes.py").read_text(encoding="utf-8")
    assert "'diarias/mixto/01_mi_reporte'" in texto and r.ruta.endswith("grupos/mixto/r01_mi_reporte.py")
    assert "frecuencia='diaria'" in (raiz / "src/modulos/reportes/catalogo/grupos/mixto/r01_mi_reporte.py").read_text(encoding="utf-8")


def test_la_base_sale_del_use_del_sql(raiz):
    sin_base = {k: v for k, v in PEDIDO.items() if k != "base"}
    crear_reporte.crear(PedidoReporteNuevo(**sin_base), raiz=raiz, en_vivo=False)
    assert "base='storage'" in (raiz / "src/modulos/reportes/catalogo/mensuales/piero/r99_mi_reporte.py").read_text(encoding="utf-8")
    with pytest.raises(PeticionInvalida, match="use <base>"):
        crear_reporte.crear(PedidoReporteNuevo(**{**sin_base, "nombre": "otro", "sql": "select '@@F@@'"}), raiz=raiz, en_vivo=False)


@pytest.fixture
def sin_ejecuciones(monkeypatch):
    """El historial real de data/outputs no interviene: por defecto, ningún reporte tiene ejecuciones."""
    monkeypatch.setattr(crear_reporte, "puertos", lambda: SimpleNamespace(cola=SimpleNamespace(historial=lambda nombre: [])))


def test_eliminar_reporte_deja_el_registro_como_estaba(raiz, dominio_aislado, sin_ejecuciones):
    antes = {f: (raiz / "src/modulos/reportes/dominio" / f).read_bytes() for f in ("reportes.py", "tablas.py", "reglas_fecha.py")}
    crear_reporte.crear(PedidoReporteNuevo(**PEDIDO), raiz=raiz)
    crear_reporte.eliminar("mi-reporte", raiz=raiz)
    assert "mi-reporte" not in dominio.REPORTES and not (raiz / "src/modulos/reportes/catalogo/mensuales/piero/r99_mi_reporte.py").exists()
    assert not (raiz / "tests/modulos/reportes/catalogo/mensuales/piero/test_r99_mi_reporte.py").exists()
    for f, b in antes.items():
        assert (raiz / "src/modulos/reportes/dominio" / f).read_bytes().replace(b"    ('storage.zz.tabla_nueva', 'referencia', None, 'por_confirmar'),\n", b"") == b, f
    dominio_tablas.TABLAS.pop("storage.zz.tabla_nueva", None)


def test_no_se_eliminan_reportes_del_legado(raiz):
    with pytest.raises(PeticionInvalida, match="legado"):
        crear_reporte.eliminar("cartera-sin-asignar", raiz=crear_reporte.BACK)


def test_sin_sql_se_crea_con_plantilla(raiz):
    crear_reporte.crear(PedidoReporteNuevo(**{k: v for k, v in PEDIDO.items() if k not in ("base", "sql")}), raiz=raiz, en_vivo=False)
    assert "pendiente" in (raiz / "src/modulos/reportes/catalogo/mensuales/piero/r99_mi_reporte.py").read_text(encoding="utf-8")


def test_los_grupos_del_legado_no_admiten_otra_frecuencia(raiz):
    with pytest.raises(PeticionInvalida, match="solo admite"):
        crear_reporte.crear(PedidoReporteNuevo(**{**PEDIDO, "frecuencia": "diaria"}), raiz=raiz, en_vivo=False)


def test_grupo_con_etiquetas_y_borrado_las_suelta(raiz, dominio_aislado):
    from modulos.reportes.aplicacion.casos_uso import etiquetas
    from modulos.reportes.aplicacion.dto import PedidoEtiqueta

    e = etiquetas.crear(PedidoEtiqueta(nombre="Riesgos", color="#f59e0b"))
    g = crear_reporte.crear_grupo(PedidoGrupo(nombre="Con etiqueta", etiquetas=[e.id]), raiz=raiz)
    assert [x.nombre for x in g.etiquetas] == ["Riesgos"]
    assert [x.nombre for x in next(x for x in crear_reporte.listar_grupos() if x.id == g.id).etiquetas] == ["Riesgos"]
    crear_reporte.eliminar_grupo(g.id, raiz=raiz)
    from modulos.reportes.aplicacion.puertos import puertos
    assert puertos().etiquetas.leer().grupos == {}
    with pytest.raises(PeticionInvalida, match="desconocidas"):
        crear_reporte.crear_grupo(PedidoGrupo(nombre="Otro", etiquetas=["no-existe"]), raiz=raiz, en_vivo=False)


def test_eliminar_con_ejecucion_en_curso_se_niega(raiz, dominio_aislado, monkeypatch):
    monkeypatch.setattr(crear_reporte, "puertos", lambda: SimpleNamespace(cola=SimpleNamespace(historial=lambda n: [SimpleNamespace(estado="ejecutando")])))
    crear_reporte.crear(PedidoReporteNuevo(**PEDIDO), raiz=raiz)
    try:
        with pytest.raises(PeticionInvalida, match="en curso"):
            crear_reporte.eliminar("mi-reporte", raiz=raiz)
        assert "mi-reporte" in dominio.REPORTES
    finally:
        monkeypatch.setattr(crear_reporte, "puertos", lambda: SimpleNamespace(cola=SimpleNamespace(historial=lambda n: [])))
        crear_reporte.eliminar("mi-reporte", raiz=raiz)
        dominio_tablas.TABLAS.pop("storage.zz.tabla_nueva", None)


def test_si_falla_la_escritura_el_registro_vuelve_a_como_estaba(raiz, monkeypatch):
    registro = {f: (raiz / "src/modulos/reportes/dominio" / f).read_bytes() for f in ("reportes.py", "tablas.py", "reglas_fecha.py")}
    escribir, fallos = Path.write_text, []

    def falla_una_vez(self, *a, **k):
        if self.name == "reglas_fecha.py" and not fallos:
            fallos.append(1)
            raise OSError("disco lleno")
        return escribir(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", falla_una_vez)
    with pytest.raises(OSError):
        crear_reporte.crear(PedidoReporteNuevo(**PEDIDO), raiz=raiz, en_vivo=False)
    assert registro == {f: (raiz / "src/modulos/reportes/dominio" / f).read_bytes() for f in registro}
    assert not (raiz / "src/modulos/reportes/catalogo/mensuales/piero/r99_mi_reporte.py").exists()


def test_al_eliminar_el_ultimo_reporte_de_un_grupo_propio_no_queda_su_carpeta(raiz, dominio_aislado, sin_ejecuciones):
    crear_reporte.crear_grupo(PedidoGrupo(nombre="Temporal"), raiz=raiz)
    crear_reporte.crear(PedidoReporteNuevo(**{**PEDIDO, "grupo": "temporal", "orden": "01"}), raiz=raiz)
    assert (raiz / "src/modulos/reportes/catalogo/grupos/temporal").is_dir()
    crear_reporte.eliminar("mi-reporte", raiz=raiz)
    dominio_tablas.TABLAS.pop("storage.zz.tabla_nueva", None)
    for base in ("src", "tests"):
        grupos = raiz / base / "modulos/reportes/catalogo/grupos"
        assert not (grupos / "temporal").exists() and (grupos / "__init__.py").exists()


def test_eliminar_limpia_el_registro_aunque_el_modulo_ya_no_este(raiz, dominio_aislado, sin_ejecuciones):
    crear_reporte.crear(PedidoReporteNuevo(**PEDIDO), raiz=raiz)
    (raiz / "src/modulos/reportes/catalogo/mensuales/piero/r99_mi_reporte.py").unlink()
    crear_reporte.eliminar("mi-reporte", raiz=raiz)
    dominio_tablas.TABLAS.pop("storage.zz.tabla_nueva", None)
    assert "mi-reporte" not in dominio.REPORTES and "mi-reporte" not in (raiz / "src/modulos/reportes/dominio/reportes.py").read_text(encoding="utf-8")
