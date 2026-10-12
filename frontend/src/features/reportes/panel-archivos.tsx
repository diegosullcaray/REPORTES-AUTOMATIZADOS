"use client";

import { ChevronRight, Download, Eye, FileImage, FileSpreadsheet, FileText, File as FileIcon, RefreshCw } from "lucide-react";
import { useMemo, useState } from "react";
import { Chip, EsqueletoFilas, EstadoVacio, ErrorEnLinea, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Button, buttonVariants } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api, urlArchivo } from "@/lib/api";
import { ESTADO_EJECUCION, corteDe, enCurso, fecha, tamano } from "@/lib/formato";
import type { Archivo, Ejecucion } from "@/lib/tipos";
import { DialogoVistaPrevia, type ArchivoAbierto } from "./vista-previa";

const ICONOS = { excel: FileSpreadsheet, imagen: FileImage, texto: FileText, otro: FileIcon };
const HISTORIAL = 50;

interface Grupo {
  clave: string;
  ejecucion: Ejecucion | null; // null = archivos que ninguna ejecución registrada generó
  archivos: Archivo[];
}

/** Cada archivo aparece bajo la ejecución que lo generó; los que no pertenecen a ninguna van al final, en «Sin ejecución registrada». */
function agrupar(archivos: Archivo[], ejecuciones: Ejecucion[]): Grupo[] {
  const porNombre = new Map(archivos.map((a) => [a.nombre, a]));
  const usados = new Set<string>();
  const grupos: Grupo[] = [];
  for (const x of [...ejecuciones].sort((a, b) => b.inicio.localeCompare(a.inicio))) {
    const propios = x.archivos.flatMap((n) => porNombre.get(n) ?? []);
    propios.forEach((a) => usados.add(a.nombre));
    if (propios.length) grupos.push({ clave: x.id, ejecucion: x, archivos: propios });
  }
  const sueltos = archivos.filter((a) => !usados.has(a.nombre));
  if (sueltos.length) grupos.push({ clave: "sin-ejecucion", ejecucion: null, archivos: sueltos });
  return grupos;
}

function FilaArchivo({ reporte, a, onVer }: { reporte: string; a: Archivo; onVer: (a: ArchivoAbierto) => void }) {
  const Icono = ICONOS[a.tipo];
  return (
    <li className="flex flex-wrap items-center gap-3 px-4 py-3 transition-colors hover:bg-muted/40">
      <Icono className="size-5 shrink-0 text-muted-foreground" />
      <div className="flex min-w-0 flex-1 flex-col">
        <span className="truncate text-sm font-medium" title={a.nombre}>{a.nombre}</span>
        <span className="text-xs text-muted-foreground"><Hace iso={a.modificado} /> · {tamano(a.tamano)}</span>
      </div>
      <div className="flex gap-2">
        {a.tipo !== "otro" && <Button variant="outline" size="sm" onClick={() => onVer({ reporte, nombre: a.nombre, tipo: a.tipo })}><Eye /> Vista previa</Button>}
        <a href={urlArchivo(reporte, a.nombre)} className={buttonVariants({ variant: "ghost", size: "sm" })}><Download /> Descargar</a>
      </div>
    </li>
  );
}

function GrupoArchivos({ reporte, g, abierto, onAlternar, onVer }: { reporte: string; g: Grupo; abierto: boolean; onAlternar: () => void; onVer: (a: ArchivoAbierto) => void }) {
  const x = g.ejecucion;
  const estado = x && ESTADO_EJECUCION[x.estado];
  const corte = x && corteDe(x.argumentos);
  return (
    <li className="rounded-lg border">
      <button type="button" onClick={onAlternar} aria-expanded={abierto} className="flex w-full flex-wrap items-center gap-3 rounded-lg px-4 py-3 text-left transition-colors hover:bg-muted/40">
        <ChevronRight className={`size-4 shrink-0 text-muted-foreground transition-transform duration-150 ${abierto ? "rotate-90" : ""}`} />
        <div className="flex min-w-0 flex-1 flex-col">
          <span className="flex flex-wrap items-center gap-2 text-sm font-medium">
            {x ? <>Ejecución {x.inicio.slice(0, 16).replace("T", " ")}{estado && <Punto tono={estado.tono} etiqueta={estado.texto} latido={enCurso(x.estado)} />}</> : "Sin ejecución registrada"}
          </span>
          <span className="text-xs text-muted-foreground">
            {x ? <>{corte ? `Corte ${corte.length === 10 ? fecha(corte) : corte} · ` : ""}<Hace iso={x.inicio} /></> : "Archivos de la carpeta que no corresponden a una ejecución del historial."}
          </span>
        </div>
        <Chip tono="neutro">{g.archivos.length} archivo(s)</Chip>
      </button>
      {abierto && <ul className="divide-y border-t">{g.archivos.map((a) => <FilaArchivo key={a.nombre} reporte={reporte} a={a} onVer={onVer} />)}</ul>}
    </li>
  );
}

/** Archivos de la carpeta de salida agrupados por ejecución: se abre una ejecución para ver sus archivos. */
export function PanelArchivos({ reporte }: { reporte: string }) {
  const archivos = useConsulta(`archivos/${reporte}`, () => api.archivos(reporte));
  const historial = useConsulta(`ejecuciones/${reporte}/${HISTORIAL}`, () => api.ejecuciones(reporte, HISTORIAL));
  const [abierto, setAbierto] = useState<ArchivoAbierto | null>(null);
  const [alternados, setAlternados] = useState<Set<string>>(new Set());

  const datos = archivos.datos;
  const grupos = useMemo(() => (datos ? agrupar(datos, historial.datos ?? []) : []), [datos, historial.datos]);
  const recargar = () => { archivos.recargar(); historial.recargar(); };

  if (archivos.error) return <ErrorEnLinea titulo="No se pudieron listar los archivos" detalle={archivos.error} onReintentar={archivos.recargar} />;
  if ((archivos.cargando && !datos) || (historial.cargando && !historial.datos && !historial.error)) return <EsqueletoFilas filas={5} />;
  if (!datos?.length) return <EstadoVacio icono={FileSpreadsheet} titulo="Aún no hay archivos" descripcion="Cuando ejecutes el reporte, el Excel aparecerá aquí con su vista previa." />;

  // La ejecución más reciente llega abierta; el resto, cerrado. «Alternados» guarda lo que la persona invirtió.
  const estaAbierto = (i: number, clave: string) => (i === 0) !== alternados.has(clave);
  const alternar = (clave: string) => setAlternados((s) => { const n = new Set(s); if (n.has(clave)) n.delete(clave); else n.add(clave); return n; });

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{datos.length} archivo(s) en {grupos.length} {grupos.length === 1 ? "grupo" : "grupos"}, de la ejecución más reciente a la más antigua</span>
        <Button variant="outline" size="icon-sm" onClick={recargar} aria-label="Actualizar lista"><RefreshCw className={archivos.cargando ? "animate-spin" : ""} /></Button>
      </div>
      <ul className="flex flex-col gap-2">
        {grupos.map((g, i) => <GrupoArchivos key={g.clave} reporte={reporte} g={g} abierto={estaAbierto(i, g.clave)} onAlternar={() => alternar(g.clave)} onVer={setAbierto} />)}
      </ul>
      <DialogoVistaPrevia archivo={abierto} onCerrar={() => setAbierto(null)} />
    </div>
  );
}
