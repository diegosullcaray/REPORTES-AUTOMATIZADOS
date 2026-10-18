"use client";

import { Check, Download, Play, Send } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Chip } from "@/components/estados";
import { Tarjeta } from "@/components/tarjeta";
import { Button, buttonVariants } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api, urlArchivo } from "@/lib/api";
import { fecha } from "@/lib/formato";
import type { PedidoEjecucion, ReporteDetalle } from "@/lib/tipos";

type Fase = NonNullable<PedidoEjecucion["fase"]>;

function Paso({ n, titulo, texto, archivo, hecho, reporte, accion }: { n: number; titulo: string; texto: string; archivo: string; hecho: boolean; reporte: string; accion: React.ReactNode }) {
  return (
    <li className="flex flex-wrap items-center gap-3 rounded-lg border px-4 py-3">
      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold">{hecho ? <Check className="size-3.5" /> : n}</span>
      <div className="flex min-w-0 flex-1 flex-col">
        <span className="text-sm font-medium">{titulo}</span>
        <span className="text-xs text-muted-foreground">{texto}</span>
      </div>
      {hecho && <Chip tono="exito">{archivo}</Chip>}
      <div className="flex gap-2">
        {accion}
        {hecho && <a href={urlArchivo(reporte, archivo)} className={buttonVariants({ variant: "ghost", size: "sm" })}><Download /> Descargar</a>}
      </div>
    </li>
  );
}

/** Flujo por fases de CMG Mora: las operaciones diarias cargan el mismo día; las provisiones, unos 5 días después. Con los dos Excel del corte se generan los INSERT. */
export function PanelFlujo({ reporte, corte }: { reporte: ReporteDetalle; corte: string }) {
  const archivos = useConsulta(`archivos/${reporte.nombre}`, () => api.archivos(reporte.nombre), () => true, 5000);
  const [ocupado, setOcupado] = useState<string | null>(null);
  const tiene = (nombre: string) => !!archivos.datos?.some((a) => a.nombre === nombre);
  const operaciones = `operaciones_${corte}.xlsx`;
  const provisiones = `provisiones_${corte}.xlsx`;
  const inserts = `inserts_${corte}.txt`;
  const listos = tiene(operaciones) && tiene(provisiones);

  async function correr(fase: Fase, chat = false) {
    setOcupado(fase + chat);
    try {
      await api.ejecutar({ reporte: reporte.nombre, fecha_corte: corte || null, fase, chat });
      toast.success("Ejecución en cola", { description: "El archivo aparece aquí al terminar; el log está en la pestaña Ejecuciones." });
    } catch (e) {
      toast.error("No se pudo ejecutar", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  return (
    <Tarjeta titulo="Flujo por fases" descripcion={`Corte ${fecha(corte)} (se cambia en «Fecha de cierre»). Cada fase deja su archivo en la carpeta de salida.`}>
      <ul className="flex flex-col gap-2">
        <Paso n={1} reporte={reporte.nombre} titulo="Operaciones diarias" texto="Recaudo + gasto operativo del día. Ya están cargados." archivo={operaciones} hecho={tiene(operaciones)}
          accion={<Button size="sm" variant="outline" disabled={!!ocupado} onClick={() => void correr("operaciones")}><Play /> Generar Excel</Button>} />
        <Paso n={2} reporte={reporte.nombre} titulo="Provisiones" texto="Llegan unos 5 días después. Si la tabla aún no existe, la ejecución termina en error y se puede reintentar." archivo={provisiones} hecho={tiene(provisiones)}
          accion={<Button size="sm" variant="outline" disabled={!!ocupado} onClick={() => void correr("provisiones")}><Play /> Generar Excel</Button>} />
        <Paso n={3} reporte={reporte.nombre} titulo="INSERT de SBTVRIE001" texto={listos ? "Los dos Excel del corte están listos." : "Se habilita cuando existen los dos Excel del corte."} archivo={inserts} hecho={tiene(inserts)}
          accion={<>
            <Button size="sm" disabled={!listos || !!ocupado} onClick={() => void correr("generar")}><Play /> Generar INSERT</Button>
            {reporte.envia_chat && <Button size="sm" variant="outline" disabled={!listos || !!ocupado} onClick={() => void correr("generar", true)}><Send /> Generar y enviar por Chat</Button>}
          </>} />
      </ul>
    </Tarjeta>
  );
}
