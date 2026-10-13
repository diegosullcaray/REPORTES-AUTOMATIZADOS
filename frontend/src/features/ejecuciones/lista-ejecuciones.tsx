"use client";

import { ChevronRight, Rocket } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { Chip, EsqueletoFilas, ErrorEnLinea, EstadoVacio, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Tarjeta } from "@/components/tarjeta";
import { buttonVariants } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { fecha } from "@/lib/formato";
import { ESTADO_PROCESO, LineaProceso, PasosEnLinea } from "./pasos-proceso";
import { agruparProcesos } from "./proceso";
import { VisorLog } from "./visor-log";

/** Ejecuciones de un reporte agrupadas por fecha de corte; cada una se abre para ver su proceso paso a paso. */
export function ListaEjecuciones({ reporte, limite = 60 }: { reporte: string; limite?: number }) {
  const { datos, error, cargando, recargar } = useConsulta(`ejecuciones/${reporte}/${limite}`, () => api.ejecuciones(reporte, limite), () => true, 5000);
  const procesos = useMemo(() => (datos ? agruparProcesos(datos) : []), [datos]);
  const [alternados, setAlternados] = useState<Set<string>>(new Set());
  const [log, setLog] = useState<string | null>(null);
  // El más reciente llega abierto; «alternados» guarda lo que la persona abrió o cerró.
  const abierto = (i: number, clave: string) => (i === 0) !== alternados.has(clave);
  const alternar = (clave: string) => setAlternados((s) => { const n = new Set(s); if (n.has(clave)) n.delete(clave); else n.add(clave); return n; });

  return (
    <Tarjeta titulo="Ejecuciones" descripcion="Agrupadas por fecha de corte; abre una para ver su proceso. Se actualiza sola."
      acciones={<Link href="/ejecuciones" className={buttonVariants({ variant: "outline", size: "sm" })}>Ver todas</Link>}>
      {error ? <ErrorEnLinea titulo="No se pudo cargar el historial" detalle={error} onReintentar={recargar} />
        : cargando && !datos ? <EsqueletoFilas filas={4} alto="h-16" />
        : !procesos.length ? <EstadoVacio icono={Rocket} titulo="Sin ejecuciones" descripcion="Ejecuta el reporte desde la pestaña General." />
        : (
          <ul className="flex flex-col gap-2">
            {procesos.map((p, i) => {
              const e = ESTADO_PROCESO[p.estado];
              const visible = abierto(i, p.clave);
              return (
                <li key={p.clave} className="rounded-lg border">
                  <button type="button" onClick={() => alternar(p.clave)} aria-expanded={visible}
                    className="flex w-full flex-wrap items-center gap-3 rounded-lg px-4 py-3 text-left transition-colors hover:bg-muted/40">
                    <ChevronRight className={`size-4 shrink-0 text-muted-foreground transition-transform duration-150 ${visible ? "rotate-90" : ""}`} />
                    <div className="flex min-w-0 flex-1 flex-col gap-1">
                      <span className="flex flex-wrap items-center gap-2 text-sm font-medium">
                        Corte {p.corte ? (p.corte.length === 10 ? fecha(p.corte) : p.corte) : "—"}
                        <Punto tono={e.tono} etiqueta={e.texto} latido={p.estado === "en_curso"} />
                      </span>
                      <PasosEnLinea pasos={p.pasos} />
                    </div>
                    <span className="flex flex-col items-end gap-1 text-xs text-muted-foreground">
                      <Chip tono={e.tono}>{e.texto}</Chip>
                      <Hace iso={p.ultima} />
                    </span>
                  </button>
                  {visible && <div className="border-t p-3"><LineaProceso pasos={p.pasos} onVerLog={setLog} /></div>}
                </li>
              );
            })}
          </ul>
        )}
      <VisorLog id={log} onCerrar={() => setLog(null)} />
    </Tarjeta>
  );
}
