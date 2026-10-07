"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Database, FileSpreadsheet, Mail, Play } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { Chip, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, TIPO, enCurso, titulo } from "@/lib/formato";
import type { Ejecucion, Grupo, ReporteResumen } from "@/lib/tipos";

type Fila = ReporteResumen & { ultima?: Ejecucion };
const RESPONSABLE: Record<Grupo, string> = { diarias: "—", piero: "Piero", erick: "Erick" };
const FILTROS = { todos: "Todos", diaria: "Diarios", mensual: "Mensuales", piero: "Heredados de Piero", erick: "Heredados de Erick" };
type Filtro = keyof typeof FILTROS;

/** Catálogo completo con la última ejecución de cada reporte (vista de escritorio de /reportes). */
export function TablaReportes() {
  const reportes = useConsulta("reportes", api.reportes);
  const ejecuciones = useConsulta("ejecuciones/catalogo", () => api.ejecuciones(undefined, 500), () => true, 10000);
  const [filtro, setFiltro] = useState<Filtro>("todos");

  const filas = useMemo<Fila[] | undefined>(() => {
    if (!reportes.datos) return undefined;
    const ultima = new Map<string, Ejecucion>();
    for (const x of ejecuciones.datos ?? []) if (!ultima.has(x.reporte)) ultima.set(x.reporte, x); // vienen de la más reciente a la más antigua
    return reportes.datos
      .filter((r) => filtro === "todos" || r.frecuencia === filtro || r.grupo === filtro)
      .map((r) => ({ ...r, ultima: ultima.get(r.nombre) }));
  }, [reportes.datos, ejecuciones.datos, filtro]);

  const columnas = useMemo<ColumnDef<Fila, unknown>[]>(() => [
    {
      id: "orden", accessorFn: (r) => `${r.grupo} ${r.orden}`, enableGlobalFilter: false,
      header: ({ column }) => <Ordenable column={column}>Nº</Ordenable>,
      cell: ({ row: { original: r } }) => <span className="text-xs text-muted-foreground tabular-nums">{r.orden}</span>,
    },
    {
      id: "reporte", accessorFn: (r) => `${titulo(r.nombre)} ${r.descripcion}`,
      header: ({ column }) => <Ordenable column={column}>Reporte</Ordenable>,
      cell: ({ row: { original: r } }) => (
        <Link href={`/reportes/${r.nombre}`} className="flex min-w-0 max-w-[16rem] flex-col 2xl:max-w-md">
          <span className="flex items-center gap-1.5 font-medium hover:underline">
            {titulo(r.nombre)}
            {r.escribe_en_bd && <Database aria-label="escribe en BD" className="size-3.5 text-[var(--mis-warning)]" />}
            {r.envia_correo && <Mail aria-label="envía correo" className="size-3.5 text-muted-foreground" />}
          </span>
          <span className="truncate text-xs text-muted-foreground" title={r.descripcion}>{r.descripcion}</span>
        </Link>
      ),
    },
    {
      id: "tipo", accessorFn: (r) => TIPO[r.frecuencia],
      header: ({ column }) => <Ordenable column={column}>Tipo</Ordenable>,
      cell: ({ getValue }) => <Badge variant="outline">{getValue() as string}</Badge>,
    },
    {
      id: "responsable", accessorFn: (r) => RESPONSABLE[r.grupo],
      header: ({ column }) => <Ordenable column={column}>Responsable</Ordenable>,
      cell: ({ getValue }) => <span className="text-muted-foreground">{getValue() as string}</span>,
    },
    {
      id: "servidor", accessorFn: (r) => r.servidores.join(", "),
      header: "Servidor", enableSorting: false,
      cell: ({ getValue }) => <span className="font-mono text-xs text-muted-foreground">{getValue() as string}</span>,
    },
    {
      id: "ultima", accessorFn: (r) => r.ultima?.inicio ?? "", enableGlobalFilter: false,
      header: ({ column }) => <Ordenable column={column}>Última ejecución</Ordenable>,
      cell: ({ row: { original: r } }) => r.ultima ? (
        <span className="flex items-center gap-2">
          <Punto tono={ESTADO_EJECUCION[r.ultima.estado].tono} etiqueta={ESTADO_EJECUCION[r.ultima.estado].texto} latido={enCurso(r.ultima.estado)} />
          <span className="flex flex-col">
            <span className="text-xs">{ESTADO_EJECUCION[r.ultima.estado].texto}</span>
            <span className="text-xs text-muted-foreground"><Hace iso={r.ultima.inicio} /></span>
          </span>
        </span>
      ) : <Chip>Sin ejecutar</Chip>,
    },
    {
      id: "acciones", enableHiding: false, enableSorting: false, header: () => <span className="sr-only">Acciones</span>,
      cell: ({ row: { original: r } }) => (
        <Link href={`/reportes/${r.nombre}`} className={buttonVariants({ variant: "outline", size: "sm" })}><Play /> Abrir</Link>
      ),
    },
  ], []);

  return (
    <TablaDatos columnas={columnas} datos={filas} cargando={reportes.cargando} error={reportes.error} onRecargar={() => { reportes.recargar(); ejecuciones.recargar(); }}
      buscar="Buscar reporte o descripción…" porPagina={25} ocultas={{ servidor: false }}
      nombres={{ orden: "Nº", reporte: "Reporte", tipo: "Tipo", responsable: "Responsable", servidor: "Servidor", ultima: "Última ejecución" }}
      vacio={{ icono: FileSpreadsheet, titulo: "Sin reportes" }}
      filtros={
        <Select value={filtro} onValueChange={(v) => setFiltro(v as Filtro)} items={FILTROS}>
          <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent>{Object.entries(FILTROS).map(([v, t]) => <SelectItem key={v} value={v}>{t}</SelectItem>)}</SelectContent>
        </Select>
      } />
  );
}
