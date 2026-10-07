// Funciones puras de presentación (sin estado ni red).
import type { EstadoEjecucion, EstadoTabla, Frecuencia, Grupo } from "./tipos";

export type Tono = "exito" | "aviso" | "peligro" | "info" | "neutro";

export const GRUPOS: Record<Grupo, string> = {
  diarias: "Diarias",
  piero: "Mensuales · Piero",
  erick: "Mensuales · Erick",
};

export const ESTADO_EJECUCION: Record<EstadoEjecucion, { texto: string; tono: Tono }> = {
  en_cola: { texto: "En cola", tono: "neutro" },
  ejecutando: { texto: "Ejecutando", tono: "info" },
  ok: { texto: "Correcto", tono: "exito" },
  error: { texto: "Error", tono: "peligro" },
  configuracion: { texto: "Configuración", tono: "aviso" },
  tablas_desactualizadas: { texto: "Tablas desactualizadas", tono: "aviso" },
};

export const ESTADO_TABLA: Record<EstadoTabla, Tono> = {
  OK: "exito",
  DESACTUALIZADA: "aviso",
  "NO EXISTE": "peligro",
  ERROR: "peligro",
  "SIN CONTROL": "neutro",
};

export const enCurso = (e: EstadoEjecucion) => e === "en_cola" || e === "ejecutando";

/** "2026-09-30" → "30/09/2026"; con hora si viene ISO completo. */
export function fecha(iso: string | null | undefined): string {
  if (!iso) return "—";
  const [d, h] = iso.split("T");
  const [y, m, dd] = d.split("-");
  return `${dd}/${m}/${y}${h ? ` ${h.slice(0, 5)}` : ""}`;
}

export function tamano(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
}

export function duracion(inicio: string, fin: string | null): string {
  if (!fin) return "—";
  const s = Math.round((Date.parse(fin) - Date.parse(inicio)) / 1000);
  return s < 60 ? `${s} s` : `${Math.floor(s / 60)} min ${s % 60} s`;
}

/** Misma regla que el servidor; solo sirve para avisar antes de enviar (el servidor decide). */
export function errorDeCorte(frecuencia: Frecuencia, iso: string): string | null {
  if (!iso) return frecuencia === "mensual" ? "Indica la fecha de corte (fin de mes)." : null;
  const [y, m, d] = iso.split("-").map(Number);
  if (new Date(y, m - 1, d) > new Date()) return "La fecha de corte no puede estar en el futuro.";
  if (frecuencia === "mensual" && d !== new Date(y, m, 0).getDate()) return "Un reporte mensual exige fin de mes.";
  return null;
}
