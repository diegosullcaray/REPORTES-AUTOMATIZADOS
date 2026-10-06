"""Catálogo de reportes automatizados: nombre -> (módulo, frecuencia, servidor(es))."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Reporte:
    nombre: str
    modulo: str
    frecuencia: str
    servidores: tuple[str, ...]
    descripcion: str


REPORTES: dict[str, Reporte] = {r.nombre: r for r in (
    Reporte("cmg-mora", "reportes.diarios.cmg_mora", "diaria", ("rcc",),
            "Recaudo + provisiones diarios -> INSERTs SBTVRIE001 (se detiene si provisiones = 0)"),
    Reporte("bancarizados", "reportes.mensuales.bancarizados", "mensual", ("rcc", "slc"),
            "Clientes exclusivos de Financiera Confianza (RCC) por producto y territorio"),
    Reporte("bancarizados-producto", "reportes.mensuales.bancarizados_producto", "mensual", ("slc",),
            "Bancarizados por producto (clientes nuevos con desembolso)"),
    Reporte("clientes-extranjeros", "reportes.mensuales.clientes_extranjeros", "mensual", ("slc", "rcc"),
            "Clientes por nacionalidad: créditos, pasivos y seguros"),
    Reporte("indicadores-clientes", "reportes.mensuales.indicadores_clientes", "mensual", ("slc",),
            "Indicadores de clientes para el Directorio"),
    Reporte('cartera-sin-asignar', 'reportes.diarios.cartera_sin_asignar', 'diaria', ('mish',),
            'Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación'),
    Reporte('cmg-castigos', 'reportes.diarios.cmg_castigos', 'diaria', ('mish',),
            'CMG Mora · recuperación de castigos 12M (SRECCAST12M): suma de SDAS005 en los últimos 11 cierres'),
    Reporte('clientes-jovenes', 'reportes.mensuales.clientes_jovenes', 'mensual', ("slc",),
            'Clientes jóvenes (Manuel Siccha): nuevos y stock de 18 a 30 años'),
    Reporte('desembolsos-por-canal', 'reportes.mensuales.desembolsos_por_canal', 'mensual', ('mish',),
            'Desembolsos por canal: contratación electrónica (CT) vs agencia física (BT)'),
    Reporte('fondeo-estable', 'reportes.mensuales.fondeo_estable', 'mensual', ('mish',),
            'Estadística de tramo / Fondeo estable (Eddy Martínez)'),
    Reporte('heredados-pdm', 'reportes.mensuales.heredados_pdm', 'mensual', ("slc",),
            'Heredados PDM: validar Cubo y tablas PDM completos al corte antes de ejecutar'),
    Reporte('productos-verdes', 'reportes.mensuales.productos_verdes', 'mensual', ("slc",),
            'Productos verdes (Manuel Siccha): crédito verde, ticket promedio y tasas'),
    Reporte('contratacion-electronica', 'reportes.mensuales.contratacion_electronica', 'mensual', ('mish',),
            'Contratación electrónica: desembolsos habilitados y desembolsados (n.º de operaciones y monto)'),
    Reporte('clientes-rurales-migrantes', 'reportes.mensuales.clientes_rurales_migrantes', 'mensual', ('mish',),
            'Clientes rurales y migrantes (Manuel Siccha): últimos 3 cierres'),
    Reporte('michael-captaciones', 'reportes.mensuales.michael_captaciones', 'mensual', ('mish',),
            'Reporte mensual de Michael Palacios · Captaciones (siempre debe traer datos)'),
    Reporte('michael-castigos', 'reportes.mensuales.michael_castigos', 'mensual', ('mish',),
            'Reporte mensual de Michael Palacios · Castigos (puede salir vacío: hay meses sin castigos)'),
    Reporte('giovanni-captaciones', 'reportes.mensuales.giovanni_captaciones', 'mensual', ('mish',),
            'Reportes Giovanni 1 · Saldo medio y saldo puntual de captaciones'),
    Reporte('giovanni-seguros', 'reportes.mensuales.giovanni_seguros', 'mensual', ('mish',),
            'Reportes Giovanni 2 · Seguros multirriesgo (versión remasterizada). Valores en 0 se etiquetan «sin asignar»'),
    Reporte('giovanni-cartera-agro', 'reportes.mensuales.giovanni_cartera_agro', 'mensual', ('mish',),
            'Reportes Giovanni 3 · Cartera vigente Agro (cierre actual y cierre del mes anterior)'),
    Reporte('saca-tu-garra', 'reportes.mensuales.saca_tu_garra', 'mensual', ('mish',),
            'Saca tu garra (Giancarlos): entregar 8:00–8:30 AM'),
    Reporte('saldo-medio-vigente', 'reportes.mensuales.saldo_medio_vigente', 'mensual', ('mish',),
            'Saldo medio vigente (Diana García): saldo medio del mes y saldos diarios'),
    Reporte('tapp-saldo-medio-territorio', 'reportes.mensuales.tapp_saldo_medio_territorio', 'mensual', ('mish',),
            'TAPP: stock TPP del mes, saldo medio vigente por territorio (Edy)'),
)}


def frecuencia_de(reporte: str) -> str:
    """'diaria' | 'mensual'."""
    try:
        return REPORTES[reporte].frecuencia
    except KeyError:
        raise KeyError(f"Reporte desconocido: {reporte}. Usa: python main.py listar") from None
