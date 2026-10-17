"""Fechas de corte y tokens que se sustituyen en el T-SQL de cada reporte (reglas puras: no leen el .env)."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta

from core.excepciones import ConfiguracionError
from core.fechas import VAR_CORTE, corte_desde_texto, fecha_iso  # noqa: F401 - se reexportan: los reportes los importan de aquí


def fin_de_mes(anio: int, mes: int) -> date:
    return date(anio, mes, calendar.monthrange(anio, mes)[1])


def meses_atras(f: date, n: int) -> date:
    """Último día del mes que está `n` meses antes del mes de `f`."""
    total = f.year * 12 + (f.month - 1) - n
    return fin_de_mes(total // 12, total % 12 + 1)


MESES_LARGO = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_CORTO = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def nombre_de_archivo(patron: str, corte: date) -> str:
    """Sustituye en `patron` los tokens de fecha de los archivos del legado.

    {AAAA-MM-DD} 2026-06-30 · {AAAAMMDD} 20260630 · {AAAAMM} 202606 · {AAAA} 2026 · {AA} 26 · {MES} Junio · {mes3} jun · {MES3} JUN
    Ej.: "Desembolsos_canal_{AAAAMMDD}" -> Desembolsos_canal_20260630 · "Clientes_jóvenes_{mes3}{AA}" -> Clientes_jóvenes_jun26
    """
    tokens = {
        "{AAAA-MM-DD}": f"{corte:%Y-%m-%d}", "{AAAAMMDD}": f"{corte:%Y%m%d}", "{AAAAMM}": f"{corte:%Y%m}", "{AAAA}": f"{corte:%Y}", "{AA}": f"{corte:%y}",
        "{MES}": MESES_LARGO[corte.month - 1], "{mes3}": MESES_CORTO[corte.month - 1], "{MES3}": MESES_CORTO[corte.month - 1].upper(),
    }
    for t, v in tokens.items():
        patron = patron.replace(t, v)
    return patron


def resolver_corte(frecuencia: str, cli: date | None = None, hoy: date | None = None, lunes_sabado: bool = True, en_env: date | None = None) -> tuple[date, str]:
    """Fecha de corte y de dónde salió. Prioridad: --fecha-corte > .env (`en_env`) > (solo diaria) día anterior; mensual sin fecha = error."""
    if cli:
        return cli, "--fecha-corte"
    if en_env:
        return en_env, f".env ({VAR_CORTE[frecuencia]})"
    if frecuencia == "diaria":
        return dia_anterior_habil_simple(hoy, lunes_sabado), "por defecto: día anterior" + (" (lunes = sábado)" if lunes_sabado else "")
    raise ConfiguracionError(
        "Falta la fecha de corte mensual: escribe FECHA_CORTE_MENSUAL=AAAA-MM-DD (fin de mes) en el .env o usa --fecha-corte AAAA-MM-DD"
    )


def dia_anterior_habil_simple(hoy: date | None = None, lunes_sabado: bool = True) -> date:
    """Día anterior. Con `lunes_sabado` (regla de CMG Mora) el lunes toma el sábado; sin ella, siempre ayer (Date - 1 del legado)."""
    hoy = hoy or date.today()
    return hoy - timedelta(days=2 if lunes_sabado and hoy.weekday() == 0 else 1)


@dataclass(frozen=True)
class Cortes:
    """Todas las fechas derivadas de un corte. Los tokens `@@X@@` del SQL se reemplazan por estos valores."""

    corte: date

    @classmethod
    def mensual(cls, corte: date) -> "Cortes":
        if corte.day != calendar.monthrange(corte.year, corte.month)[1]:
            raise ConfiguracionError(
                f"La fecha de corte debe ser fin de mes (si cae feriado, el día hábil anterior se pasa explícitamente); recibí {corte}"
            )
        return cls(corte)

    @property
    def mes_anterior(self) -> date:
        return meses_atras(self.corte, 1)

    @property
    def inicio_mes(self) -> date:
        return self.corte.replace(day=1)

    @property
    def hace_3_meses(self) -> date:
        return meses_atras(self.corte, 3)

    def tokens(self) -> dict[str, str]:
        c = self
        return {
            "@@F@@": f"{c.corte:%Y%m%d}",
            "@@F_ISO@@": f"{c.corte:%Y-%m-%d}",
            "@@F_ANT@@": f"{c.mes_anterior:%Y%m%d}",
            "@@F_ANT_ISO@@": f"{c.mes_anterior:%Y-%m-%d}",
            "@@F_INI@@": f"{c.inicio_mes:%Y%m%d}",
            "@@F_MENOS3@@": f"{c.hace_3_meses:%Y%m%d}",
        }

    def aplicar(self, sql: str) -> str:
        for token, valor in self.tokens().items():
            sql = sql.replace(token, valor)
        if "@@" in sql:
            raise ConfiguracionError("El SQL tiene tokens de fecha sin resolver (@@…@@)")
        return sql
