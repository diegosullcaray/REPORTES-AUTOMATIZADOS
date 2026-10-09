"use client";

import { Save, SlidersHorizontal, Undo2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { FilaAjuste, SeccionAjustes } from "@/components/ajustes";
import { Aviso, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { ConfiguracionGeneral, PedidoConfiguracion } from "@/lib/tipos";

type Campo = keyof PedidoConfiguracion;
type Valores = Record<Campo, string>;

/** Un corte solo se muestra como valor si está escrito en el .env; si es el de por defecto, el campo queda vacío y la ayuda dice de dónde sale. */
const valoresDe = (c: ConfiguracionGeneral): Valores => ({
  corte_mensual: c.corte_mensual.origen.startsWith(".env") ? (c.corte_mensual.fecha ?? "") : "",
  corte_diario: c.corte_diario.origen.startsWith(".env") ? (c.corte_diario.fecha ?? "") : "",
  dir_inputs: c.dir_inputs, dir_outputs: c.dir_outputs, driver_odbc: c.driver_odbc,
});

function Formulario({ c, onGuardado }: { c: ConfiguracionGeneral; onGuardado: (c: ConfiguracionGeneral) => void }) {
  const [base, setBase] = useState(() => valoresDe(c));
  const [borrador, setBorrador] = useState(base);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cambios = (Object.keys(base) as Campo[]).filter((k) => borrador[k] !== base[k]);

  const campo = (k: Campo, props: { type?: string; ayuda?: string; className?: string } = {}) => (
    <div className="flex w-full flex-col gap-1">
      <Input id={k} type={props.type} value={borrador[k]} onChange={(ev) => setBorrador((b) => ({ ...b, [k]: ev.target.value }))}
        className={props.className} aria-invalid={error?.includes(k.toUpperCase()) || undefined} />
      {props.ayuda && <span className="text-xs text-muted-foreground">{props.ayuda}</span>}
    </div>
  );

  async function guardar() {
    setGuardando(true);
    setError(null);
    try {
      const nueva = await api.guardarConfiguracion(Object.fromEntries(cambios.map((k) => [k, borrador[k]])));
      const valores = valoresDe(nueva);
      // Lo pendiente de reinicio sigue mostrando lo guardado, no lo que la API tiene en memoria.
      const guardado = { ...valores, ...Object.fromEntries(cambios.filter((k) => !k.startsWith("corte_")).map((k) => [k, borrador[k]])) } as Valores;
      setBase(guardado);
      setBorrador(guardado);
      onGuardado(nueva);
      toast.success("Configuración guardada en el .env", { description: (nueva.pendientes_reinicio ?? []).length ? "Reinicia la API para aplicar las carpetas o el driver." : "Rige desde la próxima ejecución." });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={(ev) => { ev.preventDefault(); if (cambios.length) void guardar(); }} className="flex flex-col gap-6">
      <SeccionAjustes titulo="Fechas de corte" descripcion="Se usan cuando un reporte se ejecuta sin --fecha-corte. Rigen desde la próxima ejecución; vacío = el valor por defecto.">
        <FilaAjuste etiqueta="Corte mensual (fin de mes)">{campo("corte_mensual", { type: "date", className: "w-48", ayuda: c.corte_mensual.origen })}</FilaAjuste>
        <FilaAjuste etiqueta="Corte diario">{campo("corte_diario", { type: "date", className: "w-48", ayuda: c.corte_diario.origen })}</FilaAjuste>
      </SeccionAjustes>
      <SeccionAjustes titulo="Carpetas y conexión" descripcion="Se guardan en el .env y la API las aplica al reiniciar. Usa rutas completas.">
        <FilaAjuste etiqueta="Carpeta de entradas">{campo("dir_inputs", { className: "font-mono" })}</FilaAjuste>
        <FilaAjuste etiqueta="Carpeta de salidas">{campo("dir_outputs", { className: "font-mono" })}</FilaAjuste>
        <FilaAjuste etiqueta="Driver ODBC">{campo("driver_odbc", { className: "font-mono" })}</FilaAjuste>
      </SeccionAjustes>

      {(c.pendientes_reinicio ?? []).length > 0 && <Aviso>Guardado en el .env, pendiente de reiniciar la API: {c.pendientes_reinicio.join(", ")}.</Aviso>}
      {error && <ErrorEnLinea titulo="No se guardó" detalle={error} />}

      <div className="flex flex-wrap justify-end gap-2">
        <Button type="button" variant="outline" disabled={!cambios.length || guardando} onClick={() => { setBorrador(base); setError(null); }}><Undo2 /> Descartar</Button>
        <Button type="submit" disabled={!cambios.length || guardando}><Save /> {guardando ? "Guardando…" : `Guardar${cambios.length ? ` (${cambios.length})` : ""}`}</Button>
      </div>
    </form>
  );
}

/** Configuración general: ajustes del motor, guardados en el .env de la API (las contraseñas no se muestran). */
export function PanelConfiguracion() {
  const { datos: c, error, cargando, recargar } = useConsulta("configuracion", api.configuracion);
  return (
    <Pagina>
      <Marco icono={<SlidersHorizontal />} titulo="Configuración" descripcion="Fechas de corte, carpetas y driver. Se guardan en el .env de la API; el resto del .env no se toca.">
        {error ? <ErrorEnLinea titulo="No se pudo leer la configuración" detalle={error} onReintentar={recargar} />
          : cargando && !c ? <EsqueletoFilas filas={5} />
          : c && <Formulario c={c} onGuardado={recargar} />}
      </Marco>
    </Pagina>
  );
}
