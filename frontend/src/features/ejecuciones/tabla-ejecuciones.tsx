"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { History, ListChecks } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { Chip, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { TIPO, fecha, titulo } from "@/lib/formato";
import type { Frecuencia } from "@/lib/tipos";
import { ESTADO_PROCESO, LineaProceso, PasosEnLinea } from "./pasos-proceso";
import { agruparProcesos, type EstadoProceso, type Proceso } from "./proceso";
import { VisorLog } from "./visor-log";

type FiltroEstado = "todos" | EstadoProceso;
const FILTROS_ESTADO: Record<FiltroEstado, string> = { todos: "Todos los estados", completo: "Completos", incompleto: "Incompletos", fallo: "Con fallas", en_curso: "En curso" };
const corteTexto = (c: string | null) => (c ? (c.length === 10 ? fecha(c) : c) : "—");

/** Ejecuciones agrupadas por reporte y fecha de corte: una fila por proceso; al abrirla se ven sus pasos. Se refresca cada 5 s. */
export function TablaEjecuciones() {
  const consulta = useConsulta("ejecuciones/", () => api.ejecuciones(), () => true, 5000);
  const { datos: catalogo } = useConsulta("reportes", api.reportes);
  const [estado, setEstado] = useState<FiltroEstado>("todos");
  const [tipo, setTipo] = useState<"todos" | Frecuencia>("todos");
  const [abierto, setAbierto] = useState<string | null>(null);
  const [log, setLog] = useState<string | null>(null);

  const frecuencia = useMemo(() => new Map(catalogo?.map((r) => [r.nombre, r.frecuencia])), [catalogo]);
  const procesos = useMemo(() => (consulta.datos ? agruparProcesos(consulta.datos) : undefined), [consulta.datos]);
  const datos = useMemo(() => procesos?.filter((p) =>
    (estado === "todos" || p.estado === estado) && (tipo === "todos" || frecuencia.get(p.reporte) === tipo)), [procesos, estado, tipo, frecuencia]);
  const elegido = procesos?.find((p) => p.clave === abierto) ?? null;

  const columnas = useMemo<ColumnDef<Proceso, unknown>[]>(() => [
    {
      id: "estado", accessorFn: (p) => ESTADO_PROCESO[p.estado].texto,
      header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>,
      cell: ({ row: { original: p } }) => (
        <span className="flex items-center gap-2">
          <Punto tono={ESTADO_PROCESO[p.estado].tono} etiqueta={ESTADO_PROCESO[p.estado].texto} latido={p.estado === "en_curso"} />
          <Chip tono={ESTADO_PROCESO[p.estado].tono}>{ESTADO_PROCESO[p.estado].texto}</Chip>
        </span>
      ),
    },
    {
      id: "reporte", accessorFn: (p) => titulo(p.reporte),
      header: ({ column }) => <Ordenable column={column}>Reporte</Ordenable>,
      cell: ({ row: { original: p } }) => (
        <span className="flex flex-col gap-0.5">
          <Link href={`/reportes/${p.reporte}`} className="font-medium hover:underline">{titulo(p.reporte)}</Link>
          {frecuencia.get(p.reporte) && <Badge variant="outline" className="h-4 w-fit px-1 text-[10px]">{TIPO[frecuencia.get(p.reporte)!]}</Badge>}
        </span>
      ),
    },
    {
      id: "corte", accessorFn: (p) => p.corte ?? "",
      header: ({ column }) => <Ordenable column={column}>Corte</Ordenable>,
      cell: ({ row: { original: p } }) => <span className="tabular-nums">{corteTexto(p.corte)}</span>,
    },
    {
      id: "proceso", accessorFn: (p) => p.pasos.map((x) => x.nombre).join(" "), header: "Proceso", enableSorting: false,
      cell: ({ row: { original: p } }) => <PasosEnLinea pasos={p.pasos} />,
    },
    {
      id: "ultima", accessorKey: "ultima", enableGlobalFilter: false,
      header: ({ column }) => <Ordenable column={column}>Última</Ordenable>,
      cell: ({ row: { original: p } }) => <span className="text-muted-foreground"><Hace iso={p.ultima} /></span>,
    },
    {
      id: "acciones", enableHiding: false, enableSorting: false,
      header: () => <span className="sr-only">Acciones</span>,
      cell: ({ row: { original: p } }) => (
        <div className="flex justify-end"><Button variant="ghost" size="sm" onClick={() => setAbierto(p.clave)}><ListChecks /> Ver proceso</Button></div>
      ),
    },
  ], [frecuencia]);

  const filtros = (
    <>
      <Select value={estado} onValueChange={(v) => setEstado(v as FiltroEstado)} items={FILTROS_ESTADO}>
        <SelectTrigger className="w-44"><SelectValue /></SelectTrigger>
        <SelectContent>{Object.entries(FILTROS_ESTADO).map(([v, t]) => <SelectItem key={v} value={v}>{t}</SelectItem>)}</SelectContent>
      </Select>
      <Select value={tipo} onValueChange={(v) => setTipo(v as typeof tipo)} items={{ todos: "Todos los tipos", diaria: "Diarios", mensual: "Mensuales" }}>
        <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
        <SelectContent>
          <SelectItem value="todos">Todos los tipos</SelectItem>
          <SelectItem value="diaria">Diarios</SelectItem>
          <SelectItem value="mensual">Mensuales</SelectItem>
        </SelectContent>
      </Select>
    </>
  );

  return (
    <>
      <TablaDatos columnas={columnas} datos={datos} cargando={consulta.cargando} error={consulta.error} onRecargar={consulta.recargar}
        buscar="Buscar por reporte o corte…" filtros={filtros} porPagina={10} ordenInicial={[{ id: "ultima", desc: true }]}
        nombres={{ estado: "Estado", reporte: "Reporte", corte: "Corte", proceso: "Proceso", ultima: "Última" }}
        vacio={{ icono: History, titulo: "Sin ejecuciones", descripcion: "Aquí aparecerá cada reporte que ejecutes desde la web, agrupado por fecha de corte." }} />
      <Dialog open={!!elegido} onOpenChange={(a) => !a && setAbierto(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{elegido && titulo(elegido.reporte)}</DialogTitle>
            <DialogDescription>{elegido && `Corte ${corteTexto(elegido.corte)} · ${ESTADO_PROCESO[elegido.estado].texto.toLowerCase()}`}</DialogDescription>
          </DialogHeader>
          {elegido && <LineaProceso pasos={elegido.pasos} onVerLog={setLog} />}
        </DialogContent>
      </Dialog>
      <VisorLog id={log} onCerrar={() => setLog(null)} />
    </>
  );
}
