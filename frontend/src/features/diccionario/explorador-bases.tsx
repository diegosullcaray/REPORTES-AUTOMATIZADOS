"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { ArrowLeft, ChevronRight, Database } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { Chip, ErrorEnLinea, EsqueletoFilas, EstadoVacio } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { REJILLA_TARJETAS, Tarjeta } from "@/components/tarjeta-enlace";
import { buttonVariants } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { DicBaseDetalle, DicProcedimientoFila, DicTablaDeBase } from "@/lib/tipos";
import { EnlaceTabla, EstadoSP, enlaceReporte } from "./comun";

const FILTROS = { todas: "Todas las que ocupa", propias: "Viven en esta base", ajenas: "De otras bases" };
type Seccion = "procedimientos" | "tablas";

/** Primer nivel: una tarjeta por base de datos, con lo que tiene (procedimientos y tablas). */
function Bases() {
  const { datos, error, recargar } = useConsulta("dic/bases", api.dic.bases);
  if (error) return <ErrorEnLinea titulo="No se pudieron cargar las bases" detalle={error} onReintentar={recargar} />;
  if (!datos) return <EsqueletoFilas filas={3} alto="h-28" />;
  if (!datos.length) return <EstadoVacio icono={Database} titulo="Sin bases" descripcion="El diccionario no tiene datos todavía." />;
  return (
    <div className={REJILLA_TARJETAS}>
      {datos.map((b) => (
        <Tarjeta key={b.base} href={`/diccionario/reportes?base=${encodeURIComponent(b.base)}`} icono={Database} titulo={b.base}
          descripcion={`${b.procedimientos} procedimientos · ${b.tablas_propias} tablas propias`}
          pie={<><span>{b.procedimientos ? `${b.reportes} reportes · ${b.tablas_usadas} tablas que ocupa` : "solo guarda tablas"}</span><ChevronRight className="size-4" /></>} />
      ))}
    </div>
  );
}

function Procedimientos({ base, datos, recargar }: { base: string; datos: DicProcedimientoFila[]; recargar: () => void }) {
  const columnas = useMemo<ColumnDef<DicProcedimientoFila, unknown>[]>(() => [
    { accessorKey: "nombre", header: ({ column }) => <Ordenable column={column}>Procedimiento</Ordenable>, cell: ({ row: { original: p } }) => <span className="font-mono text-[12px]">{p.nombre}</span> },
    { accessorKey: "estado", header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>, cell: ({ row: { original: p } }) => <EstadoSP estado={p.estado} /> },
    { id: "reportes", accessorFn: (p) => p.reportes.join(" "), header: "Reportes que lo ejecutan", enableSorting: false,
      cell: ({ row: { original: p } }) => (
        <span className="flex flex-wrap gap-1">
          {p.reportes.slice(0, 3).map((c) => <Link key={c} href={enlaceReporte(c)} className="rounded-md border px-1.5 py-0.5 font-mono text-[12px] hover:underline">{c}</Link>)}
          {p.reportes.length > 3 && <span className="text-xs text-muted-foreground">+{p.reportes.length - 3}</span>}
        </span>
      ) },
    { accessorKey: "parametros", header: ({ column }) => <Ordenable column={column}>Parám.</Ordenable>, cell: ({ row: { original: p } }) => <span className="tabular-nums">{p.parametros}</span> },
    { accessorKey: "tablas", header: ({ column }) => <Ordenable column={column}>Tablas</Ordenable>, cell: ({ row: { original: p } }) => <span className="tabular-nums">{p.tablas}</span> },
  ], []);
  return (
    <TablaDatos columnas={columnas} datos={datos} cargando={false} error={null} onRecargar={recargar} buscar={`Buscar procedimientos de ${base}…`}
      vacio={{ titulo: "Sin procedimientos", descripcion: "Esta base solo guarda tablas: ningún reporte del MIS ejecuta procedimientos aquí." }}
      nombres={{ nombre: "Procedimiento", estado: "Estado", reportes: "Reportes", parametros: "Parámetros", tablas: "Tablas" }} />
  );
}

function Tablas({ base, datos, recargar }: { base: string; datos: DicTablaDeBase[]; recargar: () => void }) {
  const [filtro, setFiltro] = useState<keyof typeof FILTROS>("todas");
  const filas = useMemo(() => datos.filter((t) => filtro === "todas" || (filtro === "propias") === t.propia), [datos, filtro]);
  const columnas = useMemo<ColumnDef<DicTablaDeBase, unknown>[]>(() => [
    { accessorKey: "nombre", header: ({ column }) => <Ordenable column={column}>Tabla</Ordenable>, cell: ({ row: { original: t } }) => <EnlaceTabla nombre={t.nombre} /> },
    { id: "vive", accessorFn: (t) => t.base, header: ({ column }) => <Ordenable column={column}>Vive en</Ordenable>, cell: ({ row: { original: t } }) => (t.propia ? <Chip tono="info">esta base</Chip> : <span className="font-mono text-[12px]">{t.base}</span>) },
    { id: "tipo", accessorFn: (t) => t.tipo ?? "—", header: ({ column }) => <Ordenable column={column}>Tipo</Ordenable> },
    { id: "existe", accessorFn: (t) => (t.existe === null ? "sin comprobar" : t.existe ? "existe" : "no existe"), header: "En la base",
      cell: ({ row: { original: t } }) => <Chip tono={t.existe === false ? "peligro" : t.existe ? "exito" : "neutro"}>{t.existe === null ? "sin comprobar" : t.existe ? "existe" : "no existe"}</Chip> },
    { accessorKey: "columnas", header: ({ column }) => <Ordenable column={column}>Columnas</Ordenable>, cell: ({ row: { original: t } }) => <span className="tabular-nums">{t.columnas}</span> },
    { accessorKey: "usada_por", header: ({ column }) => <Ordenable column={column}>Procedimientos que la usan</Ordenable>, cell: ({ row: { original: t } }) => <span className="tabular-nums">{t.usada_por}</span> },
    { id: "registro", accessorFn: (t) => (t.en_registro ? "sí" : "no"), header: "En mis reportes", cell: ({ row: { original: t } }) => (t.en_registro ? <Chip tono="info">en uso</Chip> : <span className="text-muted-foreground">—</span>) },
  ], []);
  return (
    <TablaDatos columnas={columnas} datos={filas} cargando={false} error={null} onRecargar={recargar} buscar={`Buscar tablas que ocupa ${base}…`}
      vacio={{ titulo: "Sin tablas", descripcion: "Ninguna tabla coincide con el filtro." }} ordenInicial={[{ id: "usada_por", desc: true }]}
      nombres={{ nombre: "Tabla", vive: "Vive en", tipo: "Tipo", existe: "En la base", columnas: "Columnas", usada_por: "Procedimientos que la usan", registro: "En mis reportes" }}
      filtros={(
        <Select value={filtro} onValueChange={(v) => setFiltro(v as keyof typeof FILTROS)} items={FILTROS}>
          <SelectTrigger className="w-56"><SelectValue /></SelectTrigger>
          <SelectContent>{Object.entries(FILTROS).map(([k, t]) => <SelectItem key={k} value={k}>{t}</SelectItem>)}</SelectContent>
        </Select>
      )} />
  );
}

/** Segundo nivel: una base con sus dos secciones, procedimientos y tablas que ocupa (pestañas en la URL: `?seccion=`). */
function DetalleBase({ base }: { base: string }) {
  const { datos, error, recargar } = useConsulta<DicBaseDetalle>(`dic/base/${base}`, () => api.dic.base(base));
  const router = useRouter();
  const ruta = usePathname();
  const pedida = useSearchParams().get("seccion");
  const seccion: Seccion = pedida === "tablas" ? "tablas" : "procedimientos";
  const irA = (s: Seccion) => router.replace(`${ruta}?base=${encodeURIComponent(base)}&seccion=${s}`, { scroll: false });

  if (error) return <ErrorEnLinea titulo="No se pudo cargar la base" detalle={error} onReintentar={recargar} />;
  if (!datos) return <EsqueletoFilas filas={5} />;
  return (
    <Tabs value={seccion} onValueChange={(v) => irA(v as Seccion)}>
      <TabsList>
        <TabsTrigger value="procedimientos">Procedimientos ({datos.procedimientos.length})</TabsTrigger>
        <TabsTrigger value="tablas">Tablas ({datos.tablas.length})</TabsTrigger>
      </TabsList>
      <TabsContent value="procedimientos" className="pt-3"><Procedimientos base={datos.base} datos={datos.procedimientos} recargar={recargar} /></TabsContent>
      <TabsContent value="tablas" className="pt-3"><Tablas base={datos.base} datos={datos.tablas} recargar={recargar} /></TabsContent>
    </Tabs>
  );
}

/** Reportes del MIS por niveles: primero la base de datos; dentro, sus procedimientos y las tablas que ocupa. El nivel va en la URL (`?base=`). */
export function ExploradorBasesDic() {
  const base = useSearchParams().get("base");
  return (
    <Pagina>
      <Marco icono={<Database />} titulo={base ?? "Reportes del MIS"}
        descripcion={base ? "Los procedimientos que ejecutan los reportes del MIS en esta base y las tablas que ocupa: las que guarda y las que sus procedimientos leen de otras bases." : "Elige una base de datos para ver sus procedimientos y las tablas que ocupa."}
        acciones={base ? <Link href="/diccionario/reportes" className={buttonVariants({ variant: "ghost", size: "sm" })}><ArrowLeft /> Bases</Link> : undefined}>
        {base ? <DetalleBase key={base} base={base} /> : <Bases />}
      </Marco>
    </Pagina>
  );
}
