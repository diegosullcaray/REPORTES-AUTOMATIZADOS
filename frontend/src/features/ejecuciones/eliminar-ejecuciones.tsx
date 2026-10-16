"use client";

import { ScrollText, Trash2 } from "lucide-react";
import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import { Chip } from "@/components/estados";
import { Confirmar } from "@/components/confirmar";
import { Hace } from "@/components/hace";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, enCurso } from "@/lib/formato";
import type { Ejecucion } from "@/lib/tipos";

/** Botón de papelera con confirmación: quita del historial las ejecuciones `ids` (estado y log). No borra los archivos generados. */
export function BotonEliminar({ ids, descripcion, onHecho, deshabilitado, etiqueta = "Eliminar" }: {
  ids: string[]; descripcion: ReactNode; onHecho: () => void; deshabilitado?: string | false; etiqueta?: string;
}) {
  const [abierto, setAbierto] = useState(false);
  const [ocupado, setOcupado] = useState(false);

  async function eliminar() {
    setOcupado(true);
    try {
      const r = await api.eliminarEjecuciones(ids);
      toast.success(r.eliminadas === 1 ? "Ejecución eliminada" : `${r.eliminadas} ejecuciones eliminadas`);
      setAbierto(false);
    } catch (e) {
      toast.error("No se eliminó", { description: (e as Error).message });
    } finally {
      setOcupado(false);
      onHecho(); // también si falló: la lista pudo cambiar (p. ej. ya no existía)
    }
  }

  return (
    <>
      <Button type="button" variant="ghost" size="icon-sm" aria-label={etiqueta} title={deshabilitado || etiqueta} disabled={!!deshabilitado}
        onClick={() => setAbierto(true)}><Trash2 className="text-[var(--mis-danger)]" /></Button>
      <Confirmar abierto={abierto} onAbierto={setAbierto} titulo={etiqueta} accion={ocupado ? "Eliminando…" : "Eliminar"} peligro deshabilitado={ocupado}
        descripcion={<>{descripcion} Se quitan del historial y su log; los archivos generados no se borran.</>} onConfirmar={() => void eliminar()} />
    </>
  );
}

/** Todas las ejecuciones de un proceso, una por fila (las repetidas o las que salieron mal), cada una con su log y su papelera. */
export function ListaIntentos({ ejecuciones, onVerLog, onCambio }: { ejecuciones: Ejecucion[]; onVerLog: (id: string) => void; onCambio: () => void }) {
  return (
    <ul className="flex flex-col divide-y rounded-lg border">
      {ejecuciones.map((x) => {
        const estado = ESTADO_EJECUCION[x.estado];
        return (
          <li key={x.id} className="flex flex-wrap items-center gap-2 px-3 py-2 text-xs">
            <Chip tono={estado.tono}>{estado.texto}</Chip>
            <span className="text-muted-foreground"><Hace iso={x.inicio} /></span>
            <code className="min-w-0 flex-1 truncate text-muted-foreground" title={x.argumentos.join(" ")}>{x.argumentos.slice(1).join(" ") || "sin argumentos"}</code>
            <Button variant="ghost" size="sm" onClick={() => onVerLog(x.id)}><ScrollText /> Ver log</Button>
            <BotonEliminar ids={[x.id]} onHecho={onCambio} deshabilitado={enCurso(x.estado) && "En curso: espera a que termine"} etiqueta="Eliminar ejecución"
              descripcion={<>Se eliminará esta ejecución ({estado.texto.toLowerCase()}).</>} />
          </li>
        );
      })}
    </ul>
  );
}
