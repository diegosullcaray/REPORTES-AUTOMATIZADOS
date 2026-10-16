"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { History } from "lucide-react";
import { Chip } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import type { Consulta } from "@/hooks/use-consulta";
import { fecha } from "@/lib/formato";
import type { EntradaValidacion } from "@/lib/tipos";

const COLUMNAS: ColumnDef<EntradaValidacion, unknown>[] = [
  {
    id: "verificada", accessorFn: (x) => x.ejecutada, header: ({ column }) => <Ordenable column={column}>Verificada</Ordenable>,
    cell: ({ row: { original: x } }) => <span className="flex flex-col"><span className="tabular-nums">{x.ejecutada.slice(0, 16).replace("T", " ")}</span><span className="text-xs text-muted-foreground"><Hace iso={x.ejecutada} /></span></span>,
  },
  { id: "corte", accessorFn: (x) => x.corte, header: ({ column }) => <Ordenable column={column}>Corte</Ordenable>, cell: ({ row: { original: x } }) => <span className="tabular-nums">{fecha(x.corte)}</span> },
  {
    id: "resultado", accessorFn: (x) => (x.listo ? 0 : x.tablas_pendientes ? 1 : 2), enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Resultado</Ordenable>,
    cell: ({ row: { original: x } }) => <Chip tono={x.listo ? "exito" : x.tablas_pendientes ? "aviso" : "peligro"}>{x.listo ? "Todo al día" : x.tablas_pendientes ? "Faltan tablas" : "Sin verificar"}</Chip>,
  },
  {
    id: "reportes", accessorFn: (x) => x.reportes.filter((r) => r.listo).length, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Reportes al día</Ordenable>,
    cell: ({ row: { original: x } }) => <span className="tabular-nums">{x.reportes.filter((r) => r.listo).length} / {x.reportes.length}</span>,
  },
  { id: "tablas", accessorFn: (x) => x.tablas_ok, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Tablas al día</Ordenable>, cell: ({ row: { original: x } }) => <span className="tabular-nums">{x.tablas_ok} / {x.tablas_total}</span> },
  { id: "pendientes", accessorFn: (x) => x.tablas_pendientes, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Sin actualizar</Ordenable>, cell: ({ row: { original: x } }) => <span className="tabular-nums">{x.tablas_pendientes}</span> },
  { id: "dudosas", accessorFn: (x) => x.tablas_dudosas, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Sin verificar</Ordenable>, cell: ({ row: { original: x } }) => <span className="tabular-nums">{x.tablas_dudosas}</span> },
  {
    id: "chat", accessorFn: (x) => x.chat_enviado ?? "", enableGlobalFilter: false, header: "Pedido por Chat",
    cell: ({ row: { original: x } }) => x.chat_enviado
      ? <span className="flex flex-col text-xs"><span className="truncate" title={x.chat_a.join(", ")}>{x.chat_a.join(", ")}</span><span className="text-muted-foreground"><Hace iso={x.chat_enviado} /></span></span>
      : <span className="text-muted-foreground">—</span>,
  },
];

/** Cada verificación del responsable, de la más reciente a la más antigua. */
export function HistorialValidacion({ historial }: { historial: Consulta<EntradaValidacion[]> }) {
  return (
    <TablaDatos columnas={COLUMNAS} datos={historial.datos} cargando={historial.cargando} error={historial.error} onRecargar={historial.recargar}
      buscar="Buscar por fecha o corte…" porPagina={10} ordenInicial={[{ id: "verificada", desc: true }]}
      nombres={{ verificada: "Verificada", corte: "Corte", resultado: "Resultado", reportes: "Reportes al día", tablas: "Tablas al día", pendientes: "Sin actualizar", dudosas: "Sin verificar", chat: "Pedido por Chat" }}
      vacio={{ icono: History, titulo: "Aún no hay validaciones", descripcion: "Cada vez que verifiques las tablas de este responsable quedará aquí con su resultado." }} />
  );
}
