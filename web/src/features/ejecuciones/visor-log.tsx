"use client";

import { Chip } from "@/components/estados";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, enCurso, titulo } from "@/lib/formato";
import { ContenidoEjecucion } from "./contenido-ejecucion";

/** Detalle de una ejecución (datos, log en vivo y archivos) en un diálogo, como el de un deployment en Dokploy. */
export function VisorLog({ id, onCerrar }: { id: string | null; onCerrar: () => void }) {
  const { datos: x } = useConsulta(id && `ejecucion/${id}`, () => api.ejecucion(id!), (d) => enCurso(d.estado), 1500);
  return (
    <Dialog open={!!id} onOpenChange={(abierto) => !abierto && onCerrar()}>
      <DialogContent className="flex max-h-[90vh] flex-col sm:max-w-5xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {x ? titulo(x.reporte) : "Ejecución"}
            {x && <Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip>}
          </DialogTitle>
          <DialogDescription>Detalle, log y archivos de la ejecución.</DialogDescription>
        </DialogHeader>
        <div className="min-h-0 overflow-auto">{id && <ContenidoEjecucion id={id} />}</div>
      </DialogContent>
    </Dialog>
  );
}
