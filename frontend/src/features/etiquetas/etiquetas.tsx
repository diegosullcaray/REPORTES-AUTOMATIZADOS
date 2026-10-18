"use client";

import { Check, ChevronsUpDown, PenBox, Plus, Tag } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Etiqueta } from "@/lib/tipos";

const HEX = /^#[0-9a-f]{6}$/i;

/** Color de partida: el de la marca (token `--mis-primary`, siempre #rrggbb); así no hay colores crudos en el código. */
function colorDeMarca(): string {
  const v = typeof document === "undefined" ? "" : getComputedStyle(document.documentElement).getPropertyValue("--mis-primary").trim();
  return HEX.test(v) ? v : "";
}

/** Etiqueta con el color que eligió la persona (como el `TagBadge` de Dokploy): fondo y borde translúcidos del mismo color. */
export function EtiquetaBadge({ e, className, children }: { e: Pick<Etiqueta, "nombre" | "color">; className?: string; children?: React.ReactNode }) {
  return (
    <Badge variant="outline" className={cn("border", className)} style={{ backgroundColor: `${e.color}33`, color: e.color, borderColor: `${e.color}66` }}>
      {e.nombre}
      {children}
    </Badge>
  );
}

/** Alta o edición de una etiqueta en un diálogo (como `HandleTag` de Dokploy), con selector de color RGB y campo #rrggbb. */
export function DialogoEtiqueta({ etiqueta, onCerrar, onGuardada }: { etiqueta?: Etiqueta; onCerrar: () => void; onGuardada: (e: Etiqueta) => void }) {
  const [nombre, setNombre] = useState(etiqueta?.nombre ?? "");
  const [color, setColor] = useState(etiqueta?.color ?? colorDeMarca);
  const [ocupado, setOcupado] = useState(false);
  const valido = HEX.test(color);

  async function guardar() {
    setOcupado(true);
    try {
      const e = await (etiqueta ? api.actualizarEtiqueta(etiqueta.id, { nombre, color }) : api.crearEtiqueta({ nombre, color }));
      toast.success(etiqueta ? "Etiqueta actualizada" : "Etiqueta creada");
      onGuardada(e);
      onCerrar();
    } catch (e) {
      toast.error("No se guardó", { description: (e as Error).message });
    } finally {
      setOcupado(false);
    }
  }

  return (
    <Dialog open onOpenChange={(a) => !a && onCerrar()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{etiqueta ? "Editar etiqueta" : "Nueva etiqueta"}</DialogTitle>
          <DialogDescription>Una etiqueta ayuda a organizar los grupos de reportes.</DialogDescription>
        </DialogHeader>
        {/* stopPropagation: el diálogo vive dentro del formulario de «Nuevo grupo» en el árbol de React y su submit no debe llegar allí */}
        <form id="form-etiqueta" onSubmit={(ev) => { ev.preventDefault(); ev.stopPropagation(); void guardar(); }}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="et-nombre">Nombre</FieldLabel>
              <Input id="et-nombre" value={nombre} onChange={(ev) => setNombre(ev.target.value)} required maxLength={50} autoComplete="off" autoFocus placeholder="Riesgos" />
            </Field>
            <Field>
              <FieldLabel htmlFor="et-color">Color</FieldLabel>
              <div className="flex gap-2">
                <Input id="et-color" type="color" value={valido ? color : colorDeMarca()} onChange={(ev) => setColor(ev.target.value)} aria-label="Elegir color" className="h-9 w-14 cursor-pointer p-1" />
                <Input value={color} onChange={(ev) => setColor(ev.target.value)} aria-label="Color en formato #rrggbb" placeholder="#rrggbb" maxLength={7} className="font-mono" autoComplete="off" aria-invalid={!valido} />
              </div>
              <FieldDescription>Elige con el selector o escribe el valor #rrggbb.</FieldDescription>
            </Field>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">Vista previa: {valido && <EtiquetaBadge e={{ nombre: nombre.trim() || "Etiqueta", color }} />}</div>
          </FieldGroup>
        </form>
        <DialogFooter>
          <Button type="submit" form="form-etiqueta" disabled={ocupado || !nombre.trim() || !valido}>{ocupado ? "Guardando…" : "Guardar"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/** Botón que abre el diálogo (crear o editar). */
export function BotonEtiqueta({ etiqueta, onGuardada }: { etiqueta?: Etiqueta; onGuardada: (e: Etiqueta) => void }) {
  const [abierto, setAbierto] = useState(false);
  return (
    <>
      {etiqueta
        ? <Button variant="ghost" size="icon" aria-label={`Editar ${etiqueta.nombre}`} onClick={() => setAbierto(true)}><PenBox className="size-4" /></Button>
        : <Button type="button" variant="outline" size="sm" onClick={() => setAbierto(true)}><Plus /> Crear etiqueta</Button>}
      {abierto && <DialogoEtiqueta etiqueta={etiqueta} onCerrar={() => setAbierto(false)} onGuardada={onGuardada} />}
    </>
  );
}

/** Selección múltiple de etiquetas (como el `TagSelector` de Dokploy): `Command` con búsqueda en un popover y «Crear etiqueta» al pie. */
export function SelectorEtiquetas({ etiquetas, elegidas, onCambio, onCreada }: { etiquetas: Etiqueta[]; elegidas: string[]; onCambio: (ids: string[]) => void; onCreada: () => void }) {
  const alternar = (id: string) => onCambio(elegidas.includes(id) ? elegidas.filter((x) => x !== id) : [...elegidas, id]);
  const marcadas = etiquetas.filter((e) => elegidas.includes(e.id));
  return (
    <Popover>
      <PopoverTrigger render={<Button type="button" variant="outline" className="h-auto min-h-9 w-full justify-between" />}>
        <span className="flex flex-1 flex-wrap gap-1 text-left">
          {marcadas.length ? marcadas.map((e) => <EtiquetaBadge key={e.id} e={e} />) : <span className="font-normal text-muted-foreground">Elegir etiquetas…</span>}
        </span>
        <ChevronsUpDown className="size-4 shrink-0 opacity-50" />
      </PopoverTrigger>
      <PopoverContent align="start" className="w-72 p-0">
        <Command>
          <CommandInput placeholder="Buscar etiquetas…" />
          <CommandList>
            <CommandEmpty>
              <span className="flex items-center justify-center gap-2 py-1 text-sm text-muted-foreground"><Tag className="size-4" />{etiquetas.length === 0 ? "Aún no hay etiquetas." : "Sin resultados."}</span>
            </CommandEmpty>
            <CommandGroup>
              {etiquetas.map((e) => (
                <CommandItem key={e.id} value={e.nombre} onSelect={() => alternar(e.id)} className="cursor-pointer">
                  <Checkbox checked={elegidas.includes(e.id)} tabIndex={-1} />
                  <EtiquetaBadge e={e} />
                  <Check className={cn("ml-auto size-4", elegidas.includes(e.id) ? "opacity-100" : "opacity-0")} />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
        <div className="flex justify-center border-t p-2"><BotonEtiqueta onGuardada={(e) => { onCreada(); onCambio([...elegidas, e.id]); }} /></div>
      </PopoverContent>
    </Popover>
  );
}
