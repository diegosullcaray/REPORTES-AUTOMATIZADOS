"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Play } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Chip, Punto } from "@/components/estados";
import { Confirmar } from "@/components/confirmar";
import { Hace } from "@/components/hace";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Tarjeta } from "@/components/tarjeta";
import { Terminal } from "@/components/terminal";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { duracion, type Tono } from "@/lib/formato";
import type { DicEjecucion, DicProceso } from "@/lib/tipos";
import { ValidarBases } from "./validar-bases";

type Pestana = "procesos" | "historial";
const ESTADO: Record<DicEjecucion["estado"], { texto: string; tono: Tono }> = { ejecutando: { texto: "Ejecutando", tono: "info" }, ok: { texto: "Correcto", tono: "exito" }, error: { texto: "Con error", tono: "peligro" } };

function LogEjecucion({ id, onCerrar }: { id: string | null; onCerrar: () => void }) {
  const { datos: x } = useConsulta(id && `dic/ejecucion/${id}`, () => api.dic.ejecucion(id!), (d) => d.estado === "ejecutando", 1500);
  return (
    <Dialog open={!!id} onOpenChange={(a) => !a && onCerrar()}>
      <DialogContent className="flex max-h-[90vh] flex-col sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">{x?.proceso ?? "Proceso"} {x && <Chip tono={ESTADO[x.estado].tono}>{ESTADO[x.estado].texto}</Chip>}</DialogTitle>
          <DialogDescription>{x ? <>Inició <Hace iso={x.inicio} />{x.fin ? ` · duró ${duracion(x.inicio, x.fin)}` : ""}{x.codigo !== null ? ` · código de salida ${x.codigo}` : ""}</> : "Salida del proceso."}</DialogDescription>
        </DialogHeader>
        <div className="min-h-0 overflow-auto"><Terminal titulo={x?.proceso ?? ""} texto={x?.log ?? ""} /></div>
      </DialogContent>
    </Dialog>
  );
}

/** Procesos del repo DICCIONARIO que se lanzan con un clic: lista cerrada, uno a la vez, con historial y log. */
export function PanelProcesos() {
  const procesos = useConsulta("dic/procesos", api.dic.procesos);
  const historial = useConsulta("dic/ejecuciones", api.dic.ejecuciones, (d) => d.some((x) => x.estado === "ejecutando"), 2000);
  const [pedido, setPedido] = useState<DicProceso | null>(null);
  const [log, setLog] = useState<string | null>(null);
  const router = useRouter();
  const ruta = usePathname();
  const tab: Pestana = useSearchParams().get("tab") === "historial" ? "historial" : "procesos";
  const irA = (t: Pestana) => router.replace(t === "procesos" ? ruta : `${ruta}?tab=${t}`, { scroll: false });
  const ocupado = historial.datos?.some((x) => x.estado === "ejecutando") ?? false;

  async function lanzar(p: DicProceso) {
    try {
      const x = await api.dic.ejecutar(p.id);
      historial.recargar();
      irA("historial");  // el proceso recién lanzado se ve ahí, corriendo
      setLog(x.id);
    } catch (e) {
      toast.error("No se pudo lanzar", { description: (e as Error).message });
    }
  }

  const columnas = useMemo<ColumnDef<DicEjecucion, unknown>[]>(() => [
    { id: "estado", accessorFn: (x) => ESTADO[x.estado].texto, header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>,
      cell: ({ row: { original: x } }) => <span className="flex items-center gap-2"><Punto tono={ESTADO[x.estado].tono} etiqueta={ESTADO[x.estado].texto} latido={x.estado === "ejecutando"} /><Chip tono={ESTADO[x.estado].tono}>{ESTADO[x.estado].texto}</Chip></span> },
    { accessorKey: "proceso", header: ({ column }) => <Ordenable column={column}>Proceso</Ordenable> },
    { accessorKey: "inicio", header: ({ column }) => <Ordenable column={column}>Inicio</Ordenable>, cell: ({ row: { original: x } }) => <Hace iso={x.inicio} /> },
    { id: "duracion", accessorFn: (x) => duracion(x.inicio, x.fin), header: "Duración", enableSorting: false },
    { id: "ver", header: "", enableSorting: false, cell: ({ row: { original: x } }) => <Button variant="ghost" size="sm" onClick={() => setLog(x.id)}>Ver log</Button> },
  ], []);

  return (
    <Pagina>
      <Marco icono={<Play />} titulo="Procesos" descripcion="Mantén el diccionario al día sin abrir una consola. Corren en el repo DICCIONARIO, de a uno, y dejan su log.">
        <Tabs value={tab} onValueChange={(v) => irA(v as Pestana)}>
          <TabsList>
            <TabsTrigger value="procesos">Procesos</TabsTrigger>
            <TabsTrigger value="historial" className="gap-2">
              Historial{historial.datos ? ` (${historial.datos.length})` : ""}
              {ocupado && <Punto tono="info" etiqueta="Hay un proceso en curso" latido />}
            </TabsTrigger>
          </TabsList>
          <TabsContent value="procesos" className="pt-3">
            <div className="grid gap-3 md:grid-cols-3">
              {procesos.datos?.map((p) => (
                <Tarjeta key={p.id} titulo={p.nombre} descripcion={p.descripcion}
                  acciones={<Button size="sm" disabled={ocupado} onClick={() => setPedido(p)}><Play /> Ejecutar</Button>}>
                  <span className="font-mono text-[12px] text-muted-foreground">{p.comando}</span>
                  <span className="text-xs text-muted-foreground">Escribe en: {p.escribe}</span>
                </Tarjeta>
              ))}
            </div>
            <div className="pt-3"><ValidarBases /></div>
          </TabsContent>
          <TabsContent value="historial" className="pt-3">
            <TablaDatos columnas={columnas} datos={historial.datos} cargando={historial.cargando} error={historial.error} onRecargar={historial.recargar}
              vacio={{ titulo: "Sin ejecuciones", descripcion: "Lanza un proceso y aparecerá aquí. Se actualiza sola mientras hay uno en curso." }} ordenInicial={[{ id: "inicio", desc: true }]} porPagina={10}
              nombres={{ estado: "Estado", proceso: "Proceso", inicio: "Inicio", duracion: "Duración" }} />
          </TabsContent>
        </Tabs>
      </Marco>
      <Confirmar abierto={!!pedido} onAbierto={(a) => !a && setPedido(null)} titulo={`¿Ejecutar «${pedido?.nombre}»?`} accion="Ejecutar"
        descripcion={pedido && <>Corre <span className="font-mono">{pedido.comando}</span> en el repo DICCIONARIO. Escribe en: {pedido.escribe}.</>}
        onConfirmar={() => { const p = pedido; setPedido(null); if (p) void lanzar(p); }} />
      <LogEjecucion id={log} onCerrar={() => setLog(null)} />
    </Pagina>
  );
}
