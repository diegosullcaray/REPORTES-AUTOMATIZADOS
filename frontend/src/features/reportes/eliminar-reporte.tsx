"use client";

import { Copy } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Field, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

/** Eliminar un reporte como el servicio de Dokploy (`delete-service.tsx`): hay que escribir su nombre para confirmar. */
export function EliminarReporte({ nombre, abierto, onAbierto }: { nombre: string; abierto: boolean; onAbierto: (a: boolean) => void }) {
  const [texto, setTexto] = useState("");
  const [ocupado, setOcupado] = useState(false);

  async function eliminar() {
    setOcupado(true);
    try {
      await api.eliminarReporte(nombre);
      toast.success("Reporte eliminado");
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- recarga completa a propósito: el sidebar y el conteo del grupo vuelven a leer el catálogo
      window.location.href = "/reportes";
    } catch (e) {
      toast.error("No se pudo eliminar", { description: (e as Error).message });
      setOcupado(false);
    }
  }

  return (
    <Dialog open={abierto} onOpenChange={(a) => { onAbierto(a); if (!a) setTexto(""); }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>¿Estás completamente seguro?</DialogTitle>
          <DialogDescription>
            Esta acción no se puede deshacer. Borra el módulo, el test y el registro del reporte; solo aplica a reportes creados desde la web. Si estás seguro, escribe su nombre.
          </DialogDescription>
        </DialogHeader>
        <form id="eliminar-reporte" onSubmit={(ev) => { ev.preventDefault(); if (texto === nombre) void eliminar(); }} className="grid gap-2">
          <Field>
            <FieldLabel htmlFor="er-nombre" className="flex-wrap">
              Para confirmar, escribe
              <Badge variant="outline" className="cursor-pointer gap-1 p-2" onClick={() => { void navigator.clipboard.writeText(nombre); toast.success("Copiado. ¡Con cuidado!"); }}>
                {nombre}<Copy className="size-4 text-muted-foreground" />
              </Badge>
              en el cuadro:
            </FieldLabel>
            <Input id="er-nombre" value={texto} onChange={(ev) => setTexto(ev.target.value)} placeholder="Nombre del reporte" autoComplete="off" />
          </Field>
        </form>
        <DialogFooter>
          <Button variant="secondary" onClick={() => onAbierto(false)}>Cancelar</Button>
          <Button type="submit" form="eliminar-reporte" variant="destructive" disabled={ocupado || texto !== nombre}>{ocupado ? "Eliminando…" : "Confirmar"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
