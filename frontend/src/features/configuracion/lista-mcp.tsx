"use client";

import { ChevronRight, Plug } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { Chip, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Skeleton } from "@/components/ui/skeleton";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { GoogleMcp } from "@/lib/tipos";

type Tono = "exito" | "aviso" | "neutro";

function estadoGoogle(g: GoogleMcp): { tono: Tono; texto: string } {
  if (!g.autorizado) return { tono: "neutro", texto: "Sin autorizar" };
  return g.servicios.some((s) => s.falta_consentimiento) ? { tono: "aviso", texto: "Faltan permisos" } : { tono: "exito", texto: "Conectado" };
}

function TarjetaIntegracion({ href, icono, nombre, descripcion, estado, pie }: { href: string; icono: ReactNode; nombre: string; descripcion: string; estado?: { tono: Tono; texto: string }; pie?: string }) {
  return (
    <Link href={href} className="group flex flex-col gap-3 rounded-xl border bg-background p-4 shadow-sm transition-colors hover:bg-muted/40">
      <div className="flex items-start justify-between gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl border bg-muted text-muted-foreground [&>svg]:size-5">{icono}</span>
        {estado ? <Chip tono={estado.tono}>{estado.texto}</Chip> : <Skeleton className="h-5 w-20 rounded-full" />}
      </div>
      <div className="flex flex-col gap-0.5">
        <span className="text-sm font-semibold">{nombre}</span>
        <span className="text-xs text-muted-foreground">{descripcion}</span>
      </div>
      <div className="mt-auto flex items-center justify-between gap-2 text-xs text-muted-foreground">
        <span className="truncate">{pie ?? " "}</span>
        <ChevronRight className="size-4 shrink-0 transition-transform group-hover:translate-x-0.5" />
      </div>
    </Link>
  );
}

/** Integraciones MCP en tarjetas; el detalle de cada una (cómo se configura) está en su propia ruta. */
export function ListaMcp() {
  const google = useConsulta("mcp/google", api.googleMcp);
  const params = useSearchParams();
  const router = useRouter();
  const g = google.datos;

  // Google devuelve el código a esta ruta (la URI registrada); el detalle de Google lo canjea.
  const vuelta = params.has("code") || params.has("error");
  useEffect(() => { if (vuelta) router.replace(`/configuracion/mcp/google?${params.toString()}`); }, [vuelta, params, router]);
  if (vuelta) return null;

  return (
    <Pagina>
      <Marco icono={<Plug />} titulo="MCP" descripcion="Integraciones MCP del sistema. Abre una para ver y cambiar su configuración.">
        {google.error && <ErrorEnLinea titulo="No se pudo leer el MCP de Google" detalle={`${google.error} Si acabas de actualizar el sistema, reinicia la API.`} onReintentar={google.recargar} />}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <TarjetaIntegracion href="/configuracion/mcp/google" icono={<Plug />} nombre="Google Workspace"
            descripcion="Servidores MCP oficiales de Google con tu cuenta, y envío por Gmail y Chat."
            estado={g ? estadoGoogle(g) : google.error ? { tono: "neutro", texto: "Sin datos" } : undefined}
            pie={g ? `${g.servicios.filter((s) => s.activo).length} de ${g.servicios.length} servidores activos${g.cuenta ? ` · ${g.cuenta}` : ""}` : undefined} />
        </div>
      </Marco>
    </Pagina>
  );
}
