"use client";

import { FileImage, FileSpreadsheet, FileText, File as FileIcon, RefreshCw } from "lucide-react";
import { useState } from "react";
import { EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { fecha, tamano } from "@/lib/formato";
import type { Archivo } from "@/lib/tipos";
import { VistaPreviaArchivo } from "./vista-previa";

const ICONOS = { excel: FileSpreadsheet, imagen: FileImage, texto: FileText, otro: FileIcon };

export function PanelArchivos({ reporte, inicial }: { reporte: string; inicial?: string }) {
  const { datos, error, cargando, recargar } = useConsulta(`archivos/${reporte}`, () => api.archivos(reporte));
  const [elegido, setElegido] = useState<string | undefined>(inicial);
  const actual: Archivo | undefined = datos?.find((a) => a.nombre === elegido) ?? datos?.[0];

  if (error) return <ErrorEnLinea titulo="No se pudieron listar los archivos" detalle={error} onReintentar={recargar} />;
  if (cargando && !datos) return <EsqueletoFilas filas={5} />;
  if (!datos?.length) return <EstadoVacio icono={FileSpreadsheet} titulo="Aún no hay archivos" descripcion="Cuando ejecutes el reporte, el Excel aparecerá aquí con su vista previa." />;

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(240px,320px)_1fr]">
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-[12px] text-[var(--mis-text-tertiary)]">{datos.length} archivo(s) en la carpeta del reporte</span>
          <Button variant="ghost" size="icon-sm" onClick={recargar} aria-label="Actualizar lista"><RefreshCw /></Button>
        </div>
        <ul className="flex max-h-[30vh] flex-col gap-1 overflow-auto lg:max-h-[65vh]">
          {datos.map((a) => {
            const Icono = ICONOS[a.tipo];
            const activo = a.nombre === actual?.nombre;
            return (
              <li key={a.nombre}>
                <button onClick={() => setElegido(a.nombre)} aria-pressed={activo}
                  className="flex w-full items-center gap-2 rounded-[var(--mis-radius-sm)] px-2 py-1.5 text-left transition-colors duration-150 hover:bg-[var(--mis-hover-bg)]"
                  style={activo ? { background: "var(--mis-primary-light)" } : undefined}>
                  <Icono className="size-4 shrink-0 text-[var(--mis-primary-text)]" />
                  <span className="flex min-w-0 flex-col">
                    <span className="truncate text-[13px]">{a.nombre}</span>
                    <span className="text-[11px] text-[var(--mis-text-tertiary)]">{fecha(a.modificado)} · {tamano(a.tamano)}</span>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
      {actual && <VistaPreviaArchivo key={actual.nombre} reporte={reporte} archivo={actual.nombre} tipo={actual.tipo} />}
    </div>
  );
}
