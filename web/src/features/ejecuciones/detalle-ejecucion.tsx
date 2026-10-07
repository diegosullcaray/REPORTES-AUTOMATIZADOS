"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Aviso, Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { buttonVariants } from "@/components/ui/button";
import { Ventana } from "@/components/ventana";
import { VistaPreviaArchivo } from "@/features/reportes/vista-previa";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, duracion, enCurso, fecha } from "@/lib/formato";
import type { EjecucionDetalle, TipoArchivo } from "@/lib/tipos";

const SIGUIENTE: Partial<Record<EjecucionDetalle["estado"], string>> = {
  tablas_desactualizadas: "Faltan tablas al corte: en el paso «Validar» del reporte tienes el mensaje para Producción. Cuando confirmen la carga, vuelve a verificar y ejecuta.",
  configuracion: "Revisa la fecha de corte, el .env o las confirmaciones pedidas (el log indica cuál).",
  error: "Revisa el log. Si es de conexión, prueba la sección Conexiones; si el Excel estaba abierto, ciérralo y repite.",
};

function tipoDe(nombre: string): TipoArchivo {
  const ext = nombre.split(".").pop()?.toLowerCase() ?? "";
  return ["xlsx", "xlsm"].includes(ext) ? "excel" : ["jpg", "jpeg", "png"].includes(ext) ? "imagen" : ["txt", "csv", "json"].includes(ext) ? "texto" : "otro";
}

export function DetalleEjecucion({ id }: { id: string }) {
  const { datos: x, error, cargando, recargar } = useConsulta(`ejecucion/${id}`, () => api.ejecucion(id), (d) => enCurso(d.estado), 1500);
  const [archivo, setArchivo] = useState<string>();
  const log = useRef<HTMLPreElement>(null);

  useEffect(() => {
    if (log.current) log.current.scrollTop = log.current.scrollHeight;
  }, [x?.log]);

  const volver = (
    <Link href={x ? `/reportes/${x.reporte}` : "/ejecuciones"} className={buttonVariants({ variant: "ghost", size: "sm" })}>
      <ArrowLeft /> {x ? x.reporte : "Ejecuciones"}
    </Link>
  );

  return (
    <Ventana titulo={x ? `Ejecución · ${x.reporte}` : "Ejecución"} acciones={volver}>
      {error ? (
        <ErrorEnLinea titulo="No se pudo cargar la ejecución" detalle={error} onReintentar={recargar} />
      ) : cargando && !x ? (
        <EsqueletoFilas filas={6} />
      ) : x && (
        <>
          <div className="flex flex-wrap items-center gap-2 text-[13px]">
            <Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip>
            <span className="text-[var(--mis-text-secondary)]">Inicio {fecha(x.inicio)} · Duración {duracion(x.inicio, x.fin)}{x.codigo !== null && ` · código ${x.codigo}`}</span>
          </div>
          <code className="mis-superficie block overflow-x-auto p-2 font-mono text-[12px]">python main.py {x.argumentos.join(" ")}</code>
          {SIGUIENTE[x.estado] && <Aviso tono={x.estado === "error" ? "peligro" : "aviso"}>{SIGUIENTE[x.estado]}</Aviso>}

          <section className="flex flex-col gap-2">
            <h2 className="text-[15px] font-semibold">Salida</h2>
            <pre ref={log} aria-live="polite" className="mis-superficie max-h-[45vh] overflow-auto p-3 font-mono text-[12px] whitespace-pre-wrap">
              {x.log || (enCurso(x.estado) ? "Esperando salida…" : "(sin salida)")}
            </pre>
          </section>

          {x.archivos.length > 0 && (
            <section className="flex flex-col gap-2">
              <h2 className="text-[15px] font-semibold">Archivos generados</h2>
              <div className="flex flex-wrap gap-2">
                {x.archivos.map((a) => (
                  <button key={a} onClick={() => setArchivo(a)} aria-pressed={archivo === a}
                    className={buttonVariants({ variant: archivo === a ? "secondary" : "outline", size: "sm" })}>{a}</button>
                ))}
              </div>
              {archivo && <VistaPreviaArchivo key={archivo} reporte={x.reporte} archivo={archivo} tipo={tipoDe(archivo)} />}
            </section>
          )}
        </>
      )}
    </Ventana>
  );
}
