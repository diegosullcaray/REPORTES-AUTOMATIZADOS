import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Tarjeta enmarcada (patrón de Dokploy): marco `bg-sidebar` y panel interno con sombra.
 * Encabezado con ícono, título, descripción y acciones; el cuerpo va separado por un borde.
 */
export function Marco({ icono, titulo, descripcion, acciones, children, className }: {
  icono?: ReactNode; titulo: ReactNode; descripcion?: ReactNode; acciones?: ReactNode; children: ReactNode; className?: string;
}) {
  return (
    <section className={cn("flex flex-1 flex-col rounded-xl bg-sidebar p-2 sm:p-2.5", className)}>
      <div className="flex flex-1 flex-col rounded-xl border bg-background shadow-sm">
        <header className="flex flex-wrap items-start justify-between gap-4 p-4 sm:p-6">
          <div className="flex min-w-0 flex-col gap-1">
            <h1 className="flex min-w-0 items-center gap-2 text-xl font-semibold tracking-tight">
              {icono && <span className="shrink-0 text-muted-foreground [&>svg]:size-5">{icono}</span>}
              <span className="truncate">{titulo}</span>
            </h1>
            {descripcion && <p className="text-sm text-muted-foreground">{descripcion}</p>}
          </div>
          {acciones && <div className="flex flex-wrap items-center gap-2">{acciones}</div>}
        </header>
        <div className="flex flex-1 flex-col gap-4 border-t p-4 sm:p-6">{children}</div>
      </div>
    </section>
  );
}
