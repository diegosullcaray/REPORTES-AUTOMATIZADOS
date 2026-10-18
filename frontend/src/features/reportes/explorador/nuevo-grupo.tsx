"use client";

import { FolderPlus } from "lucide-react";
import { useState, type FormEvent } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SelectorEtiquetas } from "@/features/etiquetas/etiquetas";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";

/** Botón + diálogo del tablero de reportes: un grupo nuevo con sus etiquetas. */
export function NuevoGrupo() {
  const [abierto, setAbierto] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [elegidas, setElegidas] = useState<string[]>([]);
  const etiquetas = useConsulta(abierto ? "etiquetas" : null, api.etiquetas);

  async function crear(ev: FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    const d = new FormData(ev.currentTarget);
    setOcupado(true);
    try {
      const g = await api.crearGrupo({ nombre: String(d.get("nombre")), etiquetas: elegidas });
      toast.success("Grupo creado", { description: "Entra al grupo para crear sus reportes." });
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- recarga completa a propósito: el sidebar vuelve a leer los grupos
      window.location.href = `/reportes?grupo=${g.id}`;
    } catch (e) {
      toast.error("No se pudo crear", { description: (e as Error).message });
      setOcupado(false);
    }
  }

  return (
    <Dialog open={abierto} onOpenChange={setAbierto}>
      <DialogTrigger render={<Button size="sm" />}><FolderPlus /> Nuevo grupo</DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Nuevo grupo</DialogTitle>
          <DialogDescription>Agrupa reportes de una misma persona o área. La frecuencia (diaria o mensual) se elige en cada reporte.</DialogDescription>
        </DialogHeader>
        <form onSubmit={crear} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="ng-nombre">Nombre</Label>
            <Input id="ng-nombre" name="nombre" required maxLength={60} autoComplete="off" placeholder="Cierre de riesgos" />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label>Etiquetas</Label>
            <SelectorEtiquetas etiquetas={etiquetas.datos ?? []} elegidas={elegidas} onCambio={setElegidas} onCreada={etiquetas.recargar} />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={ocupado}>{ocupado ? "Creando…" : "Crear grupo"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
