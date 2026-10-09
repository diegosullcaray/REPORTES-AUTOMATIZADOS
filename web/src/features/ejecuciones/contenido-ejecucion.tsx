"use client";

import { Copy, Eye, FileSpreadsheet } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Aviso, Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Terminal } from "@/components/terminal";
import { Button } from "@/components/ui/button";
import { DialogoVistaPrevia, type ArchivoAbierto } from "@/features/reportes/vista-previa";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, corteDe, duracion, enCurso, fecha } from "@/lib/formato";
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

/** Detalle de una ejecución: datos, log en vivo y archivos generados. Sirve tanto en el diálogo como en la página. */
export function ContenidoEjecucion({ id }: { id: string }) {
  const { datos: x, error, cargando, recargar } = useConsulta(`ejecucion/${id}`, () => api.ejecucion(id), (d) => enCurso(d.estado), 1500);
  const [abierto, setAbierto] = useState<ArchivoAbierto | null>(null);

  if (error) return <ErrorEnLinea titulo="No se pudo cargar la ejecución" detalle={error} onReintentar={recargar} />;
  if (cargando && !x) return <EsqueletoFilas filas={6} />;
  if (!x) return null;

  const comando = `python main.py ${x.argumentos.join(" ")}`;
  const corte = corteDe(x.argumentos);
  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Dato etiqueta="Estado"><Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip></Dato>
        <Dato etiqueta="Corte">{corte ? fecha(corte) : "—"}</Dato>
        <Dato etiqueta="Inicio"><Hace iso={x.inicio} /></Dato>
        <Dato etiqueta="Duración">{duracion(x.inicio, x.fin)}</Dato>
        <Dato etiqueta="Código de salida">{x.codigo ?? "—"}</Dato>
      </div>
      {SIGUIENTE[x.estado] && <Aviso tono={x.estado === "error" ? "peligro" : "aviso"}>{SIGUIENTE[x.estado]}</Aviso>}
      <Terminal titulo={comando} texto={x.log} vacio={enCurso(x.estado) ? "Esperando salida…" : "(sin salida)"}
        estado={<Button variant="ghost" size="icon-sm" aria-label="Copiar comando" onClick={() => { navigator.clipboard.writeText(comando); toast.success("Comando copiado"); }}><Copy /></Button>} />

      {x.archivos.length > 0 && (
        <section className="flex flex-col gap-2">
          <h3 className="flex items-center gap-2 text-sm font-medium"><FileSpreadsheet className="size-4 text-muted-foreground" /> Archivos generados</h3>
          <ul className="divide-y rounded-lg border">
            {x.archivos.map((a) => (
              <li key={a} className="flex items-center justify-between gap-3 px-3 py-2">
                <span className="truncate text-sm" title={a}>{a}</span>
                {tipoDe(a) !== "otro" && <Button variant="outline" size="sm" onClick={() => setAbierto({ reporte: x.reporte, nombre: a, tipo: tipoDe(a) })}><Eye /> Vista previa</Button>}
              </li>
            ))}
          </ul>
        </section>
      )}
      <DialogoVistaPrevia archivo={abierto} onCerrar={() => setAbierto(null)} />
    </div>
  );
}
