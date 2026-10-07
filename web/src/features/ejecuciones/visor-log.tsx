"use client";

import { ExternalLink } from "lucide-react";
import Link from "next/link";
import { Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Terminal } from "@/components/terminal";
import { buttonVariants } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, duracion, enCurso, fecha, titulo } from "@/lib/formato";

/** Log de una ejecución en un panel lateral (como el drawer de logs de Dokploy); se actualiza mientras corre. */
export function VisorLog({ id, onCerrar }: { id: string | null; onCerrar: () => void }) {
  const { datos: x, error, cargando, recargar } = useConsulta(id && `log/${id}`, () => api.ejecucion(id!), (d) => enCurso(d.estado), 1500);
  return (
    <Sheet open={!!id} onOpenChange={(abierto) => !abierto && onCerrar()}>
      <SheetContent side="right" className="w-full gap-0 sm:max-w-3xl">
        <SheetHeader className="border-b">
          <SheetTitle className="flex items-center gap-2">
            {x ? titulo(x.reporte) : "Ejecución"}
            {x && <Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip>}
          </SheetTitle>
          <SheetDescription>{x ? `Inicio ${fecha(x.inicio)} · duración ${duracion(x.inicio, x.fin)}` : "Cargando…"}</SheetDescription>
        </SheetHeader>
        <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-4">
          {error ? <ErrorEnLinea titulo="No se pudo leer el log" detalle={error} onReintentar={recargar} />
            : cargando && !x ? <EsqueletoFilas filas={8} alto="h-5" />
            : x && (
              <>
                <Terminal titulo={`python main.py ${x.argumentos.join(" ")}`} texto={x.log} vacio={enCurso(x.estado) ? "Esperando salida…" : "(sin salida)"} />
                <Link href={`/ejecuciones/${x.id}`} className={`${buttonVariants({ variant: "outline", size: "sm" })} self-start`}>
                  <ExternalLink /> Abrir detalle y archivos
                </Link>
              </>
            )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
