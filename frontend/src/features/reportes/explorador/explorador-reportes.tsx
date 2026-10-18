"use client";

import { CalendarDays, ChevronRight, Database, FileSpreadsheet, Folder, LayoutGrid, Mail, Server, Trash2, UserRound } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState, type ReactNode } from "react";
import { toast } from "sonner";
import { ErrorEnLinea, EsqueletoFilas, EstadoVacio, Punto } from "@/components/estados";
import { Confirmar } from "@/components/confirmar";
import { Hace } from "@/components/hace";
import { REJILLA_TARJETAS as REJILLA, Tarjeta } from "@/components/tarjeta-enlace";
import { Button } from "@/components/ui/button";
import { useConsulta, type Consulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, GRUPOS, agruparPorCarpeta, enCurso, titulo } from "@/lib/formato";
import type { Ejecucion, Grupo, ReporteResumen, Seccion } from "@/lib/tipos";

const ICONO_GRUPO: Record<Grupo, LucideIcon> = { diarias: CalendarDays, piero: UserRound, erick: UserRound };

/** Reportes en tarjetas por niveles (como proyectos → servicios de Dokploy): grupo → carpeta del legado → reporte. El nivel va en la URL. */
export function ExploradorReportes({ reportes, secciones }: { reportes: Consulta<ReporteResumen[]>; secciones: Consulta<Seccion[]> }) {
  const ejecuciones = useConsulta("ejecuciones/catalogo", () => api.ejecuciones(undefined, 500), () => true, 10000);
  const router = useRouter();
  const [borrando, setBorrando] = useState(false);
  const params = useSearchParams();
  const idSeccion = params.get("seccion");
  const grupo = params.get("grupo") as Grupo | null;
  const carpeta = params.get("carpeta");

  const ultima = useMemo(() => {
    const m = new Map<string, Ejecucion>();
    for (const x of ejecuciones.datos ?? []) if (!m.has(x.reporte)) m.set(x.reporte, x); // vienen de la más reciente a la más antigua
    return m;
  }, [ejecuciones.datos]);

  if (reportes.error) return <ErrorEnLinea titulo="No se pudo cargar el catálogo" detalle={reportes.error} onReintentar={reportes.recargar} />;
  if (reportes.cargando && !reportes.datos) return <EsqueletoFilas filas={3} alto="h-28" />;
  const todos = reportes.datos ?? [];
  const delGrupo = grupo && grupo in GRUPOS ? todos.filter((r) => r.grupo === grupo) : [];

  const tarjetaReporte = (r: ReporteResumen) => {
    const x = ultima.get(r.nombre);
    const e = x && ESTADO_EJECUCION[x.estado];
    return (
      <Tarjeta key={r.nombre} href={`/reportes/${r.nombre}`} icono={FileSpreadsheet} titulo={`${r.orden} · ${titulo(r.nombre)}`} descripcion={r.descripcion}
        estado={<Punto tono={e?.tono ?? "neutro"} etiqueta={e?.texto ?? "Sin ejecutar"} latido={!!x && enCurso(x.estado)} />}
        pie={<>
          <span className="flex items-center gap-1.5"><Server className="size-3" />{r.servidores.join(", ")}{r.escribe_en_bd && <Database aria-label="escribe en BD" className="size-3 text-[var(--mis-warning)]" />}{r.envia_correo && <Mail aria-label="envía correo" className="size-3" />}</span>
          <span>{x ? <Hace iso={x.inicio} /> : "Sin ejecutar"}</span>
        </>} />
    );
  };

  const entradas = grupo ? agruparPorCarpeta(delGrupo) : [];
  const nodo = carpeta ? entradas.find((e) => e.tipo === "nodo" && e.reportes[0].carpeta === carpeta) : undefined;

  const seccion = secciones.datos?.find((x) => x.id === idSeccion);
  async function eliminar() {
    if (!seccion) return;
    try {
      await api.eliminarSeccion(seccion.id);
      toast.success("Sección eliminada");
      secciones.recargar();
      router.replace("/reportes");
    } catch (e) {
      toast.error("No se pudo eliminar", { description: (e as Error).message });
    } finally {
      setBorrando(false);
    }
  }

  let contenido: ReactNode;
  if (idSeccion) {
    const miembros = todos.filter((r) => seccion?.reportes.includes(r.nombre));
    contenido = !seccion ? <EstadoVacio icono={LayoutGrid} titulo="Esa sección ya no existe" />
      : (
        <div className="flex flex-col gap-4">
          <div className="flex items-start justify-between gap-3">
            <p className="text-sm text-muted-foreground">{seccion.descripcion || `${miembros.length} reportes`}</p>
            <Button variant="outline" size="sm" onClick={() => setBorrando(true)}><Trash2 /> Eliminar sección</Button>
          </div>
          {miembros.length ? <div className={REJILLA}>{miembros.map(tarjetaReporte)}</div> : <EstadoVacio icono={FileSpreadsheet} titulo="Sección sin reportes" />}
          <Confirmar abierto={borrando} onAbierto={setBorrando} titulo="Eliminar sección" accion="Eliminar" peligro onConfirmar={() => void eliminar()}
            descripcion={<>Se borra la sección <b>{seccion.nombre}</b>. Los reportes no se tocan.</>} />
        </div>
      );
  } else if (!grupo) {
    contenido = (
      <div className={REJILLA}>
        {(Object.keys(GRUPOS) as Grupo[]).map((g) => {
          const n = todos.filter((r) => r.grupo === g).length;
          return <Tarjeta key={g} href={`/reportes?grupo=${g}`} icono={ICONO_GRUPO[g]} titulo={GRUPOS[g]} pie={<><span>{n} {n === 1 ? "reporte" : "reportes"}</span><ChevronRight className="size-4" /></>} />;
        })}
        {(secciones.datos ?? []).map((x) => (
          <Tarjeta key={x.id} href={`/reportes?seccion=${x.id}`} icono={LayoutGrid} titulo={x.nombre} descripcion={x.descripcion || undefined}
            pie={<><span>{x.reportes.length} {x.reportes.length === 1 ? "reporte" : "reportes"}</span><ChevronRight className="size-4" /></>} />
        ))}
      </div>
    );
  } else if (nodo?.tipo === "nodo") {
    contenido = <div className={REJILLA}>{nodo.reportes.map(tarjetaReporte)}</div>;
  } else if (!entradas.length) {
    contenido = <EstadoVacio icono={FileSpreadsheet} titulo="Sin reportes" />;
  } else {
    contenido = (
      <div className={REJILLA}>
        {entradas.map((e) => e.tipo === "reporte" ? tarjetaReporte(e.r)
          : <Tarjeta key={e.reportes[0].carpeta} href={`/reportes?grupo=${grupo}&carpeta=${encodeURIComponent(e.reportes[0].carpeta)}`} icono={Folder} titulo={`${e.orden} · ${e.titulo}`}
              pie={<><span>{e.reportes.length} reportes</span><ChevronRight className="size-4" /></>} />)}
      </div>
    );
  }

  return contenido;
}
