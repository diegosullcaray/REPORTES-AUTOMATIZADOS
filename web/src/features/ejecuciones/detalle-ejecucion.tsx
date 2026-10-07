"use client";

import { ArrowLeft, Copy, FileSpreadsheet, ScrollText } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { Aviso, Chip, EsqueletoFilas, ErrorEnLinea, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Terminal } from "@/components/terminal";
import { Button, buttonVariants } from "@/components/ui/button";
import { VistaPreviaArchivo } from "@/features/reportes/vista-previa";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, corteDe, duracion, enCurso, fecha, titulo } from "@/lib/formato";
import type { EjecucionDetalle, TipoArchivo } from "@/lib/tipos";

const SIGUIENTE: Partial<Record<EjecucionDetalle["estado"], string>> = {
  tablas_desactualizadas: "Faltan tablas al corte: en «Validación de tablas» del reporte tienes el mensaje para Producción. Cuando confirmen la carga, vuelve a verificar y ejecuta.",
  configuracion: "Revisa la fecha de corte, el .env o las confirmaciones pedidas (el log indica cuál).",
  error: "Revisa el log. Si es de conexión, prueba en Configuración › Bases de datos; si el Excel estaba abierto, ciérralo y repite.",
};

function tipoDe(nombre: string): TipoArchivo {
  const ext = nombre.split(".").pop()?.toLowerCase() ?? "";
  return ["xlsx", "xlsm"].includes(ext) ? "excel" : ["jpg", "jpeg", "png"].includes(ext) ? "imagen" : ["txt", "csv", "json"].includes(ext) ? "texto" : "otro";
}

function Dato({ etiqueta, children }: { etiqueta: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1 rounded-lg border p-3">
      <span className="text-[11px] tracking-wider text-muted-foreground uppercase">{etiqueta}</span>
      <span className="text-sm font-medium">{children}</span>
    </div>
  );
}

export function DetalleEjecucion({ id }: { id: string }) {
  const { datos: x, error, cargando, recargar } = useConsulta(`ejecucion/${id}`, () => api.ejecucion(id), (d) => enCurso(d.estado), 1500);
  const [archivo, setArchivo] = useState<string>();
  const comando = x && `python main.py ${x.argumentos.join(" ")}`;

  const acciones = x && (
    <>
      <Button variant="outline" size="sm" onClick={() => { navigator.clipboard.writeText(comando!); toast.success("Comando copiado"); }}><Copy /> Copiar comando</Button>
      <Link href={`/reportes/${x.reporte}`} className={buttonVariants({ variant: "outline", size: "sm" })}><ArrowLeft /> {titulo(x.reporte)}</Link>
    </>
  );

  return (
    <Pagina>
      <Marco icono={<ScrollText />} acciones={acciones}
        titulo={<span className="flex items-center gap-2">Ejecución {x && <Punto tono={ESTADO_EJECUCION[x.estado].tono} etiqueta={ESTADO_EJECUCION[x.estado].texto} latido={enCurso(x.estado)} />}</span>}
        descripcion={x ? titulo(x.reporte) : id}>
        {error ? (
          <ErrorEnLinea titulo="No se pudo cargar la ejecución" detalle={error} onReintentar={recargar} />
        ) : cargando && !x ? (
          <EsqueletoFilas filas={6} />
        ) : x && (
          <>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
              <Dato etiqueta="Estado"><Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip></Dato>
              <Dato etiqueta="Corte">{corteDe(x.argumentos) ? fecha(corteDe(x.argumentos)) : "—"}</Dato>
              <Dato etiqueta="Inicio"><Hace iso={x.inicio} /></Dato>
              <Dato etiqueta="Duración">{duracion(x.inicio, x.fin)}</Dato>
              <Dato etiqueta="Código de salida">{x.codigo ?? "—"}</Dato>
            </div>
            {SIGUIENTE[x.estado] && <Aviso tono={x.estado === "error" ? "peligro" : "aviso"}>{SIGUIENTE[x.estado]}</Aviso>}
            <Terminal titulo={comando!} texto={x.log} vacio={enCurso(x.estado) ? "Esperando salida…" : "(sin salida)"} />

            {x.archivos.length > 0 && (
              <section className="flex flex-col gap-3">
                <h2 className="flex items-center gap-2 text-sm font-medium"><FileSpreadsheet className="size-4 text-muted-foreground" /> Archivos generados</h2>
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
      </Marco>
    </Pagina>
  );
}
