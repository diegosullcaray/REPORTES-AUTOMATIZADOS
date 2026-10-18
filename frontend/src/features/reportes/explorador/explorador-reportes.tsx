"use client";

import { CalendarDays, ChevronRight, Database, FileSpreadsheet, Folder, Mail, Server, UserRound } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useMemo, type ReactNode } from "react";
import { ErrorEnLinea, EsqueletoFilas, EstadoVacio, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { REJILLA_TARJETAS as REJILLA, Tarjeta } from "@/components/tarjeta-enlace";
import { useConsulta, type Consulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { EtiquetaBadge } from "@/features/etiquetas/etiquetas";
import { MenuGrupo } from "./menu-grupo";
import { MenuReporte } from "./menu-reporte";
import { ESTADO_EJECUCION, agruparPorCarpeta, enCurso, titulo } from "@/lib/formato";
import type { Ejecucion, Grupo, GrupoReportes, ReporteResumen } from "@/lib/tipos";

const ICONO_GRUPO: Record<string, LucideIcon> = { diarias: CalendarDays, piero: UserRound, erick: UserRound };

/** Reportes en tarjetas por niveles (como proyectos → servicios de Dokploy): grupo → carpeta del legado → reporte. El nivel va en la URL. */
export function ExploradorReportes({ reportes, grupos }: { reportes: Consulta<ReporteResumen[]>; grupos: Consulta<GrupoReportes[]> }) {
  const ejecuciones = useConsulta("ejecuciones/catalogo", () => api.ejecuciones(undefined, 500), () => true, 10000);
  const params = useSearchParams();
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
  const delGrupo = grupo && grupos.datos?.some((g) => g.id === grupo) ? todos.filter((r) => r.grupo === grupo) : [];

  const tarjetaReporte = (r: ReporteResumen) => {
    const x = ultima.get(r.nombre);
    const e = x && ESTADO_EJECUCION[x.estado];
    return (
      <Tarjeta key={r.nombre} href={`/reportes/${r.nombre}`} icono={FileSpreadsheet} titulo={`${r.orden} · ${titulo(r.nombre)}`} descripcion={r.descripcion} acciones={<MenuReporte nombre={r.nombre} />}
        estado={<Punto tono={e?.tono ?? "neutro"} etiqueta={e?.texto ?? "Sin ejecutar"} latido={!!x && enCurso(x.estado)} />}
        pie={<>
          <span className="flex items-center gap-1.5"><Server className="size-3" />{r.servidores.join(", ")}{r.escribe_en_bd && <Database aria-label="escribe en BD" className="size-3 text-[var(--mis-warning)]" />}{r.envia_correo && <Mail aria-label="envía correo" className="size-3" />}</span>
          <span>{x ? <Hace iso={x.inicio} /> : "Sin ejecutar"}</span>
        </>} />
    );
  };

  const entradas = grupo ? agruparPorCarpeta(delGrupo) : [];
  const nodo = carpeta ? entradas.find((e) => e.tipo === "nodo" && e.reportes[0].carpeta === carpeta) : undefined;

  let contenido: ReactNode;
  if (!grupo) {
    contenido = (
      <div className={REJILLA}>
        {(grupos.datos ?? []).map((g) => (
          <Tarjeta key={g.id} href={`/reportes?grupo=${g.id}`} icono={ICONO_GRUPO[g.id] ?? Folder} titulo={g.nombre} acciones={<MenuGrupo g={g} onCambio={grupos.recargar} />}
            etiquetas={g.etiquetas.length ? g.etiquetas.map((e) => <EtiquetaBadge key={e.id} e={e} />) : undefined}
            pie={<><span>{g.reportes} {g.reportes === 1 ? "reporte" : "reportes"}</span><ChevronRight className="size-4" /></>} />
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
