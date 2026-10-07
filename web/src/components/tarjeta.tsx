import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/** Tarjeta interna de una pestaña (como las Card de Dokploy: «Deploy Settings», «Deployments»…). */
export function Tarjeta({ titulo, descripcion, acciones, children, className }: {
  titulo: ReactNode; descripcion?: ReactNode; acciones?: ReactNode; children?: ReactNode; className?: string;
}) {
  return (
    <section className={cn("rounded-xl border bg-background", className)}>
      <header className="flex flex-wrap items-start justify-between gap-3 p-5 pb-0">
        <div className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold tracking-tight">{titulo}</h2>
          {descripcion && <p className="text-sm text-muted-foreground">{descripcion}</p>}
        </div>
        {acciones && <div className="flex flex-wrap items-center gap-2">{acciones}</div>}
      </header>
      {children && <div className="flex flex-col gap-4 p-5">{children}</div>}
    </section>
  );
}
