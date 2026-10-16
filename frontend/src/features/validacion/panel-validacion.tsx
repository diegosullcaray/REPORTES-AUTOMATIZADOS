"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Database, FileSpreadsheet, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useState, type ReactNode } from "react";
import { Aviso, Chip, ErrorEnLinea } from "@/components/estados";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { ESTADO_TABLA, errorDeCorte, fecha, titulo } from "@/lib/formato";
import type { Grupo } from "./grupos";
import type { ResumenValidacion, ReporteResumen, TablaValidada, VerificacionGrupo } from "@/lib/tipos";


const COLUMNAS_TABLAS: ColumnDef<TablaValidada, unknown>[] = [
  {
    id: "estado", accessorFn: (t) => t.estado, header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>,
    cell: ({ row: { original: t } }) => <Chip tono={ESTADO_TABLA[t.estado]}>{t.estado}</Chip>,
  },
  {
    id: "tabla", accessorFn: (t) => t.nombre, header: ({ column }) => <Ordenable column={column}>Tabla</Ordenable>,
    cell: ({ row: { original: t } }) => <span className="font-mono text-xs">{t.nombre}</span>,
  },
  { id: "servidor", accessorFn: (t) => t.servidor, header: "Servidor", cell: ({ getValue }) => <span className="text-muted-foreground">{getValue() as string}</span> },
  {
    id: "ultima", accessorFn: (t) => t.ultima_fecha ?? "", enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Última fecha</Ordenable>,
    cell: ({ row: { original: t } }) => <span className="whitespace-nowrap">{fecha(t.ultima_fecha)}</span>,
  },
  {
    id: "usan", accessorFn: (t) => t.reportes.map(titulo).join(" "), header: "La usan",
    cell: ({ row: { original: t } }) => <span className="line-clamp-2 max-w-xs text-xs text-muted-foreground" title={t.reportes.map(titulo).join(", ")}>{t.reportes.map(titulo).join(", ")}</span>,
  },
  { id: "detalle", accessorFn: (t) => t.detalle, header: "Detalle", cell: ({ getValue }) => <span className="text-xs text-muted-foreground">{getValue() as string}</span> },
];

const COLUMNAS_REPORTES: ColumnDef<ResumenValidacion, unknown>[] = [
  {
    id: "orden", accessorFn: (r) => r.orden, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Nº</Ordenable>,
    cell: ({ getValue }) => <span className="text-xs text-muted-foreground tabular-nums">{getValue() as string}</span>,
  },
  {
    id: "reporte", accessorFn: (r) => titulo(r.nombre), header: ({ column }) => <Ordenable column={column}>Reporte</Ordenable>,
    cell: ({ row: { original: r } }) => <Link href={`/reportes/${r.nombre}`} className="font-medium hover:underline">{titulo(r.nombre)}</Link>,
  },
  { id: "tablas", accessorFn: (r) => r.tablas, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Tablas</Ordenable>, cell: ({ getValue }) => <span className="tabular-nums">{getValue() as number}</span> },
  { id: "pendientes", accessorFn: (r) => r.pendientes, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Sin actualizar</Ordenable>, cell: ({ getValue }) => <span className="tabular-nums">{getValue() as number}</span> },
  { id: "dudosas", accessorFn: (r) => r.dudosas, enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Sin verificar</Ordenable>, cell: ({ getValue }) => <span className="tabular-nums">{getValue() as number}</span> },
  {
    id: "estado", accessorFn: (r) => (r.listo ? 0 : r.pendientes ? 1 : 2), enableGlobalFilter: false, header: ({ column }) => <Ordenable column={column}>Estado</Ordenable>,
    cell: ({ row: { original: r } }) => <Chip tono={r.listo ? "exito" : r.pendientes ? "aviso" : "peligro"}>{r.listo ? "Al día" : r.pendientes ? "Esperando carga" : "Sin verificar"}</Chip>,
  },
];

function Cifra({ etiqueta, valor, total, tono }: { etiqueta: string; valor: number; total?: number; tono: "exito" | "aviso" | "peligro" | "neutro" }) {
  const color = { exito: "var(--mis-success)", aviso: "var(--mis-warning)", peligro: "var(--mis-danger)", neutro: "var(--mis-text-secondary)" }[tono];
  return (
    <div className="flex flex-col gap-1 rounded-lg border bg-card p-4">
      <span className="text-xs text-muted-foreground">{etiqueta}</span>
      <span className="text-xl font-semibold tabular-nums" style={{ color: valor ? color : undefined }}>
        {valor}{total !== undefined && <span className="text-sm font-normal text-muted-foreground"> / {total}</span>}
      </span>
    </div>
  );
}

function Bloque({ icono, titulo: t, children }: { icono: ReactNode; titulo: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-3">
      <h3 className="flex items-center gap-2 text-sm font-semibold [&>svg]:size-4 [&>svg]:text-muted-foreground">{icono}{t}</h3>
      {children}
    </section>
  );
}

function Resultado({ v, grupo, onRecargar }: { v: VerificacionGrupo; grupo: Grupo; onRecargar: () => void }) {
  const alDia = v.reportes.filter((r) => r.listo).length;
  const esperando = v.reportes.filter((r) => r.pendientes > 0).length;
  const sinVerificar = v.reportes.filter((r) => r.pendientes === 0 && r.dudosas > 0).length;
  const verificables = v.tablas.filter((t) => t.estado !== "SIN CONTROL");
  const tablasOk = verificables.filter((t) => t.estado === "OK").length;

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Cifra etiqueta="Reportes al día" valor={alDia} total={v.reportes.length} tono="exito" />
        <Cifra etiqueta="Esperando carga de Producción" valor={esperando} tono="aviso" />
        <Cifra etiqueta="Sin verificar (conexión)" valor={sinVerificar} tono="peligro" />
        <Cifra etiqueta="Tablas al día" valor={tablasOk} total={verificables.length} tono="exito" />
      </div>

      <Bloque icono={<ShieldCheck />} titulo={v.listo ? `Todo al día al ${fecha(v.corte)}: puedes ejecutar los ${v.reportes.length} reportes` : `Detalle al ${fecha(v.corte)}`}>
        <Tabs defaultValue="reportes">
          <TabsList className="w-full justify-start overflow-x-auto no-scrollbar sm:w-fit">
            <TabsTrigger value="reportes"><FileSpreadsheet /> Por reporte</TabsTrigger>
            <TabsTrigger value="tablas"><Database /> Por tabla</TabsTrigger>
          </TabsList>
          <TabsContent value="reportes" className="pt-3">
            <TablaDatos columnas={COLUMNAS_REPORTES} datos={v.reportes} cargando={false} error={null} onRecargar={onRecargar}
              buscar="Buscar reporte…" porPagina={7} ordenInicial={[{ id: "orden", desc: false }]}
              nombres={{ orden: "Nº", reporte: "Reporte", tablas: "Tablas", pendientes: "Sin actualizar", dudosas: "Sin verificar", estado: "Estado" }}
              vacio={{ icono: FileSpreadsheet, titulo: "Sin reportes" }} />
          </TabsContent>
          <TabsContent value="tablas" className="pt-3">
            <TablaDatos columnas={COLUMNAS_TABLAS} datos={v.tablas} cargando={false} error={null} onRecargar={onRecargar}
              buscar="Buscar tabla o reporte…" porPagina={7} ordenInicial={[{ id: "estado", desc: false }]}
              nombres={{ estado: "Estado", tabla: "Tabla", servidor: "Servidor", ultima: "Última fecha", usan: "La usan", detalle: "Detalle" }}
              vacio={{ icono: Database, titulo: "Sin tablas" }} />
          </TabsContent>
        </Tabs>
      </Bloque>

      {v.solicitud && <Aviso>Faltan tablas por actualizar: el mensaje para pedirlo está en la pestaña <Link href={`/validacion/${grupo}?tab=mensaje`} className="font-medium underline">Mensaje</Link>.</Aviso>}
    </div>
  );
}

/** Verificar las tablas del responsable al corte elegido y ver el resultado por reporte y por tabla. */
export function PanelVerificacion({ grupo, corte, reportes, resultado, onResultado, onVerificado }: {
  grupo: Grupo; corte: string; reportes: ReporteResumen[]; resultado: VerificacionGrupo | null; onResultado: (v: VerificacionGrupo | null) => void; onVerificado: () => void;
}) {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const invalido = errorDeCorte("mensual", corte);
  const propios = reportes.filter((r) => r.grupo === grupo && r.frecuencia === "mensual");
  const vigente = resultado && resultado.corte === corte ? resultado : null;

  async function verificar() {
    setCargando(true);
    setError(null);
    try {
      onResultado(await api.verificarGrupo(grupo, corte || null));
      onVerificado(); // la verificación quedó en el historial
    } catch (e) {
      onResultado(null);
      setError((e as Error).message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-4">
        <div className="flex min-w-0 flex-1 flex-col gap-0.5">
          <span className="text-sm font-medium">{propios.length} reportes mensuales</span>
          <span className="truncate text-xs text-muted-foreground">{propios.map((r) => titulo(r.nombre)).join(" · ") || "—"}</span>
        </div>
        <Button onClick={verificar} disabled={cargando || !!invalido || !corte}>
          <ShieldCheck /> {cargando ? "Verificando…" : vigente ? "Verificar de nuevo" : `Verificar al ${corte ? fecha(corte) : "corte"}`}
        </Button>
      </div>
      {invalido && <p className="-mt-3 text-sm text-[var(--mis-danger)]">{invalido}</p>}
      {cargando && <p className="-mt-3 text-sm text-muted-foreground">Consultando los servidores a la vez (solo lectura). Si alguno no responde puede tardar hasta un minuto.</p>}

      {error ? <ErrorEnLinea titulo="No se pudo verificar" detalle={error} onReintentar={verificar} />
        : vigente ? <Resultado v={vigente} grupo={grupo} onRecargar={verificar} />
        : !cargando && <p className="text-sm text-muted-foreground">Cada tabla se consulta una sola vez aunque la usen varios reportes y, si falta alguna, obtienes un único mensaje para Producción.</p>}
    </div>
  );
}
