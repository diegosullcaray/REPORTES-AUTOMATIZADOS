"use client";

import { ArrowRight, CalendarCheck, History, Rocket } from "lucide-react";
import Link from "next/link";
import { useMemo, useState, type ReactNode } from "react";
import { Chip, EsqueletoFilas, ErrorEnLinea, EstadoVacio, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Pagina } from "@/components/pagina";
import { buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { VisorLog } from "@/features/ejecuciones/visor-log";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, corteDe, enCurso, fecha, titulo } from "@/lib/formato";
import type { Ejecucion, ReporteResumen } from "@/lib/tipos";
import { resumenSemanal, pendientesDelCierre } from "./metricas";

function Tarjeta({ etiqueta, valor, detalle }: { etiqueta: string; valor: ReactNode; detalle?: ReactNode }) {
  return (
    <div className="flex min-h-32 flex-col justify-between rounded-xl border bg-background p-5">
      <span className="text-xs tracking-wider text-muted-foreground uppercase">{etiqueta}</span>
      <div className="flex flex-col gap-1">
        <span className="text-3xl font-semibold tracking-tight tabular-nums">{valor}</span>
        {detalle && <span className="text-xs text-muted-foreground">{detalle}</span>}
      </div>
    </div>
  );
}

function saludo(hora = new Date().getHours()) {
  return hora < 12 ? "Buenos días" : hora < 19 ? "Buenas tardes" : "Buenas noches";
}

function Recientes({ ejecuciones, onLog }: { ejecuciones: Ejecucion[]; onLog: (id: string) => void }) {
  if (ejecuciones.length === 0) return <EstadoVacio icono={Rocket} titulo="Aún no hay ejecuciones" descripcion="Elige un reporte y ejecútalo; aparecerá aquí." />;
  return (
    <ul className="divide-y">
      {ejecuciones.map((x) => {
        const e = ESTADO_EJECUCION[x.estado];
        return (
          <li key={x.id} className="flex items-center gap-4 px-5 py-3 transition-colors hover:bg-muted/40">
            <Punto tono={e.tono} etiqueta={e.texto} latido={enCurso(x.estado)} />
            <Link href={`/reportes/${x.reporte}`} className="flex min-w-0 flex-1 flex-col">
              <span className="truncate text-sm font-medium">{titulo(x.reporte)}</span>
              <span className="truncate text-xs text-muted-foreground">Corte {corteDe(x.argumentos) ?? "—"}</span>
            </Link>
            <span className="hidden w-40 justify-end sm:flex"><Chip tono={e.tono}>{e.texto}</Chip></span>
            <span className="hidden w-28 text-right text-xs text-muted-foreground md:inline"><Hace iso={x.inicio} /></span>
            <button onClick={() => onLog(x.id)} className="text-xs text-muted-foreground transition-colors hover:text-foreground">log →</button>
          </li>
        );
      })}
    </ul>
  );
}

function Cierre({ reportes, ejecuciones, corte }: { reportes: ReporteResumen[]; ejecuciones: Ejecucion[]; corte: string | null }) {
  if (!corte) return <p className="p-5 text-sm text-muted-foreground">Define FECHA_CORTE_MENSUAL en el .env para seguir el avance del cierre.</p>;
  const { listos, pendientes, total } = pendientesDelCierre(reportes, ejecuciones, corte);
  const avance = total ? Math.round((listos / total) * 100) : 0;
  return (
    <div className="flex flex-col gap-4 p-5">
      <div className="flex items-end justify-between gap-2">
        <span className="text-sm"><b className="text-2xl tabular-nums">{listos}</b> <span className="text-muted-foreground">de {total} mensuales listos</span></span>
        <span className="text-sm font-medium tabular-nums">{avance}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted" role="progressbar" aria-valuenow={avance} aria-valuemin={0} aria-valuemax={100}>
        <div className="h-full rounded-full bg-primary transition-[width] duration-300" style={{ width: `${avance}%` }} />
      </div>
      {pendientes.length > 0 ? (
        <ul className="flex max-h-64 flex-col gap-1 overflow-auto">
          {pendientes.map((r) => (
            <li key={r.nombre}>
              <Link href={`/reportes/${r.nombre}`} className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors hover:bg-muted/60">
                <span className="w-9 text-[11px] text-muted-foreground tabular-nums">{r.orden}</span>
                <span className="flex-1 truncate">{titulo(r.nombre)}</span>
                <ArrowRight className="size-3.5 text-muted-foreground" />
              </Link>
            </li>
          ))}
        </ul>
      ) : <Chip tono="exito">Cierre completo</Chip>}
    </div>
  );
}

/** Inicio (como el home de Dokploy): saludo, métricas de la semana, avance del cierre y ejecuciones recientes. */
export function PanelInicio() {
  const reportes = useConsulta("reportes", api.reportes);
  const ejecuciones = useConsulta("ejecuciones/inicio", () => api.ejecuciones(undefined, 500), () => true, 5000);
  const config = useConsulta("configuracion", api.configuracion);
  const [log, setLog] = useState<string | null>(null);

  const semana = useMemo(() => resumenSemanal(ejecuciones.datos ?? []), [ejecuciones.datos]);
  const diarios = reportes.datos?.filter((r) => r.frecuencia === "diaria").length ?? 0;
  const corte = config.datos?.corte_mensual.fecha ?? null;
  const cargandoTodo = (reportes.cargando && !reportes.datos) || (ejecuciones.cargando && !ejecuciones.datos);
  const error = reportes.error ?? ejecuciones.error;

  return (
    <Pagina>
      <section className="rounded-xl bg-sidebar p-2 sm:p-2.5">
        <div className="flex flex-col gap-6 rounded-xl border bg-background p-4 shadow-sm sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex flex-col gap-1">
              <h1 className="text-3xl font-semibold tracking-tight">{saludo()}</h1>
              <p className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                <CalendarCheck className="size-4" /> Corte mensual {corte ? fecha(corte) : "sin definir"}
                {config.datos?.corte_diario.fecha && <> · diario {fecha(config.datos.corte_diario.fecha)}</>}
              </p>
            </div>
            <Link href="/reportes" className={`${buttonVariants({ variant: "secondary" })} w-fit`}>Ir a reportes <ArrowRight /></Link>
          </div>

          {error ? (
            <ErrorEnLinea titulo="No se pudo cargar el resumen" detalle={error} onReintentar={() => { reportes.recargar(); ejecuciones.recargar(); }} />
          ) : (
            <>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {cargandoTodo ? Array.from({ length: 4 }, (_, i) => <Skeleton key={i} className="h-32 rounded-xl" />) : (
                  <>
                    <Tarjeta etiqueta="Reportes" valor={reportes.datos?.length ?? 0} detalle={`${diarios} diarios · ${(reportes.datos?.length ?? 0) - diarios} mensuales`} />
                    <Tarjeta etiqueta="Ejecuciones / 7 días" valor={semana.total} detalle={semana.variacion} />
                    <Tarjeta etiqueta="Éxito / 7 días" valor={semana.total ? `${semana.exito}%` : "—"} detalle={`${semana.correctas} correctas de ${semana.total}`} />
                    <div className="flex min-h-32 flex-col gap-3 rounded-xl border bg-background p-5">
                      <span className="text-xs tracking-wider text-muted-foreground uppercase">Estado / 7 días</span>
                      <ul className="flex flex-col gap-1.5 text-sm">
                        {semana.estados.map((e) => (
                          <li key={e.texto} className="flex items-center gap-2.5">
                            <Punto tono={e.tono} etiqueta={e.texto} />
                            <span className="w-8 font-semibold tabular-nums">{e.cantidad}</span>
                            <span className="text-muted-foreground">{e.texto}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </>
                )}
              </div>

              <div className="grid gap-4 lg:grid-cols-[1fr_22rem]">
                <div className="rounded-xl border bg-background">
                  <div className="flex items-center justify-between border-b px-5 py-4">
                    <h2 className="flex items-center gap-2 text-sm font-semibold"><History className="size-4 text-muted-foreground" /> Ejecuciones recientes</h2>
                    <Link href="/ejecuciones" className="text-xs text-muted-foreground transition-colors hover:text-foreground">ver todas →</Link>
                  </div>
                  {cargandoTodo ? <div className="p-5"><EsqueletoFilas filas={6} alto="h-9" /></div>
                    : <Recientes ejecuciones={(ejecuciones.datos ?? []).slice(0, 8)} onLog={setLog} />}
                </div>
                <div className="rounded-xl border bg-background">
                  <div className="border-b px-5 py-4">
                    <h2 className="flex items-center gap-2 text-sm font-semibold"><CalendarCheck className="size-4 text-muted-foreground" /> Cierre de mes</h2>
                  </div>
                  {cargandoTodo || config.cargando ? <div className="p-5"><EsqueletoFilas filas={4} alto="h-7" /></div>
                    : <Cierre reportes={reportes.datos ?? []} ejecuciones={ejecuciones.datos ?? []} corte={corte} />}
                </div>
              </div>
            </>
          )}
        </div>
      </section>
      <VisorLog id={log} onCerrar={() => setLog(null)} />
    </Pagina>
  );
}
