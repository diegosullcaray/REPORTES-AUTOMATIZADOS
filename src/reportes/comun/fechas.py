"""Fechas de corte y tokens que se sustituyen en el T-SQL de cada reporte."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from ..config import ConfiguracionError


def fecha_iso(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Fecha inválida '{valor}', usa AAAA-MM-DD") from exc


def fin_de_mes(anio: int, mes: int) -> date:
    return date(anio, mes, calendar.monthrange(anio, mes)[1])


def meses_atras(f: date, n: int) -> date:
    """Último día del mes que está `n` meses antes del mes de `f`."""
    total = f.year * 12 + (f.month - 1) - n
    return fin_de_mes(total // 12, total % 12 + 1)


def dia_anterior_habil_simple(hoy: date | None = None) -> date:
    """Día anterior; lunes -> sábado (regla de los reportes diarios)."""
    hoy = hoy or date.today()
    return hoy - timedelta(days=2 if hoy.weekday() == 0 else 1)


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
