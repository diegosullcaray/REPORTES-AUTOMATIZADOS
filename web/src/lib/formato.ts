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

/** Categoría del sidebar y de las migas: Diarios / Mensuales. */
export const CATEGORIA: Record<Frecuencia, string> = { diaria: "Diarios", mensual: "Mensuales" };
export const TIPO: Record<Frecuencia, string> = { diaria: "Diario", mensual: "Mensual" };

/** "diego.sullcaray" → "DS", "24681" → "24" (avatar del menú de usuario). */
export function iniciales(usuario: string): string {
  const partes = usuario.split(/[.\s_-]+/).filter(Boolean);
  if (partes.length >= 2) return (partes[0][0] + partes[1][0]).toUpperCase();
  return (partes[0] ?? "?").slice(0, 2).toUpperCase();
}

/** "cartera-sin-asignar" → "Cartera sin asignar". */
export const titulo = (nombre: string) => nombre.charAt(0).toUpperCase() + nombre.slice(1).replaceAll("-", " ");

export type Entrada<T> = { tipo: "reporte"; r: T } | { tipo: "nodo"; orden: string; titulo: string; reportes: T[] };

/**
 * Sub-reportes de una misma carpeta del legado (09.1, 09.2…) bajo un nodo con el nombre de esa carpeta;
 * los reportes solos quedan sueltos. Conserva el orden de entrada.
 */
export function agruparPorCarpeta<T extends { carpeta: string }>(reportes: T[]): Entrada<T>[] {
  const porCarpeta = Map.groupBy(reportes, (r) => r.carpeta);
  const vistos = new Set<string>();
  return reportes.flatMap((r): Entrada<T>[] => {
    const grupo = porCarpeta.get(r.carpeta)!;
    if (grupo.length === 1) return [{ tipo: "reporte", r }];
    if (vistos.has(r.carpeta)) return [];
    vistos.add(r.carpeta);
    const [orden, ...palabras] = r.carpeta.split("/").pop()!.split("_"); // "09_reporte_mensual_michael_palacios"
    return [{ tipo: "nodo", orden, titulo: titulo(palabras.join("-")), reportes: grupo }];
  });
}

export type TipoLinea = "ok" | "error" | "aviso" | "paso" | "normal";

/** Color de cada línea del log según los prefijos que imprime el ejecutor (✓ ✗ AVISO ▶). */
export function tipoLinea(linea: string): TipoLinea {
  const l = linea.trimStart();
  if (l.startsWith("✓")) return "ok";
  if (l.startsWith("✗") || l.startsWith("ERROR") || l.startsWith("NO EXISTE")) return "error";
  if (l.startsWith("AVISO") || l.startsWith("DESACTUALIZADA")) return "aviso";
  if (l.startsWith("▶") || l.startsWith("Fecha de corte")) return "paso";
  return "normal";
}

export const enCurso = (e: EstadoEjecucion) => e === "en_cola" || e === "ejecutando";

const relativo = new Intl.RelativeTimeFormat("es", { numeric: "auto" });
const UNIDADES: [Intl.RelativeTimeFormatUnit, number][] = [["day", 86400], ["hour", 3600], ["minute", 60], ["second", 1]];

/** "hace 5 minutos", "ayer"… (`ahora` inyectable para pruebas). */
export function haceTiempo(iso: string, ahora = Date.now()): string {
  const s = Math.round((Date.parse(iso) - ahora) / 1000);
  const [unidad, tam] = UNIDADES.find(([, t]) => Math.abs(s) >= t) ?? UNIDADES[3];
  return relativo.format(Math.round(s / tam), unidad);
}

/** Corte con que se lanzó una ejecución, leído de sus argumentos (--fecha-corte AAAA-MM-DD o --mes AAAA-MM). */
export function corteDe(argumentos: string[]): string | null {
  const i = argumentos.findIndex((a) => a === "--fecha-corte" || a === "--mes");
  return i >= 0 ? argumentos[i + 1] ?? null : null;
}

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
