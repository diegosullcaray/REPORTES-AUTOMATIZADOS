"use client";

import { CalendarDays } from "lucide-react";
import { es } from "react-day-picker/locale";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { fecha } from "@/lib/formato";

/** "2026-06-30" → Date local (sin el desfase de zona horaria de `new Date(iso)`). */
const aFecha = (iso: string) => { const [y, m, d] = iso.split("-").map(Number); return new Date(y, m - 1, d); };
const aIso = (f: Date) => `${f.getFullYear()}-${String(f.getMonth() + 1).padStart(2, "0")}-${String(f.getDate()).padStart(2, "0")}`;

/** Selector de fecha de shadcn (Popover + Calendar). `soloFinDeMes` deshabilita los demás días; nunca deja elegir el futuro. El valor es AAAA-MM-DD. */
export function SelectorFecha({ id, valor, onCambio, soloFinDeMes, invalido }: { id?: string; valor: string; onCambio: (iso: string) => void; soloFinDeMes?: boolean; invalido?: boolean }) {
  const elegida = valor ? aFecha(valor) : undefined;
  const hoy = new Date();
  return (
    <Popover>
      <PopoverTrigger render={<Button id={id} type="button" variant="outline" aria-invalid={invalido} className="w-full justify-start font-normal tabular-nums" />}>
        <CalendarDays /> {valor ? fecha(valor) : "Elegir fecha"}
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar mode="single" locale={es} selected={elegida} defaultMonth={elegida} onSelect={(f) => f && onCambio(aIso(f))}
          captionLayout="dropdown" startMonth={new Date(2020, 0)} endMonth={hoy}
          disabled={[{ after: hoy }, ...(soloFinDeMes ? [(f: Date) => f.getDate() !== new Date(f.getFullYear(), f.getMonth() + 1, 0).getDate()] : [])]} />
      </PopoverContent>
    </Popover>
  );
}
