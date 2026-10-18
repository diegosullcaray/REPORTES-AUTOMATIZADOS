"use client";

import { Plus } from "lucide-react";
import { useState, type FormEvent } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { titulo } from "@/lib/formato";
import type { ReporteResumen } from "@/lib/tipos";

/** Botón + diálogo (como «Create Project» de Dokploy): una sección nueva con los reportes que agrupa. */
export function NuevaSeccion({ reportes, onCreada }: { reportes: ReporteResumen[]; onCreada: () => void }) {
  const [abierto, setAbierto] = useState(false);
  const [elegidos, setElegidos] = useState<string[]>([]);
  const [ocupado, setOcupado] = useState(false);

  async function crear(ev: FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    const datos = new FormData(ev.currentTarget);
    setOcupado(true);
    try {
      await api.crearSeccion({ nombre: String(datos.get("nombre")), descripcion: String(datos.get("descripcion")), reportes: elegidos });
      toast.success("Sección creada");
      setAbierto(false);
      setElegidos([]);
      onCreada();
    } catch (e) {
      toast.error("No se pudo crear", { description: (e as Error).message });
    } finally {
      setOcupado(false);
    }
  }

  return (
    <Dialog open={abierto} onOpenChange={setAbierto}>
      <DialogTrigger render={<Button size="sm" />}><Plus /> Nueva sección</DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Nueva sección</DialogTitle>
          <DialogDescription>Agrupa tarjetas de reportes; no cambia los reportes.</DialogDescription>
        </DialogHeader>
        <form onSubmit={crear} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="seccion-nombre">Nombre</Label>
            <Input id="seccion-nombre" name="nombre" required maxLength={80} autoComplete="off" />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="seccion-descripcion">Descripción</Label>
            <Input id="seccion-descripcion" name="descripcion" maxLength={200} autoComplete="off" />
          </div>
          <fieldset className="flex max-h-56 flex-col gap-2 overflow-y-auto rounded-lg border p-3">
            <legend className="px-1 text-sm font-medium">Reportes ({elegidos.length})</legend>
            {reportes.map((r) => (
              <label key={r.nombre} className="flex cursor-pointer items-center gap-3 text-sm">
                <Checkbox checked={elegidos.includes(r.nombre)} onCheckedChange={(v) => setElegidos(v === true ? [...elegidos, r.nombre] : elegidos.filter((x) => x !== r.nombre))} />
                <span className="truncate">{r.orden} · {titulo(r.nombre)}</span>
              </label>
            ))}
          </fieldset>
          <DialogFooter>
            <Button type="submit" disabled={ocupado}>{ocupado ? "Creando…" : "Crear"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
