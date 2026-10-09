"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { errorDeCorte } from "@/lib/formato";
import type { ReporteDetalle } from "@/lib/tipos";

/** Fecha de corte compartida por todos los pasos; muestra de dónde sale la de por defecto. */
export function CampoCorte({ reporte, valor, onCambio }: { reporte: ReporteDetalle; valor: string; onCambio: (v: string) => void }) {
  const error = errorDeCorte(reporte.frecuencia, valor);
  const ayuda = !valor ? reporte.corte.origen : valor === reporte.corte.fecha ? `Origen: ${reporte.corte.origen}` : "Fecha elegida a mano";
  return (
    <div className="flex flex-col gap-1">
      <Label htmlFor="corte">Fecha de corte {reporte.frecuencia === "mensual" && "(fin de mes)"}</Label>
      <Input id="corte" type="date" value={valor} onChange={(e) => onCambio(e.target.value)} aria-invalid={!!error} aria-describedby="corte-ayuda" className="w-48" />
      <span id="corte-ayuda" className={`text-[12px] ${error ? "text-[var(--mis-danger)]" : "text-[var(--mis-text-tertiary)]"}`}>{error ?? ayuda}</span>
    </div>
  );
}
