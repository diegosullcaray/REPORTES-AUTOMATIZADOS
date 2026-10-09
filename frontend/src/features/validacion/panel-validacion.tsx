"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Database, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { Aviso, Chip, ErrorEnLinea } from "@/components/estados";
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
import type { ReporteResumen, TablaValidada, VerificacionGrupo } from "@/lib/tipos";
import { SolicitudProduccion } from "./solicitud-produccion";

const GRUPOS = { piero: "Heredados de Piero", erick: "Heredados de Erick" } as const;
type Grupo = keyof typeof GRUPOS;

const COLUMNAS: ColumnDef<TablaValidada, unknown>[] = [
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
  {
    id: "detalle", accessorFn: (t) => t.detalle, header: "Detalle",
    cell: ({ getValue }) => <span className="text-xs text-muted-foreground">{getValue() as string}</span>,
  },
];

function Resultado({ v, grupo, corte, onRecargar }: { v: VerificacionGrupo; grupo: Grupo; corte: string; onRecargar: () => void }) {
  const pendientes = v.reportes.filter((r) => r.pendientes > 0).length;
  const dudosos = v.reportes.filter((r) => r.dudosas > 0).length;
  return (
    <div className="flex flex-col gap-4">
      {v.listo ? (
        <Aviso tono="exito">✓ Las tablas de los {v.reportes.length} reportes están al día al {fecha(v.corte)}. Puedes ejecutarlos.</Aviso>
      ) : (
        <Aviso tono={pendientes ? "aviso" : "peligro"}>
          {pendientes > 0 && <>✗ {pendientes} reporte(s) con tablas sin actualizar al {fecha(v.corte)}: no los ejecutes hasta que Producción las cargue. </>}
          {dudosos > 0 && <>{dudosos} reporte(s) con tablas que no se pudieron verificar (conexión o columna de fecha por confirmar).</>}
        </Aviso>
      )}
      <ul className="flex flex-wrap gap-2">
        {v.reportes.map((r) => (
          <li key={r.nombre}>
            <Link href={`/reportes/${r.nombre}`} className="flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm hover:bg-muted/50">
              <span className="text-xs text-muted-foreground tabular-nums">{r.orden}</span>
              {titulo(r.nombre)}
              <Chip tono={r.listo ? "exito" : r.pendientes ? "aviso" : "peligro"}>{r.listo ? "al día" : r.pendientes ? `${r.pendientes} pendiente(s)` : `${r.dudosas} sin verificar`}</Chip>
            </Link>
          </li>
        ))}
      </ul>
      <TablaDatos columnas={COLUMNAS} datos={v.tablas} cargando={false} error={null} onRecargar={onRecargar}
        buscar="Buscar tabla o reporte…" porPagina={7} ordenInicial={[{ id: "estado", desc: false }]}
        nombres={{ estado: "Estado", tabla: "Tabla", servidor: "Servidor", ultima: "Última fecha", usan: "La usan", detalle: "Detalle" }}
        vacio={{ icono: Database, titulo: "Sin tablas" }} />
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
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={verificar} disabled={cargando || !!invalido || !corte}>
          <ShieldCheck /> {cargando ? "Verificando…" : `Verificar los ${propios.length} reportes al ${corte ? fecha(corte) : "corte"}`}
        </Button>
        {invalido && <span className="text-sm text-muted-foreground">{invalido}</span>}
      </div>
      {error ? <ErrorEnLinea titulo="No se pudo verificar" detalle={error} onReintentar={verificar} />
        : vigente ? <Resultado v={vigente} grupo={grupo} corte={corte} onRecargar={verificar} />
        : (
          <p className="text-sm text-muted-foreground">
            Comprueba de una vez las tablas de {propios.map((r) => titulo(r.nombre)).join(", ") || "los reportes"}. Cada tabla se consulta una sola vez (solo lectura) y,
            si falta alguna, obtienes un único mensaje para Producción.
          </p>
        )}
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
  const origen = useMemo(() => (elegido ? "Fecha elegida a mano" : config.datos?.corte_mensual.origen ?? ""), [elegido, config.datos]);

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
              <TabsContent key={g} value={g} className="pt-3">
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
