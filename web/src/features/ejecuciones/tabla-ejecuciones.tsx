"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Copy, FileText, History, MoreHorizontal, ScrollText } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Chip, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, TIPO, corteDe, duracion, enCurso, fecha, titulo } from "@/lib/formato";
import type { Ejecucion, EstadoEjecucion, Frecuencia } from "@/lib/tipos";
import { VisorLog } from "./visor-log";

type FiltroEstado = "todos" | "en_curso" | EstadoEjecucion;
const FILTROS_ESTADO: Record<FiltroEstado, string> = {
  todos: "Todos los estados", en_curso: "En curso", ok: "Correcto", error: "Error",
  configuracion: "Configuración", tablas_desactualizadas: "Tablas desactualizadas", en_cola: "En cola", ejecutando: "Ejecutando",
};
const OPCIONES: Record<string, string> = { "--forzar": "forzado", "--confirmar-escritura": "escribe en BD", "--conforme": "correo a todos" };
const segundos = (x: Ejecucion) => (x.fin ? Date.parse(x.fin) - Date.parse(x.inicio) : -1);

/** Historial de ejecuciones (todas o de un reporte). Se refresca cada 5 s, como las tablas de Dokploy. */
export function TablaEjecuciones({ reporte }: { reporte?: string }) {
  const consulta = useConsulta(`ejecuciones/${reporte ?? ""}`, () => api.ejecuciones(reporte), () => true, 5000);
  const { datos: catalogo } = useConsulta(reporte ? null : "reportes", api.reportes);
  const [estado, setEstado] = useState<FiltroEstado>("todos");
  const [tipo, setTipo] = useState<"todos" | Frecuencia>("todos");
  const [log, setLog] = useState<string | null>(null);

  const frecuencia = useMemo(() => new Map(catalogo?.map((r) => [r.nombre, r.frecuencia])), [catalogo]);
  const datos = useMemo(() => consulta.datos?.filter((x) =>
    (estado === "todos" || (estado === "en_curso" ? enCurso(x.estado) : x.estado === estado)) &&
    (tipo === "todos" || frecuencia.get(x.reporte) === tipo)), [consulta.datos, estado, tipo, frecuencia]);

  const columnas = useMemo<ColumnDef<Ejecucion, unknown>[]>(() => [
    {
      id: "estado", accessorKey: "estado",
      header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>,
      cell: ({ row: { original: x } }) => (
        <span className="flex items-center gap-2">
          <Punto tono={ESTADO_EJECUCION[x.estado].tono} etiqueta={ESTADO_EJECUCION[x.estado].texto} latido={enCurso(x.estado)} />
          <Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip>
        </span>
      ),
    },
    ...(reporte ? [] : [{
      id: "reporte", accessorFn: (x: Ejecucion) => titulo(x.reporte),
      header: ({ column }) => <Ordenable column={column}>Reporte</Ordenable>,
      cell: ({ row: { original: x } }) => (
        <span className="flex flex-col gap-0.5">
          <Link href={`/reportes/${x.reporte}`} className="font-medium hover:underline">{titulo(x.reporte)}</Link>
          {frecuencia.get(x.reporte) && <Badge variant="outline" className="h-4 w-fit px-1 text-[10px]">{TIPO[frecuencia.get(x.reporte)!]}</Badge>}
        </span>
      ),
    } satisfies ColumnDef<Ejecucion, unknown>]),
    {
      id: "corte", accessorFn: (x) => corteDe(x.argumentos) ?? "",
      header: ({ column }) => <Ordenable column={column}>Corte</Ordenable>,
      cell: ({ getValue }) => {
        const v = getValue() as string; // AAAA-MM-DD, o AAAA-MM en los reportes que reciben el mes
        return <span className="tabular-nums">{v.length === 10 ? fecha(v) : v || "—"}</span>;
      },
    },
    {
      id: "opciones", accessorFn: (x) => x.argumentos.filter((a) => OPCIONES[a]).map((a) => OPCIONES[a]).join(" "),
      header: "Opciones", enableSorting: false,
      cell: ({ row: { original: x } }) => (
        <span className="flex flex-wrap gap-1">
          {x.argumentos.filter((a) => OPCIONES[a]).map((a) => <Chip key={a} tono="aviso">{OPCIONES[a]}</Chip>)}
        </span>
      ),
    },
    {
      id: "inicio", accessorKey: "inicio",
      header: ({ column }) => <Ordenable column={column}>Inicio</Ordenable>,
      cell: ({ row: { original: x } }) => <span className="text-muted-foreground"><Hace iso={x.inicio} /></span>,
    },
    {
      id: "duracion", accessorFn: segundos, enableGlobalFilter: false,
      header: ({ column }) => <Ordenable column={column}>Duración</Ordenable>,
      cell: ({ row: { original: x } }) => <span className="text-muted-foreground tabular-nums">{duracion(x.inicio, x.fin)}</span>,
    },
    {
      id: "archivos", accessorFn: (x) => x.archivos.length, enableGlobalFilter: false,
      header: ({ column }) => <Ordenable column={column}>Archivos</Ordenable>,
      cell: ({ getValue }) => <span className="tabular-nums">{(getValue() as number) || "—"}</span>,
    },
    {
      id: "acciones", enableHiding: false, enableSorting: false,
      header: () => <span className="sr-only">Acciones</span>,
      cell: ({ row: { original: x } }) => (
        <div className="flex items-center justify-end gap-1">
          <Button variant="ghost" size="sm" onClick={() => setLog(x.id)}><ScrollText /> Detalle</Button>
          <DropdownMenu>
            <DropdownMenuTrigger render={<Button variant="ghost" size="icon-sm" aria-label="Más acciones" />}><MoreHorizontal /></DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52">
              <DropdownMenuGroup>
                <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => setLog(x.id)}><ScrollText /> Ver detalle</DropdownMenuItem>
                <DropdownMenuItem render={<Link href={`/reportes/${x.reporte}`} />}><FileText /> Ir al reporte</DropdownMenuItem>
              </DropdownMenuGroup>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => { navigator.clipboard.writeText(`python main.py ${x.argumentos.join(" ")}`); toast.success("Comando copiado"); }}>
                <Copy /> Copiar comando
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      ),
    },
  ], [reporte, frecuencia]);

  const filtros = (
    <>
      <Select value={estado} onValueChange={(v) => setEstado(v as FiltroEstado)} items={FILTROS_ESTADO}>
        <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
        <SelectContent>{Object.entries(FILTROS_ESTADO).map(([v, t]) => <SelectItem key={v} value={v}>{t}</SelectItem>)}</SelectContent>
      </Select>
      {!reporte && (
        <Select value={tipo} onValueChange={(v) => setTipo(v as typeof tipo)} items={{ todos: "Todos los tipos", diaria: "Diarios", mensual: "Mensuales" }}>
          <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="todos">Todos los tipos</SelectItem>
            <SelectItem value="diaria">Diarios</SelectItem>
            <SelectItem value="mensual">Mensuales</SelectItem>
          </SelectContent>
        </Select>
      )}
    </>
  );

  return (
    <>
      <TablaDatos columnas={columnas} datos={datos} cargando={consulta.cargando} error={consulta.error} onRecargar={consulta.recargar}
        buscar={reporte ? "Buscar por corte u opción…" : "Buscar por reporte, corte u opción…"} filtros={filtros}
        ordenInicial={[{ id: "inicio", desc: true }]}
        nombres={{ estado: "Estado", reporte: "Reporte", corte: "Corte", opciones: "Opciones", inicio: "Inicio", duracion: "Duración", archivos: "Archivos" }}
        vacio={{ icono: History, titulo: "Sin ejecuciones", descripcion: "Aquí aparecerá cada reporte que ejecutes desde la web." }} />
      <VisorLog id={log} onCerrar={() => setLog(null)} />
    </>
  );
}
