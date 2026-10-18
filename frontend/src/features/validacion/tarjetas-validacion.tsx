"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { Chip } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { buttonVariants } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { fecha, titulo, type Tono } from "@/lib/formato";
import type { EntradaValidacion, ReporteResumen, ResumenValidacion } from "@/lib/tipos";
import { GRUPOS, type Grupo } from "./grupos";

type Estado = "al_dia" | "esperando" | "sin_verificar" | "sin_tablas" | "sin_validar";
const ESTADO: Record<Estado, { texto: string; tono: Tono }> = {
  al_dia: { texto: "Al día", tono: "exito" }, esperando: { texto: "Esperando carga", tono: "aviso" }, sin_verificar: { texto: "Sin verificar", tono: "peligro" },
  sin_tablas: { texto: "Sin tablas", tono: "neutro" }, sin_validar: { texto: "Sin validar", tono: "neutro" },
};
const FILTROS = { todos: "Todos los responsables", piero: GRUPOS.piero, erick: GRUPOS.erick };
const RESPONSABLE = { piero: "Piero", erick: "Erick" } as const;

interface Fila { reporte: ReporteResumen; grupo: Grupo; entrada?: EntradaValidacion; resumen?: ResumenValidacion; estado: Estado }

/** Estado de un reporte según la última verificación de su responsable: sin verificación → sin validar; no figura en ella → sin tablas. */
function estadoDe(entrada?: EntradaValidacion, resumen?: ResumenValidacion): Estado {
  if (!entrada) return "sin_validar";
  if (!resumen) return "sin_tablas";
  return resumen.listo ? "al_dia" : resumen.pendientes > 0 ? "esperando" : "sin_verificar";
}

/** Reportes mensuales de Piero y Erick con su estado en la última validación; cada uno lleva a la pantalla de su responsable. */
export function TablaValidacion() {
  const reportes = useConsulta("reportes", api.reportes);
  const piero = useConsulta("validacion/piero/historial/1", () => api.historialValidacion("piero", 1));
  const erick = useConsulta("validacion/erick/historial/1", () => api.historialValidacion("erick", 1));
  const [filtro, setFiltro] = useState<keyof typeof FILTROS>("todos");

  const filas = useMemo<Fila[] | undefined>(() => {
    if (!reportes.datos || !piero.datos || !erick.datos) return undefined;
    const ultima = { piero: piero.datos[0], erick: erick.datos[0] };
    return reportes.datos.filter((r): r is ReporteResumen & { grupo: Grupo } => r.frecuencia === "mensual" && (r.grupo === "piero" || r.grupo === "erick") && (filtro === "todos" || r.grupo === filtro))
      .map((r) => {
        const entrada = ultima[r.grupo];
        const resumen = entrada?.reportes.find((x) => x.nombre === r.nombre);
        return { reporte: r, grupo: r.grupo, entrada, resumen, estado: estadoDe(entrada, resumen) };
      });
  }, [reportes.datos, piero.datos, erick.datos, filtro]);

  const columnas = useMemo<ColumnDef<Fila, unknown>[]>(() => [
    { id: "orden", accessorFn: (f) => `${f.grupo} ${f.reporte.orden}`, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Nº</Ordenable>, cell: ({ row: { original: f } }) => <span className="text-xs text-muted-foreground tabular-nums">{f.reporte.orden}</span> },
    {
      id: "reporte", accessorFn: (f) => titulo(f.reporte.nombre), header: ({ column }) => <Ordenable column={column}>Reporte</Ordenable>,
      cell: ({ row: { original: f } }) => <Link href={`/validacion/${f.grupo}`} className="font-medium hover:underline">{titulo(f.reporte.nombre)}</Link>,
    },
    { id: "responsable", accessorFn: (f) => RESPONSABLE[f.grupo], header: ({ column }) => <Ordenable column={column}>Responsable</Ordenable> },
    { id: "tablas", accessorFn: (f) => f.resumen?.tablas ?? -1, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Tablas</Ordenable>, cell: ({ row: { original: f } }) => <span className="tabular-nums">{f.resumen?.tablas ?? "—"}</span> },
    { id: "pendientes", accessorFn: (f) => f.resumen?.pendientes ?? -1, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Sin actualizar</Ordenable>, cell: ({ row: { original: f } }) => <span className="tabular-nums">{f.resumen?.pendientes ?? "—"}</span> },
    {
      id: "verificada", accessorFn: (f) => f.entrada?.ejecutada ?? "", enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Última validación</Ordenable>,
      cell: ({ row: { original: f } }) => f.entrada
        ? <span className="flex flex-col"><span className="text-muted-foreground"><Hace iso={f.entrada.ejecutada} /></span><span className="text-xs text-muted-foreground">Corte {fecha(f.entrada.corte)}</span></span>
        : <span className="text-muted-foreground">—</span>,
    },
    { id: "estado", accessorFn: (f) => ESTADO[f.estado].texto, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>, cell: ({ row: { original: f } }) => <Chip tono={ESTADO[f.estado].tono}>{ESTADO[f.estado].texto}</Chip> },
    {
      id: "acciones", enableHiding: false, enableSorting: false, header: () => <span className="sr-only">Acciones</span>,
      cell: ({ row: { original: f } }) => <div className="flex justify-end"><Link href={`/validacion/${f.grupo}`} className={buttonVariants({ variant: "ghost", size: "sm" })}><ShieldCheck /> Validar</Link></div>,
    },
  ], []);

  const error = reportes.error ?? piero.error ?? erick.error;
  return (
    <TablaDatos columnas={columnas} datos={filas} cargando={reportes.cargando || piero.cargando || erick.cargando} error={error}
      onRecargar={() => { reportes.recargar(); piero.recargar(); erick.recargar(); }}
      buscar="Buscar reporte…" porPagina={15} ordenInicial={[{ id: "orden", desc: false }]}
      nombres={{ orden: "Nº", reporte: "Reporte", responsable: "Responsable", tablas: "Tablas", pendientes: "Sin actualizar", verificada: "Última validación", estado: "Estado" }}
      filtros={(
        <Select value={filtro} onValueChange={(v) => setFiltro(v as keyof typeof FILTROS)} items={FILTROS}>
          <SelectTrigger className="w-52"><SelectValue /></SelectTrigger>
          <SelectContent>{Object.entries(FILTROS).map(([v, t]) => <SelectItem key={v} value={v}>{t}</SelectItem>)}</SelectContent>
        </Select>
      )}
      vacio={{ icono: ShieldCheck, titulo: "Sin reportes mensuales", descripcion: "No hay reportes de Piero o Erick en el catálogo." }} />
  );
}
