"use client";

import { useSyncExternalStore } from "react";
import { fecha, haceTiempo } from "@/lib/formato";

// Un solo reloj de 30 s para todos los «hace…» de la pantalla.
let ahora = Date.now();
const oyentes = new Set<() => void>();
let reloj: ReturnType<typeof setInterval> | undefined;
function suscribir(aviso: () => void) {
  oyentes.add(aviso);
  reloj ??= setInterval(() => { ahora = Date.now(); oyentes.forEach((o) => o()); }, 30_000);
  return () => {
    oyentes.delete(aviso);
    if (!oyentes.size) { clearInterval(reloj); reloj = undefined; }
  };
}

const reloj24 = new Intl.DateTimeFormat("es-PE", { weekday: "short", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "America/Lima" });

/** Hora de Lima en el encabezado (como el TimeBadge de Dokploy). */
export function Hora() {
  const t = useSyncExternalStore(suscribir, () => ahora, () => 0);
  if (!t) return null;
  return <span className="hidden rounded-md border px-2 py-1 text-xs text-muted-foreground tabular-nums sm:inline">{reloj24.format(t)}</span>;
}

/** «hace 5 minutos», con la fecha exacta al pasar el mouse; se actualiza solo. */
export function Hace({ iso }: { iso: string }) {
  const t = useSyncExternalStore(suscribir, () => ahora, () => 0);
  return <time dateTime={iso} title={fecha(iso)} className="whitespace-nowrap">{t ? haceTiempo(iso, t) : fecha(iso)}</time>;
}
