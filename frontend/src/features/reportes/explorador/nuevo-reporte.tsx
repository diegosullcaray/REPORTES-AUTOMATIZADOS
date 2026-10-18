"use client";

import { FilePlus2 } from "lucide-react";
import { useState, type FormEvent } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Field, FieldLabel } from "@/components/ui/field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import type { Frecuencia, Grupo } from "@/lib/tipos";

const FRECUENCIAS: Record<Frecuencia, string> = { mensual: "Mensual (fin de mes)", diaria: "Diaria (día anterior)" };

/** Botón + diálogo dentro de un grupo: crea el módulo del reporte (T-SQL con tokens de fecha), su test y su registro; luego abre su pestaña Script. */
export function NuevoReporte({ grupo, nombreGrupo, frecuenciaLibre }: { grupo: Grupo; nombreGrupo: string; frecuenciaLibre: boolean }) {
  const [abierto, setAbierto] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [frecuencia, setFrecuencia] = useState<Frecuencia>("mensual");

  async function crear(ev: FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    const d = new FormData(ev.currentTarget);
    setOcupado(true);
    try {
      const r = await api.crearReporte({
        nombre: String(d.get("nombre")), grupo, orden: String(d.get("orden")),
        base: String(d.get("base")), frecuencia: frecuenciaLibre ? frecuencia : undefined, descripcion: String(d.get("descripcion")), sql: String(d.get("sql")),
      });
      toast.success("Reporte creado", {
        description: r.tablas_nuevas.length ? `Completa la columna de fecha de: ${r.tablas_nuevas.join(", ")}. Luego corre generar_inventario.py.` : "Corre generar_inventario.py antes de commitear.",
      });
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- recarga completa a propósito: el sidebar vuelve a leer el catálogo
      window.location.href = `/reportes/${r.nombre}?tab=script`;
    } catch (e) {
      toast.error("No se pudo crear", { description: (e as Error).message });
      setOcupado(false);
    }
  }

  return (
    <Dialog open={abierto} onOpenChange={setAbierto}>
      <DialogTrigger render={<Button size="sm" variant="outline" />}><FilePlus2 /> Nuevo reporte</DialogTrigger>
      <DialogContent className="max-h-[92vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Nuevo reporte</DialogTitle>
          <DialogDescription>En «{nombreGrupo}». Crea el módulo, su test y su registro. Las fechas van solo con tokens: @@F@@, @@F_ISO@@, @@F_ANT@@…</DialogDescription>
        </DialogHeader>
        <form onSubmit={crear} className="grid gap-4 sm:grid-cols-2">
          <Field>
            <FieldLabel htmlFor="nr-nombre">Nombre (comando)</FieldLabel>
            <Input id="nr-nombre" name="nombre" required maxLength={60} placeholder="cartera-sin-asignar" pattern="[a-z0-9]+(-[a-z0-9]+)*" autoComplete="off" />
          </Field>
          <Field>
            <FieldLabel htmlFor="nr-base">Base de datos</FieldLabel>
            <Input id="nr-base" name="base" required placeholder="storage" autoComplete="off" />
          </Field>
          <Field>
            <FieldLabel htmlFor="nr-orden">Número del legado</FieldLabel>
            <Input id="nr-orden" name="orden" required placeholder="10 o 10.1" pattern="\d{2}(\.\d{1,2})?" autoComplete="off" />
          </Field>
          {frecuenciaLibre && (
            <Field>
              <FieldLabel htmlFor="nr-frecuencia">Frecuencia</FieldLabel>
              <Select value={frecuencia} onValueChange={(v) => setFrecuencia(v as Frecuencia)} items={FRECUENCIAS}>
                <SelectTrigger id="nr-frecuencia" className="w-full"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {Object.entries(FRECUENCIAS).map(([valor, texto]) => <SelectItem key={valor} value={valor}>{texto}</SelectItem>)}
                </SelectContent>
              </Select>
            </Field>
          )}
          <Field className="sm:col-span-2">
            <FieldLabel htmlFor="nr-descripcion">Descripción</FieldLabel>
            <Input id="nr-descripcion" name="descripcion" required maxLength={200} autoComplete="off" />
          </Field>
          <Field className="sm:col-span-2">
            <FieldLabel htmlFor="nr-sql">T-SQL</FieldLabel>
            <Textarea id="nr-sql" name="sql" required spellCheck={false} rows={10} wrap="off" placeholder={"use storage;\ngo\nselect ... where HFECPRO = '@@F@@'"} className="font-mono text-[12px] leading-relaxed" />
          </Field>
          <DialogFooter className="sm:col-span-2">
            <Button type="submit" disabled={ocupado}>{ocupado ? "Creando…" : "Crear reporte"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
