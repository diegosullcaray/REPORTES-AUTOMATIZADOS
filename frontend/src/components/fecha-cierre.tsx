"use client";

import { CalendarDays, RotateCcw } from "lucide-react";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { errorDeCorte, fecha } from "@/lib/formato";
import type { Frecuencia } from "@/lib/tipos";

/** Fechas elegidas en la cabecera; null = la del .env. Rigen para todos los reportes y la validación de tablas. */
type Elegidas = Record<Frecuencia, string | null>;
const CLAVE = "reportes.fecha-cierre";
const VACIAS: Elegidas = { mensual: null, diaria: null };

const Contexto = createContext<{ elegidas: Elegidas; elegir: (f: Frecuencia, v: string | null) => void }>({ elegidas: VACIAS, elegir: () => undefined });

export function ProveedorCierre({ children }: { children: ReactNode }) {
  const [elegidas, setElegidas] = useState<Elegidas>(VACIAS);
  // Se recuerda en la pestaña del navegador (sessionStorage); si no está disponible, solo vive en memoria.
  useEffect(() => {
    try {
      const guardado = JSON.parse(sessionStorage.getItem(CLAVE) ?? "null") as Elegidas | null;
      if (guardado) setElegidas({ ...VACIAS, ...guardado }); // eslint-disable-line react-hooks/set-state-in-effect -- lectura única al montar
    } catch { /* sin almacenamiento */ }
  }, []);
  const elegir = (f: Frecuencia, v: string | null) => setElegidas((e) => {
    const n = { ...e, [f]: v };
    try { sessionStorage.setItem(CLAVE, JSON.stringify(n)); } catch { /* sin almacenamiento */ }
    return n;
  });
  return <Contexto.Provider value={{ elegidas, elegir }}>{children}</Contexto.Provider>;
}

/** Corte vigente para una frecuencia: el elegido en la cabecera o, si no hay, el por defecto (`defecto`). */
export function useCorte(frecuencia: Frecuencia, defecto: string | null | undefined) {
  const { elegidas } = useContext(Contexto);
  return elegidas[frecuencia] ?? defecto ?? "";
}

function Campo({ id, etiqueta, frecuencia, defecto, origen }: { id: string; etiqueta: string; frecuencia: Frecuencia; defecto: string; origen: string }) {
  const { elegidas, elegir } = useContext(Contexto);
  const valor = elegidas[frecuencia] ?? defecto;
  const error = errorDeCorte(frecuencia, valor);
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{etiqueta}</Label>
      <div className="flex gap-2">
        <Input id={id} type="date" value={valor} onChange={(ev) => elegir(frecuencia, ev.target.value || null)} aria-invalid={!!error} />
        <Button type="button" variant="ghost" size="icon" aria-label={`Volver al valor por defecto (${etiqueta})`} disabled={elegidas[frecuencia] === null}
          onClick={() => elegir(frecuencia, null)}><RotateCcw /></Button>
      </div>
      <span className={`text-xs ${error ? "text-[var(--mis-danger)]" : "text-muted-foreground"}`}>{error ?? (elegidas[frecuencia] ? "Elegida a mano" : origen)}</span>
    </div>
  );
}

/** Botón de la cabecera: calendario con tooltip «Fecha de cierre» que despliega los filtros de fecha. */
export function FiltroCierre() {
  const { elegidas } = useContext(Contexto);
  const { datos: c } = useConsulta("configuracion", api.configuracion);
  const mensual = elegidas.mensual ?? c?.corte_mensual.fecha ?? "";
  const aMano = elegidas.mensual !== null || elegidas.diaria !== null;
  return (
    <Popover>
      <Tooltip>
        <TooltipTrigger render={<PopoverTrigger render={<Button variant="outline" size="sm" className="gap-1.5" aria-label="Fecha de cierre" />} />}>
          <CalendarDays />
          <span className="hidden tabular-nums sm:inline">{mensual ? fecha(mensual) : "Cierre"}</span>
          {aMano && <span className="size-1.5 rounded-full bg-[var(--mis-warning)]" aria-hidden />}
        </TooltipTrigger>
        <TooltipContent side="bottom">Fecha de cierre</TooltipContent>
      </Tooltip>
      <PopoverContent className="flex flex-col gap-4">
        <div className="flex flex-col gap-0.5">
          <span className="text-sm font-semibold">Filtros</span>
          <span className="text-xs text-muted-foreground">Rigen para todos los reportes y la validación de tablas.</span>
        </div>
        <Campo id="cierre-mensual" etiqueta="Fecha de cierre (mensuales)" frecuencia="mensual" defecto={c?.corte_mensual.fecha ?? ""} origen={c?.corte_mensual.origen ?? ""} />
        <Campo id="cierre-diario" etiqueta="Corte diario" frecuencia="diaria" defecto={c?.corte_diario.fecha ?? ""} origen={c?.corte_diario.origen ?? ""} />
      </PopoverContent>
    </Popover>
  );
}
