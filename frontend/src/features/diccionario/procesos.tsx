"use client";

import { ChevronRight, Database, FlaskConical, Hammer, Play, RefreshCw, ShieldCheck, type LucideIcon } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { Chip, ErrorEnLinea, EsqueletoFilas, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { REJILLA_TARJETAS, Tarjeta } from "@/components/tarjeta-enlace";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO, LogEjecucion, TablaEjecuciones } from "./ejecuciones";

type Pestana = "procesos" | "historial";
export const ICONO_PROCESO: Record<string, LucideIcon> = { construir: Hammer, generar: RefreshCw, verificar: ShieldCheck, test: FlaskConical, bases: Database };

/** Procesos del diccionario: una tarjeta por proceso (entra a su detalle) y el historial de todos en otra pestaña. */
export function PanelProcesos() {
  const procesos = useConsulta("dic/procesos", api.dic.procesos);
  const historial = useConsulta("dic/ejecuciones", () => api.dic.ejecuciones(), (d) => d.some((x) => x.estado === "ejecutando"), 2000);
  const [log, setLog] = useState<string | null>(null);
  const router = useRouter();
  const ruta = usePathname();
  const tab: Pestana = useSearchParams().get("tab") === "historial" ? "historial" : "procesos";
  const irA = (t: Pestana) => router.replace(t === "procesos" ? ruta : `${ruta}?tab=${t}`, { scroll: false });
  const ocupado = historial.datos?.some((x) => x.estado === "ejecutando") ?? false;
  const ultima = useMemo(() => new Map([...(historial.datos ?? [])].reverse().map((x) => [x.proceso, x])), [historial.datos]);   // llega de la más reciente a la más antigua: al invertir, la última pisa a las anteriores

  return (
    <Pagina>
      <Marco icono={<Play />} titulo="Procesos" descripcion="Mantén el diccionario al día sin abrir una consola. Entra a uno para ejecutarlo y ver sus ejecuciones, su script y lo que genera.">
        <Tabs value={tab} onValueChange={(v) => irA(v as Pestana)}>
          <TabsList>
            <TabsTrigger value="procesos">Procesos</TabsTrigger>
            <TabsTrigger value="historial" className="gap-2">
              Historial{historial.datos ? ` (${historial.datos.length})` : ""}
              {ocupado && <Punto tono="info" etiqueta="Hay un proceso en curso" latido />}
            </TabsTrigger>
          </TabsList>
          <TabsContent value="procesos" className="pt-3">
            {procesos.error ? <ErrorEnLinea titulo="No se pudieron cargar los procesos" detalle={procesos.error} onReintentar={procesos.recargar} /> : !procesos.datos ? <EsqueletoFilas filas={2} alto="h-28" /> : (
              <div className={REJILLA_TARJETAS}>
                {procesos.datos.map((p) => {
                  const x = ultima.get(p.id);
                  return (
                    <Tarjeta key={p.id} href={`/diccionario/procesos/${p.id}`} icono={ICONO_PROCESO[p.id] ?? Play} titulo={p.nombre} descripcion={p.descripcion}
                      estado={x ? <Chip tono={ESTADO[x.estado].tono}>{ESTADO[x.estado].texto}</Chip> : undefined}
                      pie={<><span className="truncate font-mono">{p.comando}</span>{x ? <span className="shrink-0"><Hace iso={x.inicio} /></span> : <ChevronRight className="size-4 shrink-0" />}</>} />
                  );
                })}
              </div>
            )}
          </TabsContent>
          <TabsContent value="historial" className="pt-3">
            <TablaEjecuciones consulta={historial} conProceso onLog={setLog} />
          </TabsContent>
        </Tabs>
      </Marco>
      <LogEjecucion id={log} onCerrar={() => setLog(null)} />
    </Pagina>
  );
}
