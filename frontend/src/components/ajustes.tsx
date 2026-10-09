"use client";

import { Copy } from "lucide-react";
import type { ReactNode } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

/** Bloque de una pantalla de ajustes: título, descripción y filas separadas (como las secciones de Settings en Dokploy). */
export function SeccionAjustes({ titulo, descripcion, accion, children }: { titulo: string; descripcion?: string; accion?: ReactNode; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h2 className="text-base font-semibold">{titulo}</h2>
          {descripcion && <p className="text-sm text-muted-foreground">{descripcion}</p>}
        </div>
        {accion}
      </div>
      <div className="divide-y rounded-lg border px-4">{children}</div>
    </section>
  );
}

/** Fila etiqueta → valor, con ayuda y botón de copiar opcionales. `children` reemplaza al valor de texto. */
export function FilaAjuste({ etiqueta, valor, ayuda, copiable, children }: { etiqueta: string; valor?: string; ayuda?: string; copiable?: boolean; children?: ReactNode }) {
  return (
    <div className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:gap-6">
      <span className="w-56 shrink-0 text-sm text-muted-foreground">{etiqueta}</span>
      <div className="flex min-w-0 flex-1 items-center gap-2">
        {children ?? (
          <div className="flex min-w-0 flex-col">
            <span className="truncate font-mono text-sm" title={valor}>{valor}</span>
            {ayuda && <span className="text-xs text-muted-foreground">{ayuda}</span>}
          </div>
        )}
        {copiable && valor && (
          <Button variant="ghost" size="icon-sm" aria-label={`Copiar ${etiqueta}`} className="ml-auto"
            onClick={() => { navigator.clipboard.writeText(valor); toast.success("Copiado"); }}><Copy /></Button>
        )}
      </div>
    </div>
  );
}
