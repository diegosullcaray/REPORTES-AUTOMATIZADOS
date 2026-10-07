// Métricas del inicio, puras (sin red ni estado) para poder probarlas.
import { corteDe, type Tono } from "../../lib/formato.ts";
import type { Ejecucion, ReporteResumen } from "../../lib/tipos";

const SEMANA = 7 * 24 * 3600 * 1000;

/** Ejecuciones de los últimos 7 días frente a los 7 anteriores. */
export function resumenSemanal(ejecuciones: Ejecucion[], ahora = Date.now()) {
  const ultima = ejecuciones.filter((x) => ahora - Date.parse(x.inicio) < SEMANA);
  const previa = ejecuciones.filter((x) => { const d = ahora - Date.parse(x.inicio); return d >= SEMANA && d < 2 * SEMANA; }).length;
  const cuenta = (f: (x: Ejecucion) => boolean) => ultima.filter(f).length;
  const correctas = cuenta((x) => x.estado === "ok");
  const total = ultima.length;
  const variacion = previa ? `${total >= previa ? "+" : ""}${Math.round(((total - previa) / previa) * 100)}% vs 7 días previos`
    : total ? "sin datos previos" : "sin actividad aún";
  const estados: { texto: string; tono: Tono; cantidad: number }[] = [
    { texto: "correctas", tono: "exito", cantidad: correctas },
    { texto: "con error", tono: "peligro", cantidad: cuenta((x) => x.estado === "error") },
    { texto: "tablas o configuración", tono: "aviso", cantidad: cuenta((x) => x.estado === "tablas_desactualizadas" || x.estado === "configuracion") },
    { texto: "en curso", tono: "info", cantidad: cuenta((x) => x.estado === "en_cola" || x.estado === "ejecutando") },
  ];
  return { total, correctas, exito: total ? Math.round((correctas / total) * 100) : 0, variacion, estados };
}

/** Reportes mensuales sin una ejecución correcta para el corte (AAAA-MM-DD); los que reciben --mes cuentan por mes. */
export function pendientesDelCierre(reportes: ReporteResumen[], ejecuciones: Ejecucion[], corte: string) {
  const mensuales = reportes.filter((r) => r.frecuencia === "mensual");
  const hechos = new Set(ejecuciones
    .filter((x) => x.estado === "ok" && [corte, corte.slice(0, 7)].includes(corteDe(x.argumentos) ?? ""))
    .map((x) => x.reporte));
  const pendientes = mensuales.filter((r) => !hechos.has(r.nombre));
  return { total: mensuales.length, listos: mensuales.length - pendientes.length, pendientes };
}
