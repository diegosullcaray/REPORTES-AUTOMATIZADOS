"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { useMemo } from "react";
import { Chip, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Terminal } from "@/components/terminal";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useConsulta, type Consulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { duracion, type Tono } from "@/lib/formato";
import type { DicEjecucion } from "@/lib/tipos";

export const ESTADO: Record<DicEjecucion["estado"], { texto: string; tono: Tono }> = { ejecutando: { texto: "Ejecutando", tono: "info" }, ok: { texto: "Correcto", tono: "exito" }, error: { texto: "Con error", tono: "peligro" } };

/** Log de una ejecución en un diálogo; se actualiza solo mientras corre. */
export function LogEjecucion({ id, onCerrar }: { id: string | null; onCerrar: () => void }) {
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

/** Tabla de ejecuciones (todas o las de un proceso); «Ver log» abre su salida. */
export function TablaEjecuciones({ consulta, conProceso, onLog }: { consulta: Consulta<DicEjecucion[]>; conProceso?: boolean; onLog: (id: string) => void }) {
  const columnas = useMemo<ColumnDef<DicEjecucion, unknown>[]>(() => [
    { id: "estado", accessorFn: (x) => ESTADO[x.estado].texto, header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>,
      cell: ({ row: { original: x } }) => <span className="flex items-center gap-2"><Punto tono={ESTADO[x.estado].tono} etiqueta={ESTADO[x.estado].texto} latido={x.estado === "ejecutando"} /><Chip tono={ESTADO[x.estado].tono}>{ESTADO[x.estado].texto}</Chip></span> },
    ...(conProceso ? [{ accessorKey: "proceso", header: ({ column }) => <Ordenable column={column}>Proceso</Ordenable> } as ColumnDef<DicEjecucion, unknown>] : []),
    { accessorKey: "inicio", header: ({ column }) => <Ordenable column={column}>Inicio</Ordenable>, cell: ({ row: { original: x } }) => <Hace iso={x.inicio} /> },
    { id: "duracion", accessorFn: (x) => duracion(x.inicio, x.fin), header: "Duración", enableSorting: false },
    { id: "ver", header: "", enableSorting: false, cell: ({ row: { original: x } }) => <Button variant="ghost" size="sm" onClick={() => onLog(x.id)}>Ver log</Button> },
  ], [conProceso, onLog]);
  return (
    <TablaDatos columnas={columnas} datos={consulta.datos} cargando={consulta.cargando} error={consulta.error} onRecargar={consulta.recargar}
      vacio={{ titulo: "Sin ejecuciones", descripcion: "Ejecútalo y aparecerá aquí. Se actualiza sola mientras hay uno en curso." }} ordenInicial={[{ id: "inicio", desc: true }]} porPagina={10}
      nombres={{ estado: "Estado", proceso: "Proceso", inicio: "Inicio", duracion: "Duración" }} />
  );
}
