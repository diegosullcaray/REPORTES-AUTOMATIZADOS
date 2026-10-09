"""Catálogo de reportes ejecutables: comando -> módulo, responsable, número del legado, servidor(es) y carpeta de salida.

Orden y numeración = las carpetas de `docs/LEGADO` (cada reporte conserva el número con el que se heredó):
  - diarias : «01 TAREAS DIARIAS» (02 Cartera sin asignar, 04 CMG Mora)
  - piero   : «02 TAREAS MENSUALES / 01 - HEREDADO DE PIERO» (01 … 09)
  - erick   : «02 TAREAS MENSUALES / 02 - HEREDADO DE ERICK» (01 Productos verdes, 02 Clientes jóvenes, 03 Clientes exclusivos…)
Un número con punto (04.1, 04.2) son los sub-reportes de una misma carpeta del legado.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Reporte:
    nombre: str
    modulo: str
    frecuencia: str
    servidores: tuple[str, ...]
    descripcion: str
    grupo: str          # diarias | piero | erick
    orden: str          # número de la carpeta del legado ("02", "04.1"…)
    carpeta: str        # subcarpeta de salida bajo data/outputs (p. ej. mensuales/piero/01_desembolsos_por_canal)

    @property
    def clave_orden(self) -> tuple:
        return (GRUPOS.index(self.grupo), tuple(int(x) for x in self.orden.split(".")))

    @property
    def etiqueta(self) -> str:
        return f"{self.grupo.capitalize()} {self.orden}"


# Reportes diarios cuya fecha por defecto es siempre ayer (Date - 1 del legado), sin la regla lunes -> sábado de CMG Mora
DIA_ANTERIOR_SIMPLE = frozenset({"cartera-sin-asignar"})

GRUPOS = ("diarias", "piero", "erick")
TITULOS_GRUPO = {"diarias": "Diarias (01 TAREAS DIARIAS)", "piero": "Mensuales · heredados de Piero", "erick": "Mensuales · heredados de Erick"}

# (comando, grupo, orden, paquete, módulo, carpeta de salida, servidores, descripción)
_DEFINICION = [
    ('cartera-sin-asignar', 'diarias', '02', 'reportes.diarios.r02_cartera_sin_asignar', 'diarias/02_cartera_sin_asignar', ('mish',),
     'Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación'),
    ('cmg-mora', 'diarias', '04.1', 'reportes.diarios.r04_1_cmg_mora', 'diarias/04_cmg_mora', ('rcc',),
     'Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0)'),
    ('desembolsos-por-canal', 'piero', '01', 'reportes.mensuales.piero.r01_desembolsos_por_canal', 'mensuales/piero/01_desembolsos_por_canal', ('mish',),
     'Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT)'),
    ('fondeo-estable', 'piero', '02', 'reportes.mensuales.piero.r02_fondeo_estable', 'mensuales/piero/02_estadistica_de_tramo_fondeo_estable', ('mish',),
     'Estadística de tramo / Fondeo estable (Eddy Martínez)'),
    ('heredados-pdm', 'piero', '03', 'reportes.mensuales.piero.r03_heredados_pdm', 'mensuales/piero/03_heredados_pdm', ('slc',),
     'Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar'),
    ('contratacion-electronica', 'piero', '04.1', 'reportes.mensuales.piero.r04_1_contratacion_electronica', 'mensuales/piero/04_ratio_ce_clientes_nuevos_y_migrantes', ('mish',),
     'Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto)'),
    ('clientes-rurales-migrantes', 'piero', '04.2', 'reportes.mensuales.piero.r04_2_clientes_rurales_migrantes', 'mensuales/piero/04_ratio_ce_clientes_nuevos_y_migrantes', ('mish',),
     'Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres'),
    ('giovanni-captaciones', 'piero', '05.1', 'reportes.mensuales.piero.r05_1_giovanni_captaciones', 'mensuales/piero/05_reportes_para_giovanni', ('mish',),
     'Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones'),
    ('giovanni-seguros', 'piero', '05.2', 'reportes.mensuales.piero.r05_2_giovanni_seguros', 'mensuales/piero/05_reportes_para_giovanni', ('mish',),
     'Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar»'),
    ('giovanni-cartera-agro', 'piero', '05.3', 'reportes.mensuales.piero.r05_3_giovanni_cartera_agro', 'mensuales/piero/05_reportes_para_giovanni', ('mish',),
     'Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior)'),
    ('saca-tu-garra', 'piero', '06', 'reportes.mensuales.piero.r06_saca_tu_garra', 'mensuales/piero/06_saca_tu_garra', ('mish',),
     'Saca tu garra (Giancarlos): entregar 8:00–8:30 AM'),
    ('saldo-medio-vigente', 'piero', '07', 'reportes.mensuales.piero.r07_saldo_medio_vigente', 'mensuales/piero/07_saldo_medio_vigente', ('mish',),
     'Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios'),
    ('tapp-saldo-medio-territorio', 'piero', '08', 'reportes.mensuales.piero.r08_tapp_saldo_medio_territorio', 'mensuales/piero/08_tapp_stock_tpp_mes_saldo_medio_vigente_territorio', ('mish',),
     'TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy)'),
    ('michael-captaciones', 'piero', '09.1', 'reportes.mensuales.piero.r09_1_michael_captaciones', 'mensuales/piero/09_reporte_mensual_michael_palacios', ('mish',),
     'Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos)'),
    ('michael-castigos', 'piero', '09.2', 'reportes.mensuales.piero.r09_2_michael_castigos', 'mensuales/piero/09_reporte_mensual_michael_palacios', ('mish',),
     'Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos)'),
    ('productos-verdes', 'erick', '01', 'reportes.mensuales.erick.r01_productos_verdes', 'mensuales/erick/01_productos_verdes', ('slc',),
     'Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas'),
    ('clientes-jovenes', 'erick', '02', 'reportes.mensuales.erick.r02_clientes_jovenes', 'mensuales/erick/02_clientes_jovenes', ('slc',),
     'Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años'),
    ('bancarizados', 'erick', '03.1', 'reportes.mensuales.erick.r03_1_bancarizados', 'mensuales/erick/03_clientes_exclusivos_desempeno_social', ('rcc', 'slc'),
     'Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio'),
    ('bancarizados-producto', 'erick', '03.2', 'reportes.mensuales.erick.r03_2_bancarizados_producto', 'mensuales/erick/03_clientes_exclusivos_desempeno_social', ('slc',),
     'Bancarizados por producto (clientes nuevos con desembolso)'),
    ('clientes-extranjeros', 'erick', '03.3', 'reportes.mensuales.erick.r03_3_clientes_extranjeros', 'mensuales/erick/03_clientes_exclusivos_desempeno_social', ('slc', 'rcc'),
     'Clientes por nacionalidad: créditos, pasivos y seguros'),
    ('indicadores-clientes', 'erick', '03.4', 'reportes.mensuales.erick.r03_4_indicadores_clientes', 'mensuales/erick/03_clientes_exclusivos_desempeno_social', ('slc',),
     'Indicadores de clientes para el Directorio'),
]

REPORTES: dict[str, Reporte] = {}
for _cmd, _grupo, _orden, _modulo, _carpeta, _srv, _desc in _DEFINICION:
    REPORTES[_cmd] = Reporte(_cmd, _modulo, "diaria" if _grupo == "diarias" else "mensual", _srv, _desc, _grupo, _orden, _carpeta)


def ordenados() -> list[Reporte]:
    """Reportes en el orden del legado: diarias, Piero 01…09, Erick 01…03."""
    return sorted(REPORTES.values(), key=lambda r: r.clave_orden)


def carpeta_salida(comando: str) -> Path:
    """Carpeta de salida por defecto de un reporte: data/outputs/<mensuales/piero|mensuales/erick|diarias>/<NN_nombre>."""
    from .config import DIR_OUTPUTS

    return DIR_OUTPUTS / REPORTES[comando].carpeta


def frecuencia_de(reporte: str) -> str:
    """'diaria' | 'mensual'."""
    try:
        return REPORTES[reporte].frecuencia
    except KeyError:
        raise KeyError(f"Reporte desconocido: {reporte}. Usa: python main.py listar") from None
