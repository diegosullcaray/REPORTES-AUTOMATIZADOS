"use client";

import { Clock, Rocket, ScrollText } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { Chip, EsqueletoFilas, ErrorEnLinea, EstadoVacio, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Tarjeta } from "@/components/tarjeta";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, corteDe, duracion, enCurso, fecha } from "@/lib/formato";
import { VisorLog } from "./visor-log";

const OPCIONES: Record<string, string> = { "--forzar": "forzado", "--confirmar-escritura": "escribe en BD", "--conforme": "correo a todos" };

/** Ejecuciones de un reporte como lista de tarjetas (como «Deployments» de un servicio en Dokploy). */
export function ListaEjecuciones({ reporte, limite = 20 }: { reporte: string; limite?: number }) {
  const { datos, error, cargando, recargar } = useConsulta(`ejecuciones/${reporte}/${limite}`, () => api.ejecuciones(reporte, limite), () => true, 5000);
  const [log, setLog] = useState<string | null>(null);

  return (
    <Tarjeta titulo="Ejecuciones" descripcion={`Las últimas ${limite} ejecuciones de este reporte; se actualiza sola.`}
      acciones={<Link href="/ejecuciones" className={buttonVariants({ variant: "outline", size: "sm" })}>Ver todas</Link>}>
      {error ? <ErrorEnLinea titulo="No se pudo cargar el historial" detalle={error} onReintentar={recargar} />
        : cargando && !datos ? <EsqueletoFilas filas={4} alto="h-20" />
        : !datos?.length ? <EstadoVacio icono={Rocket} titulo="Sin ejecuciones" descripcion="Ejecuta el reporte desde la pestaña General." />
        : (
          <ol className="flex flex-col gap-3">
            {datos.map((x, i) => {
              const e = ESTADO_EJECUCION[x.estado];
              const corte = corteDe(x.argumentos);
              const opciones = x.argumentos.filter((a) => OPCIONES[a]);
              return (
                <li key={x.id} className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 flex-col gap-1">
                    <span className="flex items-center gap-3 font-medium">
                      {i + 1}. {e.texto}
                      <Punto tono={e.tono} etiqueta={e.texto} latido={enCurso(x.estado)} />
                    </span>
                    <span className="text-sm text-muted-foreground">
                      Corte {corte ? (corte.length === 10 ? fecha(corte) : corte) : "—"}
                      {x.archivos.length > 0 && ` · ${x.archivos.length} archivo(s)`}
                    </span>
                    {opciones.length > 0 && <span className="flex flex-wrap gap-1">{opciones.map((a) => <Chip key={a} tono="aviso">{OPCIONES[a]}</Chip>)}</span>}
                  </div>
                  <div className="flex flex-col items-start gap-2 sm:items-end">
                    <span className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                      <Hace iso={x.inicio} />
                      {x.fin && <Badge variant="outline" className="gap-1 text-[10px]"><Clock className="size-3" />{duracion(x.inicio, x.fin)}</Badge>}
                    </span>
                    <span className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => setLog(x.id)}><ScrollText /> Ver detalle</Button>
                    </span>
                  </div>
                </li>
              );
            })}
          </ol>
        )}
      <VisorLog id={log} onCerrar={() => setLog(null)} />
    </Tarjeta>
  );
}
