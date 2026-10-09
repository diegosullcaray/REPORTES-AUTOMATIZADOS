"use client";

import { Download } from "lucide-react";
import { useState } from "react";
import { EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { buttonVariants } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConsulta } from "@/hooks/use-consulta";
import { api, urlArchivo } from "@/lib/api";
import { titulo } from "@/lib/formato";
import type { Celda, HojaPrevia, TipoArchivo } from "@/lib/tipos";

const numero = new Intl.NumberFormat("es-PE", { maximumFractionDigits: 2 });

function Hoja({ hoja }: { hoja: HojaPrevia }) {
  if (hoja.filas.length === 0) return <EstadoVacio titulo="Hoja vacía" descripcion="Esta hoja no tiene filas de datos." />;
  return (
    <div className="flex flex-col gap-2">
      <p className="text-[12px] text-[var(--mis-text-tertiary)]">
        {hoja.filas.length < hoja.total_filas ? `Mostrando las primeras ${hoja.filas.length} de ${numero.format(hoja.total_filas)} filas. Descarga el Excel para verlas todas.` : `${hoja.total_filas} filas.`}
      </p>
      <div className="rounded-lg border bg-card max-h-[60vh] overflow-auto">
        <table className="w-full [&_tbody_tr:hover]:bg-muted/50 border-collapse text-[12px]">
          <thead className="sticky top-0 z-10" style={{ background: "var(--mis-ranking-header-bg)", color: "var(--mis-text-on-primary)" }}>
            <tr>{hoja.columnas.map((c, i) => <th key={i} className="px-2 py-1.5 text-left font-semibold whitespace-nowrap">{c}</th>)}</tr>
          </thead>
          <tbody>
            {hoja.filas.map((fila, i) => (
              <tr key={i} className="border-t border-[var(--mis-border)]">
                {fila.map((v: Celda, j) => (
                  <td key={j} className={`px-2 py-1 whitespace-nowrap ${typeof v === "number" ? "text-right tabular-nums" : ""}`}>
                    {v === null ? "" : typeof v === "number" ? numero.format(v) : v}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function VistaDatos({ reporte, archivo }: { reporte: string; archivo: string }) {
  const { datos, error, cargando, recargar } = useConsulta(`${reporte}/${archivo}`, () => api.vistaPrevia(reporte, archivo));
  const [hoja, setHoja] = useState(0);
  if (error) return <ErrorEnLinea titulo="No se pudo abrir la vista previa" detalle={error} onReintentar={recargar} />;
  if (cargando && !datos) return <EsqueletoFilas filas={8} alto="h-7" />;
  if (!datos) return null;
  if (datos.tipo === "texto") return <pre className="rounded-lg border bg-card max-h-[60vh] overflow-auto p-3 font-mono text-[12px] whitespace-pre-wrap">{datos.texto}</pre>;
  if (datos.hojas.length === 0) return <EstadoVacio titulo="Libro sin hojas" />;
  return (
    <div className="flex flex-col gap-3">
      {datos.hojas.length > 1 && (
        <Tabs value={String(hoja)} onValueChange={(v) => setHoja(Number(v))}>
          <TabsList variant="line" className="overflow-x-auto w-full justify-start">
            {datos.hojas.map((h, i) => <TabsTrigger key={h.nombre} value={String(i)} className="flex-none">{h.nombre}</TabsTrigger>)}
          </TabsList>
        </Tabs>
      )}
      <Hoja hoja={datos.hojas[Math.min(hoja, datos.hojas.length - 1)]} />
    </div>
  );
}

export interface ArchivoAbierto {
  reporte: string;
  nombre: string;
  tipo: TipoArchivo;
}

/** Vista previa de un archivo generado en un diálogo amplio: tabla para Excel, imagen, texto plano. */
export function DialogoVistaPrevia({ archivo, onCerrar }: { archivo: ArchivoAbierto | null; onCerrar: () => void }) {
  return (
    <Dialog open={!!archivo} onOpenChange={(abierto) => !abierto && onCerrar()}>
      <DialogContent className="flex max-h-[90vh] flex-col sm:max-w-6xl">
        {archivo && (
          <>
            <DialogHeader className="flex-row items-center justify-between gap-3 pr-8">
              <div className="flex min-w-0 flex-col gap-1">
                <DialogTitle className="truncate">{archivo.nombre}</DialogTitle>
                <DialogDescription>Vista previa · {titulo(archivo.reporte)}</DialogDescription>
              </div>
              <a href={urlArchivo(archivo.reporte, archivo.nombre)} className={buttonVariants({ variant: "outline", size: "sm" })}>
                <Download /> Descargar
              </a>
            </DialogHeader>
            <div className="min-h-0 overflow-auto">
              {archivo.tipo === "imagen" ? (
                // eslint-disable-next-line @next/next/no-img-element -- archivo local servido por la API, no optimizable
                <img src={urlArchivo(archivo.reporte, archivo.nombre, true)} alt={`Vista previa de ${archivo.nombre}`} className="mx-auto max-w-full rounded-lg border" />
              ) : archivo.tipo === "otro" ? (
                <EstadoVacio titulo="Sin vista previa" descripcion="Este tipo de archivo solo se puede descargar." />
              ) : (
                <VistaDatos key={archivo.nombre} reporte={archivo.reporte} archivo={archivo.nombre} />
              )}
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
