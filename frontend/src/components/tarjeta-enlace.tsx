import type { LucideIcon } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { Card, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export const REJILLA_TARJETAS = "grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3";

/** Tarjeta clicable al estilo de Dokploy (proyecto / servicio): título, descripción y pie con datos. */
export function Tarjeta({ href, icono: Icono, titulo: t, descripcion, estado, pie, acciones, etiquetas }: { href: string; icono: LucideIcon; titulo: string; descripcion?: string; estado?: ReactNode; pie: ReactNode; acciones?: ReactNode; etiquetas?: ReactNode }) {
  return (
    <div className="relative h-full">
    <Link href={href} className="block h-full" prefetch={false}>
      <Card className="group relative h-full bg-transparent transition-colors hover:bg-border">
        {estado && <div className="absolute top-3 right-3">{estado}</div>}
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Icono className="size-4 shrink-0 text-muted-foreground" /><span className="truncate">{t}</span></CardTitle>
          {etiquetas && <div className="flex flex-wrap gap-1.5">{etiquetas}</div>}
          {descripcion && <span className="line-clamp-2 text-sm text-muted-foreground" title={descripcion}>{descripcion}</span>}
        </CardHeader>
        <CardFooter className="mt-auto flex items-center justify-between gap-2 border-t-0 bg-transparent text-xs text-muted-foreground">{pie}</CardFooter>
      </Card>
    </Link>
    {/* fuera del enlace: un botón dentro de un <a> navegaría al pulsarlo (Dokploy detiene la propagación; aquí ni siquiera comparten árbol) */}
    {acciones && <div className="absolute top-2.5 right-2.5">{acciones}</div>}
    </div>
  );
}
