import type { DicBase, DicHallazgo } from "../../lib/tipos";

/** Errores y avisos por regla, de la regla con más hallazgos a la que menos (lo informativo no pide acción y no cuenta). */
export function porRegla(hallazgos: DicHallazgo[]): [string, { error: number; aviso: number }][] {
  const m = new Map<string, { error: number; aviso: number }>();
  for (const h of hallazgos) {
    if (h.nivel !== "error" && h.nivel !== "aviso") continue;
    const r = m.get(h.regla) ?? { error: 0, aviso: 0 };
    r[h.nivel]++;
    m.set(h.regla, r);
  }
  return [...m].sort((a, b) => b[1].error + b[1].aviso - (a[1].error + a[1].aviso) || a[0].localeCompare(b[0]));
}

/** Avance de cada base en % de sus procedimientos (así una base chica se ve igual que una grande), con los conteos reales para el tooltip y las etiquetas. */
export function avancePorBase(bases: DicBase[]) {
  return bases
    .filter((b) => b.procedimientos > 0)
    .sort((a, b) => b.procedimientos - a.procedimientos || a.base.localeCompare(b.base))
    .map((b) => {
      const validados = b.validados, extraidos = b.extraidos - b.validados, pendientes = b.procedimientos - b.extraidos;
      const pct = (n: number) => (n / b.procedimientos) * 100;
      return { base: b.base, total: b.procedimientos, validados, extraidos, pendientes, pctValidados: pct(validados), pctExtraidos: pct(extraidos), pctPendientes: pct(pendientes) };
    });
}
