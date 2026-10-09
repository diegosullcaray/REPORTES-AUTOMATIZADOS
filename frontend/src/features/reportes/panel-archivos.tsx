"use client";

import { Download, Eye, FileImage, FileSpreadsheet, FileText, File as FileIcon, RefreshCw } from "lucide-react";
import { useState } from "react";
import { EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Button, buttonVariants } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api, urlArchivo } from "@/lib/api";
import { tamano } from "@/lib/formato";
import { DialogoVistaPrevia, type ArchivoAbierto } from "./vista-previa";

const ICONOS = { excel: FileSpreadsheet, imagen: FileImage, texto: FileText, otro: FileIcon };

/** Archivos de la carpeta de salida en una sola lista; la vista previa se abre en un diálogo. */
export function PanelArchivos({ reporte }: { reporte: string }) {
  const { datos, error, cargando, recargar } = useConsulta(`archivos/${reporte}`, () => api.archivos(reporte));
  const [abierto, setAbierto] = useState<ArchivoAbierto | null>(null);

  if (error) return <ErrorEnLinea titulo="No se pudieron listar los archivos" detalle={error} onReintentar={recargar} />;
  if (cargando && !datos) return <EsqueletoFilas filas={5} />;
  if (!datos?.length) return <EstadoVacio icono={FileSpreadsheet} titulo="Aún no hay archivos" descripcion="Cuando ejecutes el reporte, el Excel aparecerá aquí con su vista previa." />;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{datos.length} archivo(s), del más reciente al más antiguo</span>
        <Button variant="outline" size="icon-sm" onClick={recargar} aria-label="Actualizar lista"><RefreshCw className={cargando ? "animate-spin" : ""} /></Button>
      </div>
      <ul className="divide-y rounded-lg border">
        {datos.map((a) => {
          const Icono = ICONOS[a.tipo];
          return (
            <li key={a.nombre} className="flex flex-wrap items-center gap-3 px-4 py-3 transition-colors hover:bg-muted/40">
              <Icono className="size-5 shrink-0 text-muted-foreground" />
              <div className="flex min-w-0 flex-1 flex-col">
                <span className="truncate text-sm font-medium" title={a.nombre}>{a.nombre}</span>
                <span className="text-xs text-muted-foreground"><Hace iso={a.modificado} /> · {tamano(a.tamano)}</span>
              </div>
              <div className="flex gap-2">
                {a.tipo !== "otro" && (
                  <Button variant="outline" size="sm" onClick={() => setAbierto({ reporte, nombre: a.nombre, tipo: a.tipo })}><Eye /> Vista previa</Button>
                )}
                <a href={urlArchivo(reporte, a.nombre)} className={buttonVariants({ variant: "ghost", size: "sm" })}><Download /> Descargar</a>
              </div>
            </li>
          );
        })}
      </ul>
      <DialogoVistaPrevia archivo={abierto} onCerrar={() => setAbierto(null)} />
    </div>
  );
}
