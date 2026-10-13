"use client";

import { CircleCheck, CircleX, LoaderCircle, ScrollText, X } from "lucide-react";
import type { Tono } from "@/lib/formato";
import { Hace } from "@/components/hace";
import { Button } from "@/components/ui/button";
import { ESTADO_EJECUCION } from "@/lib/formato";
import type { EstadoPaso, EstadoProceso, Paso } from "./proceso";

export const ESTADO_PROCESO: Record<EstadoProceso, { texto: string; tono: Tono }> = {
  completo: { texto: "Completo", tono: "exito" },
  incompleto: { texto: "Incompleto", tono: "aviso" },
  fallo: { texto: "Con fallas", tono: "peligro" },
  en_curso: { texto: "En curso", tono: "info" },
};

const PASO: Record<EstadoPaso, { icono: typeof X; color: string; texto: string }> = {
  hecho: { icono: CircleCheck, color: "var(--mis-success)", texto: "Hecho" },
  fallo: { icono: CircleX, color: "var(--mis-danger)", texto: "Falló" },
  falta: { icono: X, color: "var(--mis-text-secondary)", texto: "Falta" },
  en_curso: { icono: LoaderCircle, color: "var(--mis-primary-text)", texto: "En curso" },
};

/** Pasos en una línea (para la tabla): ✓ hecho · X falta · ✗ falló. */
export function PasosEnLinea({ pasos }: { pasos: Paso[] }) {
  return (
    <span className="flex flex-wrap items-center gap-x-3 gap-y-1">
      {pasos.map((p) => {
        const { icono: Icono, color, texto } = PASO[p.estado];
        return (
          <span key={p.id} className="inline-flex items-center gap-1 text-xs" title={`${p.nombre}: ${texto}`} style={{ color: p.estado === "falta" ? color : undefined }}>
            <Icono className={`size-3.5 shrink-0 ${p.estado === "en_curso" ? "animate-spin" : ""}`} style={{ color }} />
            <span className={p.estado === "fallo" ? "font-medium" : ""} style={{ color: p.estado === "fallo" ? color : undefined }}>{p.nombre}</span>
          </span>
        );
      })}
    </span>
  );
}

/** El proceso paso a paso: el que falló se resalta y cada paso abre el log de su último intento. */
export function LineaProceso({ pasos, onVerLog }: { pasos: Paso[]; onVerLog: (id: string) => void }) {
  return (
    <ol className="flex flex-col gap-2">
      {pasos.map((p, i) => {
        const { icono: Icono, color, texto } = PASO[p.estado];
        const x = p.ejecucion;
        const fallo = p.estado === "fallo";
        return (
          <li key={p.id} className="flex flex-wrap items-center gap-3 rounded-lg border px-3 py-2"
            style={fallo ? { background: "var(--mis-danger-light)", borderColor: "color-mix(in srgb, var(--mis-danger) 40%, transparent)" } : undefined}>
            <Icono className={`size-5 shrink-0 ${p.estado === "en_curso" ? "animate-spin" : ""}`} style={{ color }} aria-label={texto} />
            <div className="flex min-w-0 flex-1 flex-col">
              <span className="text-sm font-medium" style={{ color: fallo ? color : undefined }}>{i + 1}. {p.nombre}</span>
              <span className="text-xs text-muted-foreground">
                {x ? <>{fallo ? `Falló: ${ESTADO_EJECUCION[x.estado].texto.toLowerCase()}` : texto} · <Hace iso={x.inicio} />{p.intentos > 1 && ` · ${p.intentos} intentos`}</> : "Falta: aún no se hizo"}
              </span>
            </div>
            {x && <Button variant={fallo ? "outline" : "ghost"} size="sm" onClick={() => onVerLog(x.id)}><ScrollText /> Ver log</Button>}
          </li>
        );
      })}
    </ol>
  );
}
