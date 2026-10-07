"use client";

import { History } from "lucide-react";
import Link from "next/link";
import { Chip, EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, duracion, enCurso, fecha } from "@/lib/formato";

/** Historial de ejecuciones (todas o de un reporte). Se refresca solo mientras alguna está en curso. */
export function TablaEjecuciones({ reporte }: { reporte?: string }) {
  const { datos, error, cargando, recargar } = useConsulta(`ejecuciones/${reporte ?? ""}`, () => api.ejecuciones(reporte), (d) => d.some((x) => enCurso(x.estado)));

  if (error) return <ErrorEnLinea titulo="No se pudo cargar el historial" detalle={error} onReintentar={recargar} />;
  if (cargando && !datos) return <EsqueletoFilas filas={6} />;
  if (!datos?.length) return <EstadoVacio icono={History} titulo="Sin ejecuciones" descripcion="Aquí aparecerá cada reporte que ejecutes desde la web." />;

  return (
    <div className="mis-superficie overflow-x-auto">
      <table className="mis-tabla w-full text-[13px]">
        <thead className="text-left text-[12px] text-[var(--mis-text-secondary)]">
          <tr>
            <th className="p-2">Estado</th>
            {!reporte && <th className="p-2">Reporte</th>}
            <th className="p-2">Inicio</th><th className="p-2">Duración</th><th className="p-2">Argumentos</th><th className="p-2">Archivos</th>
          </tr>
        </thead>
        <tbody>
          {datos.map((x) => {
            const e = ESTADO_EJECUCION[x.estado];
            return (
              <tr key={x.id} className="border-t border-[var(--mis-border)]">
                <td className="p-2"><Link href={`/ejecuciones/${x.id}`} className="outline-none focus-visible:underline"><Chip tono={e.tono}>{e.texto}</Chip></Link></td>
                {!reporte && <td className="p-2"><Link href={`/reportes/${x.reporte}`} className="font-medium text-[var(--mis-primary-text)] hover:underline">{x.reporte}</Link></td>}
                <td className="p-2 whitespace-nowrap"><Link href={`/ejecuciones/${x.id}`} className="hover:underline">{fecha(x.inicio)}</Link></td>
                <td className="p-2 whitespace-nowrap">{duracion(x.inicio, x.fin)}</td>
                <td className="p-2 font-mono text-[11px] text-[var(--mis-text-secondary)]">{x.argumentos.slice(1).join(" ")}</td>
                <td className="p-2">{x.archivos.length || "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
