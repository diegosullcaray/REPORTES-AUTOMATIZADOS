"use client";

import { Tag, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { Etiqueta } from "@/lib/tipos";
import { BotonEtiqueta, EtiquetaBadge } from "./etiquetas";

/** Etiquetas (página «Tags» de Settings en Dokploy): se crean aquí o desde el selector al crear un grupo. */
export function PanelEtiquetas() {
  const { datos, error, cargando, recargar } = useConsulta("etiquetas", api.etiquetas);
  const [borrando, setBorrando] = useState<Etiqueta | null>(null);

  async function eliminar(e: Etiqueta) {
    try {
      await api.eliminarEtiqueta(e.id);
      toast.success("Etiqueta eliminada");
      recargar();
    } catch (err) {
      toast.error("No se pudo eliminar", { description: (err as Error).message });
    }
  }

  return (
    <Pagina>
      <Marco icono={<Tag />} titulo="Etiquetas" descripcion="Crea etiquetas para organizar los grupos de reportes."
        acciones={datos && datos.length > 0 && <BotonEtiqueta onGuardada={recargar} />}>
        {error ? <ErrorEnLinea titulo="No se pudieron leer las etiquetas" detalle={error} onReintentar={recargar} />
          : cargando && !datos ? <EsqueletoFilas filas={3} alto="h-14" />
          : datos && (datos.length === 0
            ? <EstadoVacio icono={Tag} titulo="Aún no hay etiquetas" descripcion="Crea tu primera etiqueta para empezar a organizar los grupos." accion={<BotonEtiqueta onGuardada={recargar} />} />
            : <div className="flex flex-col gap-3">
                {datos.map((e) => (
                  <div key={e.id} className="flex items-center justify-between rounded-lg border p-3.5">
                    <EtiquetaBadge e={e} />
                    <div className="flex items-center gap-1">
                      <BotonEtiqueta etiqueta={e} onGuardada={recargar} />
                      <Button variant="ghost" size="icon" aria-label={`Eliminar ${e.nombre}`} onClick={() => setBorrando(e)}><Trash2 className="size-4" /></Button>
                    </div>
                  </div>
                ))}
              </div>)}
      </Marco>
      <Confirmar abierto={!!borrando} onAbierto={(a) => !a && setBorrando(null)} titulo="Eliminar etiqueta" accion="Eliminar" peligro
        descripcion={`Se quita la etiqueta «${borrando?.nombre}» de todos los grupos. Esta acción no se puede deshacer.`}
        onConfirmar={() => { const e = borrando; setBorrando(null); if (e) void eliminar(e); }} />
    </Pagina>
  );
}
