"use client";

import { AlertTriangle, MoreHorizontal, Tag, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Aviso } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { SelectorEtiquetas } from "@/features/etiquetas/etiquetas";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { GrupoReportes } from "@/lib/tipos";

/** Etiquetas del grupo en un diálogo (como el `TagSelector` del formulario de proyecto de Dokploy). */
function DialogoEtiquetas({ g, onCerrar, onCambio }: { g: GrupoReportes; onCerrar: () => void; onCambio: () => void }) {
  const etiquetas = useConsulta("etiquetas", api.etiquetas);
  const [elegidas, setElegidas] = useState(g.etiquetas.map((e) => e.id));
  const [ocupado, setOcupado] = useState(false);

  async function guardar() {
    setOcupado(true);
    try {
      await api.etiquetasDeGrupo(g.id, elegidas);
      toast.success("Etiquetas guardadas");
      onCambio();
      onCerrar();
    } catch (e) {
      toast.error("No se guardaron", { description: (e as Error).message });
      setOcupado(false);
    }
  }

  return (
    <Dialog open onOpenChange={(a) => !a && onCerrar()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Etiquetas de {g.nombre}</DialogTitle>
          <DialogDescription>Organiza este grupo con etiquetas; se gestionan en Configuración › Etiquetas.</DialogDescription>
        </DialogHeader>
        <SelectorEtiquetas etiquetas={etiquetas.datos ?? []} elegidas={elegidas} onCambio={setElegidas} onCreada={etiquetas.recargar} />
        <DialogFooter><Button disabled={ocupado} onClick={() => void guardar()}>{ocupado ? "Guardando…" : "Guardar"}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/**
 * Menú «⋯» de la tarjeta de un grupo, como el de los proyectos de Dokploy: etiquetas y, en los grupos creados desde la web,
 * eliminar con confirmación (aviso y botón deshabilitado mientras el grupo tenga reportes).
 */
export function MenuGrupo({ g, onCambio }: { g: GrupoReportes; onCambio: () => void }) {
  const [confirmar, setConfirmar] = useState(false);
  const [etiquetas, setEtiquetas] = useState(false);
  const vacio = g.reportes === 0;

  async function eliminar() {
    try {
      await api.eliminarGrupo(g.id);
      toast.success("Grupo eliminado");
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- recarga completa a propósito: el sidebar vuelve a leer los grupos
      window.location.href = "/reportes";
    } catch (e) {
      toast.error("No se pudo eliminar", { description: (e as Error).message });
    }
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="px-2" aria-label={`Acciones de ${g.nombre}`} />}>
          <MoreHorizontal className="size-5" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-[200px]">
          <DropdownMenuGroup>
            <DropdownMenuLabel className="font-normal">Acciones</DropdownMenuLabel>
          </DropdownMenuGroup>
          <DropdownMenuItem className="cursor-pointer gap-3" onClick={() => setEtiquetas(true)}><Tag className="size-4" /> Etiquetas</DropdownMenuItem>
          {g.propio && <DropdownMenuItem className="cursor-pointer gap-3" onClick={() => setConfirmar(true)}><Trash2 className="size-4" /> Eliminar</DropdownMenuItem>}
        </DropdownMenuContent>
      </DropdownMenu>
      {etiquetas && <DialogoEtiquetas g={g} onCerrar={() => setEtiquetas(false)} onCambio={onCambio} />}
      <Confirmar abierto={confirmar} onAbierto={setConfirmar} titulo="¿Seguro que quieres eliminar este grupo?" accion="Eliminar" peligro deshabilitado={!vacio}
        descripcion={vacio ? "Esta acción no se puede deshacer." : null}
        onConfirmar={() => void eliminar()}>
        {!vacio && (
          <Aviso><span className="flex items-center gap-3"><AlertTriangle className="size-5 shrink-0" />El grupo tiene {g.reportes} {g.reportes === 1 ? "reporte" : "reportes"}: elimínalos primero.</span></Aviso>
        )}
      </Confirmar>
    </>
  );
}
