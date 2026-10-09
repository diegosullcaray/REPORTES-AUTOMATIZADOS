"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Database, FileSpreadsheet, ShieldCheck, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type ReactNode } from "react";
import { Chip, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_TABLA, errorDeCorte, fecha, titulo } from "@/lib/formato";
import type { ResumenValidacion, ReporteResumen, TablaValidada, VerificacionGrupo } from "@/lib/tipos";
import { SolicitudProduccion } from "./solicitud-produccion";

const GRUPOS = { piero: "Heredados de Piero", erick: "Heredados de Erick" } as const;
type Grupo = keyof typeof GRUPOS;

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
      <span className="text-2xl font-semibold tabular-nums" style={{ color: valor ? color : undefined }}>
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

function Resultado({ v, grupo, corte, onRecargar }: { v: VerificacionGrupo; grupo: Grupo; corte: string; onRecargar: () => void }) {
  const alDia = v.reportes.filter((r) => r.listo).length;
  const esperando = v.reportes.filter((r) => r.pendientes > 0).length;
  const sinVerificar = v.reportes.filter((r) => r.pendientes === 0 && r.dudosas > 0).length;
  const verificables = v.tablas.filter((t) => t.estado !== "SIN CONTROL");
  const tablasOk = verificables.filter((t) => t.estado === "OK").length;
  const problemas = v.problemas ?? [];

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Cifra etiqueta="Reportes al día" valor={alDia} total={v.reportes.length} tono="exito" />
        <Cifra etiqueta="Esperando carga de Producción" valor={esperando} tono="aviso" />
        <Cifra etiqueta="Sin verificar (conexión)" valor={sinVerificar} tono="peligro" />
        <Cifra etiqueta="Tablas al día" valor={tablasOk} total={verificables.length} tono="exito" />
      </div>

      {problemas.length > 0 && (
        <Bloque icono={<TriangleAlert />} titulo="Problemas de conexión (no son tablas desactualizadas)">
          <ul className="flex flex-col gap-2">
            {problemas.map((p) => (
              <li key={p.causa} className="flex flex-col gap-1 rounded-lg border p-3" style={{ background: "var(--mis-warning-light)", borderColor: "color-mix(in srgb, var(--mis-warning) 30%, transparent)" }}>
                <span className="text-sm font-medium">{p.causa} <span className="font-normal text-muted-foreground">· {p.tablas} tabla(s)</span></span>
                <span className="text-xs text-muted-foreground">{p.solucion}</span>
              </li>
            ))}
          </ul>
        </Bloque>
      )}

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

      {v.solicitud && <SolicitudProduccion texto={v.solicitud} guardar={() => api.guardarSolicitudGrupo(grupo, corte || null)} />}
    </div>
  );
}

function SeccionGrupo({ grupo, corte, reportes, resultado, onResultado }: {
  grupo: Grupo; corte: string; reportes: ReporteResumen[]; resultado: VerificacionGrupo | null; onResultado: (v: VerificacionGrupo | null) => void;
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
        : vigente ? <Resultado v={vigente} grupo={grupo} corte={corte} onRecargar={verificar} />
        : !cargando && <p className="text-sm text-muted-foreground">Cada tabla se consulta una sola vez aunque la usen varios reportes y, si falta alguna, obtienes un único mensaje para Producción.</p>}
    </div>
  );
}

/** Validación masiva de tablas: una sección por responsable (Piero / Erick) con todos sus reportes mensuales. */
export function PanelValidacionMasiva() {
  const params = useSearchParams();
  const router = useRouter();
  const pedido = params.get("grupo") as Grupo | null;
  const grupo: Grupo = pedido && pedido in GRUPOS ? pedido : "piero";
  const reportes = useConsulta("reportes", api.reportes);
  const config = useConsulta("configuracion", api.configuracion);
  const [elegido, setCorte] = useState<string | null>(null); // null = el corte mensual del .env
  const [resultados, setResultados] = useState<Partial<Record<Grupo, VerificacionGrupo | null>>>({});
  const corte = elegido ?? config.datos?.corte_mensual.fecha ?? "";
  const origen = elegido ? "Fecha elegida a mano" : config.datos?.corte_mensual.origen ?? "";

  return (
    <Pagina>
      <Marco icono={<ShieldCheck />} titulo="Validación de tablas" descripcion="¿Llegaron las tablas al corte? Se verifican todas las de los reportes mensuales de cada responsable, sin ejecutar nada (solo lectura).">
        <div className="flex flex-col gap-1">
          <Label htmlFor="corte-masivo">Fecha de corte (fin de mes)</Label>
          <Input id="corte-masivo" type="date" value={corte} onChange={(ev) => setCorte(ev.target.value)} className="w-48" aria-invalid={!!errorDeCorte("mensual", corte)} />
          <span className="text-xs text-muted-foreground">{errorDeCorte("mensual", corte) ?? origen}</span>
        </div>
        {reportes.error ? <ErrorEnLinea titulo="No se pudo cargar el catálogo" detalle={reportes.error} onReintentar={reportes.recargar} /> : (
          <Tabs value={grupo} onValueChange={(v) => router.replace(`/validacion?grupo=${v}`, { scroll: false })}>
            <TabsList className="w-full justify-start overflow-x-auto no-scrollbar sm:w-fit">
              {(Object.keys(GRUPOS) as Grupo[]).map((g) => <TabsTrigger key={g} value={g}>{GRUPOS[g]}</TabsTrigger>)}
            </TabsList>
            {(Object.keys(GRUPOS) as Grupo[]).map((g) => (
              <TabsContent key={g} value={g} className="pt-4">
                <SeccionGrupo grupo={g} corte={corte} reportes={reportes.datos ?? []} resultado={resultados[g] ?? null}
                  onResultado={(v) => setResultados((r) => ({ ...r, [g]: v }))} />
              </TabsContent>
            ))}
          </Tabs>
        )}
      </Marco>
    </Pagina>
  );
}
